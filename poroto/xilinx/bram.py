import string
import os
from pycparser import c_ast
import math

from poroto.common import load_template, mkdir_safe
from poroto.config import gen_path, ipcore_path
from poroto.memory import Memory

class BromMemory(Memory):
    latency = 2
    def __init__(self, designer, debug):
        self.designer = designer
        self.debug = debug
        self.xco_template = load_template('brom.xco')
        self.wrapper_template = load_template('brom_wrapper.vhdl')

    def generateCoe(self, memory):
        out = open(os.path.join(gen_path, ipcore_path, "%s_brom" % memory.name, "%s.coe" % memory.name), 'w' )
        print >> out, "MEMORY_INITIALIZATION_RADIX=10;"
        print >> out, "MEMORY_INITIALIZATION_VECTOR="
        for i in memory.init.exprs:
            if isinstance(i, c_ast.UnaryOp):
                print >> out, "-%s," % i.expr.value
            else:
                print >> out, "%s," % i.value
        out.close()

    def generateXco(self, memory):
        out = open(os.path.join(gen_path, ipcore_path, "%s_brom" % memory.name, "%s_brom.xco" % memory.name), 'w' )
        for line in self.xco_template:
            if '%%%NAME%%%' in line:
                line = string.replace(line, '%%%NAME%%%', memory.name + "_brom")
            elif '%%%COE%%%' in line:
                line = string.replace(line, '%%%COE%%%', memory.name + '.coe')
            elif '%%%SIZE%%%' in line:
                line = string.replace(line, '%%%SIZE%%%', str(memory.size))
            elif '%%%DATA_SIZE%%%' in line:
                line = string.replace(line, '%%%DATA_SIZE%%%', str(memory.data_size))
            print >> out, line,
        out.close()
        self.designer.add_file(ipcore_path, "%s_brom/%s_brom.xco" % (memory.name, memory.name))

    def generateWrapper(self, wrapper):
        out = open(os.path.join(gen_path, 'vhdl', "%s.vhdl" % wrapper.name), 'w' )
        for line in self.wrapper_template:
            if '%%%WRAPPER_NAME%%%' in line:
                line = string.replace(line, '%%%WRAPPER_NAME%%%', wrapper.name)
            elif '%%%BROM_NAME%%%' in line:
                line = string.replace(line, '%%%BROM_NAME%%%', wrapper.name + '_brom')
            elif '%%%ADDR_LEN%%%' in line:
                addr_width = int(math.ceil(math.log(wrapper.size, 2)))
                line = string.replace(line, '%%%ADDR_LEN%%%', str(int(addr_width)))
            elif '%%%DATA_SIZE%%%' in line:
                line = string.replace(line, '%%%DATA_SIZE%%%', str(wrapper.data_size))
            print >> out, line,
        out.close()
        self.designer.add_file(gen_path, "%s.vhdl" % wrapper.name)

    def generate(self, wrapper):
        mkdir_safe(os.path.join(gen_path, ipcore_path, "%s_brom" % wrapper.name))
        self.generateCoe(wrapper)
        self.generateXco(wrapper)
        self.generateWrapper(wrapper)
        return self.latency

class BramMemory(Memory):
    def __init__(self, name, data_type, size, init, debug):
        Memory.__init__(self, name, data_type, size, init, debug)
        self.internal = True
    def get_component(self):
        if self.internal:
            return []
        else:
            return [
                    "COMPONENT %s_bram" %self.name,
                    "PORT (",
                    "clka : IN STD_LOGIC;",
                    "rsta : IN STD_LOGIC;",
                    "ena : IN STD_LOGIC;",
                    "wea : IN STD_LOGIC_VECTOR(0 DOWNTO 0);",
                    "addra : IN STD_LOGIC_VECTOR(%d-1 DOWNTO 0);" % self.address_size,
                    "dina : IN STD_LOGIC_VECTOR(31 DOWNTO 0);",
                    "douta : OUT STD_LOGIC_VECTOR(31 DOWNTO 0);",
                    "clkb : IN STD_LOGIC;",
                    "enb : IN STD_LOGIC;",
                    "web : IN STD_LOGIC_VECTOR(0 DOWNTO 0);",
                    "addrb : IN STD_LOGIC_VECTOR(%d-1 DOWNTO 0);" % self.address_size,
                    "dinb : IN STD_LOGIC_VECTOR(31 DOWNTO 0);",
                    "doutb : OUT STD_LOGIC_VECTOR(31 DOWNTO 0)",
                    ");",
                    "END COMPONENT;",
                    "signal %s_addra : std_logic_vector(%d-1 downto 0);" % (self.name, self.address_size),
                    "signal %s_addrb : std_logic_vector(%d-1 downto 0);" % (self.name, self.address_size),
                ]
    def get_instance(self):
        if self.internal:
            return []
        else:
            return ["%s_i : %s_bram" % (self.name, self.name),
                "port map(",
                "-- Port A",
                "clka   => clk,",
                "rsta   => rst,",
                "ena    => '1',",
                "wea    => (0 => bram_mem_m2s(%d).we)," % self.index,
                "addra  => %s_addra," % (self.name),
                "dina   => bram_mem_m2s(%d).din," % self.index,
                "douta  => bram_mem_s2m(%d).dout," % self.index,

                "-- Port B",
                "clkb   => clk,",
                "--rstb   => rst,",
                "enb    => '1',",
                "web    => (0 => bram_app_m2s(%d).we)," % self.index,
                "addrb  => %s_addrb," % (self.name),
                "dinb   => bram_app_m2s(%d).din," % self.index,
                "doutb  => bram_app_s2m(%d).dout" % self.index,
                ");",
                "%s_addra  <= bram_mem_m2s(%d).addr_w(%d-1 downto 0) when bram_mem_m2s(%d).we = '1' else bram_mem_m2s(%d).addr_r(%d-1 downto 0);" % (self.name, self.index, self.address_size, self.index, self.index, self.address_size),
                "%s_addrb  <= bram_app_m2s(%d).addr_w(%d-1 downto 0) when bram_app_m2s(%d).we = '1' else bram_app_m2s(%d).addr_r(%d-1 downto 0);" % (self.name, self.index, self.address_size, self.index, self.index, self.address_size),
                ]

    def generateXco(self):
        out = open(os.path.join(gen_path, ipcore_path, "%s_bram" % self.name, "%s_bram.xco" % self.name), 'w' )
        for line in self.xco_template:
            if '%%%NAME%%%' in line:
                line = string.replace(line, '%%%NAME%%%', self.name + "_bram")
            elif '%%%SIZE%%%' in line:
                if self.internal:
                    line = string.replace(line, '%%%SIZE%%%', str(int(math.ceil(self.size/4.0)))) #TODO: Assume 32 bits item in 128 bits mem
                else:
                    line = string.replace(line, '%%%SIZE%%%', str(self.size))
            print >> out, line,
        out.close()

    def generate(self, designer):
        if self.internal:
            self.xco_template = load_template('bram.xco')
        else:
            self.xco_template = load_template('bram_32.xco')
        mkdir_safe(os.path.join(gen_path, ipcore_path, "%s_bram" % self.name))
        self.generateXco()
        designer.add_file(ipcore_path, "%s_bram/%s_bram.xco" % (self.name, self.name))
