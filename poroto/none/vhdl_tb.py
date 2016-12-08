import os
from poroto.common import load_template
from poroto.config import gen_path, src_path
from poroto.common import convert_format_hex, convert_format_bin

class VhdlTestBench:
    def __init__(self, designer, functions, mmap, mem_map, streams_map, debug):
        self.designer = designer
        self.functions = functions
        self.debug = debug
        self.registers_map = mmap
        self.streams_map = streams_map
        self.mem_map = mem_map
        self.dma_channel = 0

    def printComponents(self, test_vectors):
        for instance in self.functions:
            if instance.name in test_vectors:
                instance.printComponents(self.out)

    def printInputChannelSignals(self, instance, stream_name):
        pass

    def printOutputChannelSignals(self, instance, stream_name):
        print >> self.out, "\tsignal %s_%s_output_status : STD_LOGIC;" % (instance.name, stream_name)

    def printSignals(self, test_vectors):
        for instance in self.functions:
            if instance.name in test_vectors:
                instance.printSignals(self.out)
                for stream in instance.roccc_in_streams:
                    self.printInputChannelSignals(instance, stream)
                for stream in instance.roccc_out_streams:
                    self.printOutputChannelSignals(instance, stream)
                
    def printInputChannelComponents(self, instance, stream, input_values):
        print >> self.out, "\t%s_%s_stream : InputStream generic map (" % (instance.name, stream.name)
        print >> self.out, "\t  CHANNEL_BITWIDTH => %s_%s_data_channel0'length," % (instance.name, stream.name)
        print >> self.out, "\t  NUM_CHANNELS => %s_%s_stream_NUM_CHANNELS," % (instance.name, stream.name)
        print >> self.out, "\t  CONCURRENT_MEM_ACCESS => 1,"
        print >> self.out, "\t  NUM_MEMORY_ELEMENTS => %d," % len(input_values)
        print >> self.out, "\t  STREAM_NAME => \"%s\"" % (stream.name)
        print >> self.out, "\t  )"
        print >> self.out, "\tport map ("
        print >> self.out, "\t  clk => clk,"
        print >> self.out, "\t  rst => %s_rst,"% (instance.name)
        print >> self.out, "\t  full_in => %s_%s_full," % (instance.name, stream.name)
        print >> self.out, "\t  write_enable_out => %s_%s_writeEn," % (instance.name, stream.name)
        print >> self.out, "\t  channel_out => %s_%s_stream_channel," % (instance.name, stream.name)
        print >> self.out, "\t  address_in => %s_%s_stream_address," % (instance.name, stream.name)
        offset = 0
        stride = stream.data_size
        for value in input_values:
            print >> self.out, "\t  memory(%d downto %d) => %s," % (offset + stride - 1, offset, convert_format_bin(stream.data_type, value, stride))
            offset += stride
        print >> self.out, "\t  read_in => %s_%s_address_translator_address_valid" % (instance.name, stream.name)
        print >> self.out, "\t);"

    def printOutputChannelComponents(self, instance, stream, output_values):
        print >> self.out, "\t%s_%s_stream_out : OutputStream" % (instance.name, stream.name)
        print >> self.out, "\tgeneric map ("
        print >> self.out, "\t  CHANNEL_BITWIDTH => 32,"
        print >> self.out, "\t  NUM_MEMORY_ELEMENTS => %d," % len(output_values)
        print >> self.out, "\t  NUM_CHANNELS => 1,"
        print >> self.out, "\t  STREAM_NAME => \"%s\"" % (stream.name)
        print >> self.out, "\t  )"
        print >> self.out, "\tport map ("
        print >> self.out, "\t  clk => clk,"
        print >> self.out, "\t  rst => %s_rst," % (instance.name)
        print >> self.out, "\t  done_in => %s_%s_done," % (instance.name, stream.name)
        print >> self.out, "\t  empty_in => %s_%s_0_empty," % (instance.name, stream.name)
        print >> self.out, "\t  read_enable_out => %s_%s_0_stream_read_enable," % (instance.name, stream.name)
        print >> self.out, "\t  channel_in => %s_%s_0_mc_data," % (instance.name, stream.name)
        print >> self.out, "\t  address_in => %s_%s_0_address_fifo_data_2," % (instance.name, stream.name)
        print >> self.out, "\t  read_in => %s_%s_0_read," % (instance.name, stream.name)
        print >> self.out, "\t  output_status => %s_%s_output_status," % (instance.name, stream.name)
        print >> self.out, "\t  OUTPUT_CORRECT =>"
        print >> self.out, "\t  ("
        for (i, value) in enumerate(output_values):
            print >> self.out, "\t  %s%s" % (convert_format_hex(stream.data_type, value), ',' if i < len(output_values) - 1 else ')')
        print >> self.out, "\t  );"

    def printPortMaps(self, test_vectors):
        for instance in self.functions:
            if instance.name in test_vectors:
                for stream in instance.streams:
                    if stream.in_stream:
                        #TODO: more than one input should be supported
                        input_values = test_vectors[instance.name].test_vectors[stream.name][0]
                        self.printInputChannelComponents(instance, stream, input_values)
                instance.printPortMap(self.out, 'clk')
                for stream in instance.streams:
                    if stream.out_stream:
                        #TODO: more than one output should be supported
                        output_values = test_vectors[instance.name].test_vectors[stream.name][0]
                        self.printOutputChannelComponents(instance, stream, output_values)

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

    def stimulateFunctionEntry(self, instance, test_points, test_vectors):
        for test_point in range(test_points):
            for (i, port) in enumerate(instance.in_ports):
                if not port.register or port.internal:
                    continue
                if port.name in test_vectors:
                    value = test_vectors[port.name][test_point]
                    print >> self.out, "\t%s_%s <= %s;" % (instance.name, port.name, convert_format_bin(port.data_type, value, port.bitwidth))
                else:
                    raise Exception("No test signal for port %s" % port.name)
            print >> self.out, "\t%s_inputReady <= '1';" % instance.name
            print >> self.out, "\twait for clk_period;"

    def printStimulate(self, test_vectors):
        for instance in self.functions:
            if instance.name in test_vectors:
                print >> self.out
                print >> self.out, '\t--*****************************************************************************'
                print >> self.out, '\t-- APPLICATION: SIMULATION PATTERN  -- Function %s' % instance.name
                print >> self.out, '\t--*****************************************************************************'
                print >> self.out
                print >> self.out, "\t%s_inputReady <= '0';" % instance.name
                print >> self.out, "\t%s_stall <= '0';" % instance.name
                print >> self.out, "\twait for clk_period * 10;"
                print >> self.out, "\trst <= '1';"
                print >> self.out, "\t%s_rst <= '1';" % instance.name
                print >> self.out, "\twait for clk_period * 10;"
                print >> self.out, "\trst <= '0';"
                print >> self.out, "\t%s_rst <= '0';" % instance.name
                self.stimulateFunctionEntry(instance, test_vectors[instance.name].test_points, test_vectors[instance.name].test_vectors)
                print >> self.out, "\t%s_inputReady <= '0';" % instance.name

    def verifyFunctionEntry(self, instance, test_points, test_vectors):
        for test_point in range(test_points):
            if instance.system:
                print >> self.out, "\twait until clk'event and clk ='1' and %s_done = '1'" % instance.name,
                for stream in instance.roccc_out_streams:
                    print >> self.out, "and %s_%s_done = '1' and %s_%s_output_status = '1'" % (instance.name, stream, instance.name, stream),
                print >> self.out, ";"
            else:
                print >> self.out, "\twait until clk'event and clk ='1' and %s_outputReady = '1';" % instance.name
            for (i, port) in enumerate(instance.out_ports):
                if port.name in test_vectors:
                    value = test_vectors[port.name][test_point]
                    print >> self.out, "\tif (%s_%s = %s) then" % (instance.name, port.name, convert_format_hex(port.data_type, value))
                    print >> self.out, "\t\tassert false report \"Test return value for : %s ok.\" severity note;" % (port.name)
                    print >> self.out, "\telse"
                    print >> self.out, "\t\tassert false report \"Test return value for : %s = %d failed. Actual value = \" & integer'image(to_integer(signed(%s_%s))) severity error;" % (port.name, value, instance.name, port.name)
                    print >> self.out, "\t\ttest_passed <= false;"
                    print >> self.out, "\tend if;"

    def printVerify(self, test_vectors):
        for instance in self.functions:
            if instance.name in test_vectors:
                print >> self.out
                print >> self.out, '\t--*****************************************************************************'
                print >> self.out, '\t-- APPLICATION: Verification  -- Function %s' % instance.name
                print >> self.out, '\t--*****************************************************************************'
                print >> self.out
                print >> self.out, "\twait until clk'event and clk ='1' and %s_rst = '1';" % instance.name
                self.verifyFunctionEntry(instance, test_vectors[instance.name].test_points, test_vectors[instance.name].test_vectors)

    def write(self, test_vectors):
        self.designer.add_file(src_path, "StreamHandler.vhdl", synth=False)
        #TODO: hardcoded name
        self.tb_template = load_template('tb.vhdl')
        self.designer.add_file(gen_path, "tb.vhdl", synth=False)
        self.out = open(os.path.join(gen_path, 'vhdl', 'tb.vhdl'), 'w' )
        for line in self.tb_template:
            if '%%%COMPONENTS%%%' in line:
                self.printComponents(test_vectors)
            elif '%%%SIGNALS%%%' in line:
                self.printSignals(test_vectors)
            elif '%%%PORTMAPS%%%' in line:
                self.printPortMaps(test_vectors)
            elif '%%%MEMORY%%%' in line:
                self.printMemoryMap()
            elif '%%%MEM_COMPONENTS%%%' in line:
                self.printMemoryComponents()
            elif '%%%STIMULATE%%%' in line:
                self.printStimulate(test_vectors)
            elif '%%%VERIFY%%%' in line:
                self.printVerify(test_vectors)
            else:
                print >> self.out, line,
        self.out.close()
