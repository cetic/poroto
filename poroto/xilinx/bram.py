import string
import os
from pycparser import c_ast
import math

from poroto.common import mkdir_safe
from poroto.config import gen_path, ipcore_path
from poroto.memory import Memory
from poroto.template import FileTemplate

class BromMemory(Memory):
    latency = 2
    def __init__(self, name, data_type, size, init, debug):
        Memory.__init__(self, name, data_type, size, init, debug)
        self.xco_template = FileTemplate('brom.xco')

    def generateCoe(self):
        out = open(os.path.join(gen_path, ipcore_path, "%s_brom" % self.name, "%s.coe" % self.name), 'w' )
        print >> out, "MEMORY_INITIALIZATION_RADIX=10;"
        print >> out, "MEMORY_INITIALIZATION_VECTOR="
        for i in self.init.exprs:
            if isinstance(i, c_ast.UnaryOp):
                print >> out, "-%s," % i.expr.value
            else:
                print >> out, "%s," % i.value
        out.close()

    def generateXco(self, designer):
        keys={ 'NAME': self.name + "_brom",
               'COE': self.name + '.coe',
               'SIZE': self.size,
               'DATA_SIZE': self.data_size,
              }
        self.xco_template.set_keys(keys)
        self.xco_template.generate(os.path.join(gen_path, ipcore_path, "%s_brom" % self.name, "%s_brom.xco" % self.name))
        designer.add_file(ipcore_path, "%s_brom/%s_brom.xco" % (self.name, self.name))

    def generate(self, designer):
        mkdir_safe(os.path.join(gen_path, ipcore_path, "%s_brom" % self.name))
        self.generateCoe()
        self.generateXco(designer)
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
        if self.internal:
            size = int(math.ceil(self.size/4.0)) #TODO: Assume 32 bits item in 128 bits mem
            data_size=128
            byte_we="true"
        else:
            size = str(self.size)
            data_size=32
            byte_we="false"
        keys={ 'NAME': self.name + "_bram",
               'SIZE': size,
               'DATA_SIZE': data_size,
               'BYTE_WE': byte_we,
               }
        self.xco_template.set_keys(keys)
        self.xco_template.generate(os.path.join(gen_path, ipcore_path, "%s_bram" % self.name, "%s_bram.xco" % self.name))

    def generate(self, designer):
        self.xco_template = FileTemplate('bram.xco')
        mkdir_safe(os.path.join(gen_path, ipcore_path, "%s_bram" % self.name))
        self.generateXco()
        designer.add_file(ipcore_path, "%s_bram/%s_bram.xco" % (self.name, self.name))
