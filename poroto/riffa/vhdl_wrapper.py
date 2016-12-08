import os
from poroto.common import load_template
from poroto.config import gen_path
import string

class FunctionVhdlWrapper:
    def __init__(self, designer, functions, mmap, streams_map, debug):
        self.designer = designer
        self.functions = functions
        self.registers_map = mmap
        self.streams_map = streams_map
        self.debug = debug
    
    def printMemoryMap(self):
        print >>self.out, '\t------------------------'
        print >>self.out, '\t-- Input memory map'
        print >>self.out, '\t------------------------'
        for block in self.registers_map.blocks_list:
            print >>self.out, '\t-- %s' % block
            for register in self.registers_map.block_in_registers[block]:
                print >> self.out, '\t-- 0x%04x\t-\t%s' % (register.offset * 4, register.short_name)
        print >>self.out, '\t------------------------'
        print >>self.out, '\t-- Output memory map'
        print >>self.out, '\t------------------------'
        for block in self.registers_map.blocks_list:
            print >>self.out, '\t-- %s' % block
            for register in self.registers_map.block_out_registers[block]:
                print >> self.out, '\t-- 0x%04x\t-\t%s' % (register.offset * 4, register.short_name)

    def printSignals(self):
        for instance in self.functions:
            instance.printSignals(self.out)
            print >> self.out, "\tsignal %s_output_rst : std_logic;" % instance.name
            print >> self.out, "\tsignal %s_writeFirstDataIn : std_logic;" % instance.name
            print >> self.out, "\tsignal %s_resultReady : std_logic;" % instance.name

    def printComponents(self):
        for instance in self.functions:
            instance.printComponents(self.out)

    def printReset(self):
        for instance in self.functions:
            print >> self.out, "\t\t%s_inputReady <= '0';" % instance.name
            print >> self.out, "\t\t%s_writeFirstDataIn <= '0';" % instance.name
            print >> self.out, "\t\t%s_rst <= '1';" % instance.name
            print >> self.out, "\t\t%s_stall <= '1';" % instance.name
            print >> self.out, "\t\t%s_output_rst <= '1';" % instance.name
            for port in instance.in_ports:
                if port.register or port.internal:
                    if port.bitwidth == 1:
                        print >> self.out, "\t\t%s_%s <= '0';" % ( instance.name, port.name)  
                    else:
                        print >> self.out, "\t\t%s_%s <= (others => '0');" % ( instance.name, port.name)  

    def printResetResultReadyFlags(self):
        for instance in self.functions:
            print >> self.out, "\t\t%s_resultReady <= '0';" % instance.name

    def printResultReadyFlags(self):
        for instance in self.functions:
            print >> self.out, "\t\t\triffa_ctrl(0).EN <= '0';"
            for stream in instance.streams:
                if stream.out_stream:
                    print >> self.out, "\t\t\triffa_ctrl(%d).EN <= '0';" % (stream.memory.index + 1)
            if len(instance.streams) > 0:
                print >> self.out, "\t\tif %s_done = '1' then" % (instance.name)
            else:
                print >> self.out, "\t\tif %s_outputReady = '1' then" % (instance.name)
            print >> self.out, "\t\t\tif %s_resultReady = '0' then" % (instance.name)
            print >> self.out, "\t\t\t\t%s_resultReady <= '1';" % instance.name
            print >> self.out, "\t\t\t\triffa_ctrl(0).EN <= '1';"
            print >> self.out, "\t\t\t\triffa_ctrl(0).LAST <= '1';"
            print >> self.out, "\t\t\t\triffa_ctrl(0).OFF <= std_logic_vector(to_unsigned(%d, 31));" % (0x10000 / 2)
            print >> self.out, "\t\t\t\triffa_ctrl(0).LEN <= std_logic_vector(to_unsigned(%d, 32));" % (len(self.registers_map.block_out_registers[instance.name]) * 2)
            for stream in instance.streams:
                if stream.out_stream:
                    print >> self.out, "\t\t\t\triffa_ctrl(%d).EN <= '1';" % (stream.memory.index + 1)
                    print >> self.out, "\t\t\t\triffa_ctrl(%d).LAST <= '1';" % (stream.memory.index + 1)
                    print >> self.out, "\t\t\t\triffa_ctrl(%d).OFF <= std_logic_vector(to_unsigned(%d, 31));" % (stream.memory.index + 1, 0)
                    print >> self.out, "\t\t\t\triffa_ctrl(%d).LEN <= %s_%s_size;" % (stream.memory.index + 1, instance.name, stream.name)
            print >> self.out, "\t\t\telse"
            print >> self.out, "\t\t\t\triffa_ctrl(0).EN <= '0';"
            for stream in instance.streams:
                if stream.out_stream:
                    print >> self.out, "\t\t\t\triffa_ctrl(%d).EN <= '0';" % (stream.memory.index + 1)
            print >> self.out, "\t\t\tend if;"
            print >> self.out, "\t\telsif %s_writeFirstDataIn = '1' then" % instance.name
            print >> self.out, "\t\t\t%s_resultReady <= '0';" % instance.name
            print >> self.out, "\t\tend if;"

    def printResetInputReadyFlags(self):
        for instance in self.functions:
            print >> self.out, "\t\t\t%s_inputReady <= '0';" % instance.name
            print >> self.out, "\t\t\t%s_writeFirstDataIn <= '0';" % instance.name
                    
    def printReadRegs(self):
        for instance in self.functions:
            for register in self.registers_map.block_in_registers[instance.name]:
                print >> self.out, '\t\twhen  "%s" => -- %04x' % (format(register.offset, '032b'), register.offset)
                print >> self.out, '\t\t\treport "Read %s";' % register.name
                if register.size == 32:
                    print >> self.out, "\t\t\tbram_s2m.dout <= %s;" % register.name
                else:
                    print >> self.out, "\t\t\tbram_s2m.dout <= std_logic_vector(to_unsigned(0, REGISTER_DATA_SIZE-%d)) & %s;" % (register.size, register.name)
            for register in self.registers_map.block_out_registers[instance.name]:
                print >> self.out, '\t\twhen  "%s" => -- %04x' % (format(register.offset, '032b'), register.offset)
                if register.size == 32:
                    print >> self.out, "\t\t\tbram_s2m.dout <= %s;" % register.name
                else:
                    print >> self.out, "\t\t\tbram_s2m.dout <= std_logic_vector(to_unsigned(0, REGISTER_DATA_SIZE-%d)) & %s;" % (register.size, register.name)
        print >> self.out, "\t\twhen others =>"
        print >> self.out, "\t\t\tbram_s2m.dout <= bram_m2s.addr_r;"
        print >> self.out, '\t\t\treport "Read Register: Got unknown address " & integer\'image(to_integer(signed(bram_m2s.addr_r)));'

    def printWriteRegs(self):
        for instance in self.functions:
            if len(instance.streams) > 0:
                print >> self.out, "\t\tif %s_done = '1' and %s_resultReady = '0' then" % (instance.name, instance.name)
            else:
                print >> self.out, "\t\tif %s_outputReady = '1' and %s_resultReady = '0' then" % (instance.name, instance.name)
            print >> self.out, "\t\t\t%s_writeFirstDataIn <= '0';" % instance.name
            print >> self.out, "\t\tend if;"
            print >> self.out, "\t\tif (bram_m2s.we = '1') then"
            print >> self.out, "\t\tcase bram_m2s.addr_w is"
            for (i, register) in enumerate(self.registers_map.block_in_registers[instance.name]):
                print >> self.out, '\t\twhen  "%s" => -- %04x' % (format(register.offset, '032b'), register.offset)
                print >> self.out, '\t\t\treport "Write %s : " & integer\'image(to_integer(signed(bram_m2s.din)));' % register.name
                if register.size == 32:
                    print >> self.out, "\t\t\t%s <= bram_m2s.din;" % register.name
                elif register.size == 1:
                    print >> self.out, "\t\t\t%s <= bram_m2s.din(0);" % register.name
                else:
                    print >> self.out, "\t\t\t%s <= bram_m2s.din(%d downto 0);" % (register.name, register.size-1)
                if i == 1: #TODO: Beuark
                    print >> self.out, "\t\t\t%s_writeFirstDataIn <= '1';" % instance.name           
                if i == len(self.registers_map.block_in_registers[instance.name])-1:
                    print >> self.out, '\t\t\treport "Triggering core %s";' % instance.name
                    print >> self.out, "\t\t\t%s_inputReady <= '1';" % instance.name
                    print >> self.out, "\t\t\t%s_stall <= '0';" % instance.name
                    print >> self.out, "\t\t\t%s_rst <= '0';" % instance.name
                    print >> self.out, "\t\t\t%s_output_rst <= '0';" % instance.name

        print >> self.out, "\t\twhen others =>"
        print >> self.out, '\t\t\treport "Write Register: Got unknown address " & integer\'image(to_integer(signed(bram_m2s.addr_w)));'
        print >> self.out, "\t\tend case;"
        print >> self.out, "\t\tend if;"
    def printInterfaces(self):
        for instance in self.functions:
            instance.printPortMap(self.out, 'usr_clk')
                
    def wrapFunctions(self):
        #TODO: hardcoded name
        self.addr_decoder_template = load_template('registers.vhdl')
        self.designer.add_file(gen_path, "vhdl_wrapper.vhdl")
        self.out = open(os.path.join(gen_path, 'vhdl', 'vhdl_wrapper.vhdl'), 'w' )
        for line in self.addr_decoder_template:
            if '%%%INTERFACES%%%' in line:
                self.printInterfaces()
            elif '%%%MEMMAP%%%' in line:
                self.printMemoryMap()
            elif '%%%COMPONENTS%%%' in line:
                self.printComponents()
            elif '%%%SIGNALS%%%' in line:
                self.printSignals()
            elif '%%%RESET%%%' in line:
                self.printReset()
            elif '%%%RESET_RESULT_READY%%%' in line:
                self.printResetResultReadyFlags()
            elif '%%%RESULT_READY%%%' in line:
                self.printResultReadyFlags()
            elif '%%%RESET_INPUT_READY%%%' in line:
                self.printResetInputReadyFlags()
            elif '%%%READ_REGS%%%' in line:
                self.printReadRegs()
            elif '%%%WRITE_REGS%%%' in line:
                self.printWriteRegs()
            else:
                print >> self.out, line,
        self.out.close()

class VhdlMainWrapper:
    def __init__(self, designer, mem_map, debug):
        self.designer = designer
        self.mem_map = mem_map
        self.debug = debug

    def printMemoryMap(self):
        for memory in self.mem_map.mems.itervalues():
            instance = memory.get_instance()
            for line in instance:
                print >> self.out, "\t%s" % line
            print >> self.out

    def printMemoryComponents(self):
        for memory in self.mem_map.mems.itervalues():
            component = memory.get_component()
            for line in component:
                print >> self.out, "\t%s" % line
            print >> self.out

    def generate(self):
        #TODO: hardcoded name
        self.vhdl_main_template = load_template('poroto.vhdl')
        self.designer.add_file(gen_path, "poroto.vhdl")
        self.out = open(os.path.join(gen_path, 'vhdl', 'poroto.vhdl'), 'w' )
        for line in self.vhdl_main_template:
            if '%%%MEMORY%%%' in line:
                self.printMemoryMap()
            elif '%%%MEM_COMPONENTS%%%' in line:
                self.printMemoryComponents()
            else:
                print >> self.out, line,
        self.out.close()

class VhdlMainPkg:
    def __init__(self, designer, mem_map, debug):
        self.designer = designer
        self.mem_map = mem_map
        self.debug = debug

    def generate(self):
        #TODO: hardcoded name
        self.vhdl_main_pkg_template = load_template('poroto_pkg.vhdl')
        self.designer.add_file(gen_path, "poroto_pkg.vhdl")
        self.out = open(os.path.join(gen_path, 'vhdl', 'poroto_pkg.vhdl'), 'w' )
        brams_nb = len(self.mem_map.mems)
        #Temporary workaround
        if brams_nb == 0:
            brams_nb = 1
        for line in self.vhdl_main_pkg_template:
            if '%%%BRAMS_NB%%%' in line:
                line = string.replace(line, '%%%BRAMS_NB%%%', str(brams_nb))
            print >> self.out, line,
        self.out.close()

class VhdlWrapper:
    def __init__(self, designer, functions_list, registers_map, memories_map, streams_map, debug):
        self.function_vhdl_wrapper = FunctionVhdlWrapper(designer, functions_list, registers_map, streams_map, debug)
        self.vhdl_main_wrapper = VhdlMainWrapper(designer, memories_map, debug)
        self.vhdl_main_pkg = VhdlMainPkg(designer, memories_map, debug)

    def generate(self):
        self.function_vhdl_wrapper.wrapFunctions()
        self.vhdl_main_wrapper.generate()
        self.vhdl_main_pkg.generate()
