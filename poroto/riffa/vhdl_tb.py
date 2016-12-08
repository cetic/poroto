import os
from poroto.common import load_template
from poroto.config import gen_path

class VhdlTestBench:
    def __init__(self, designer, functions, mmap, streams_map, debug):
        self.designer = designer
        self.functions = functions
        self.debug = debug
        self.registers_map = mmap
        self.streams_map = streams_map
        self.dma_channel = 0

    def channelInSignals(self, stream_name, channel, test_point, data):
        print >> self.out, "\tsignal data_%s_%d : word_vector_t(0 to %d-1) := (" % (stream_name, test_point, len(data))
        for (i, value) in enumerate(data):
            print >> self.out, "\t  std_logic_vector(to_unsigned(%d, C_PCI_DATA_WIDTH))%s" % (value, ',' if i < len(data) - 1 else '')
        print >> self.out, "\t);"

    def channelOutSignals(self, stream_name, channel, test_point, data):
        print >> self.out, "\tsignal data_%s_%d : word_vector_t(0 to %d-1);" % (stream_name, test_point, len(data))
        print >> self.out, "\tsignal data_%s_%d_offset : natural;" % (stream_name, test_point)
        print >> self.out, "\tsignal data_%s_%d_len : natural;" % (stream_name, test_point)
        print >> self.out, "\tsignal data_%s_%d_last : std_logic;" % (stream_name, test_point)
        print >> self.out, "\tsignal data_%s_%d_expected : word_vector_t(0 to %d-1) := (" % (stream_name, test_point, len(data))
        for (i, value) in enumerate(data):
            print >> self.out, "\t  std_logic_vector(to_unsigned(%d, C_PCI_DATA_WIDTH))%s" % (value, ',' if i < len(data) - 1 else '')
        print >> self.out, "\t);"

    def channelWrite(self, stream_name, channel, test_point):
        print >> self.out, '\t------------------------------------------'
        print >> self.out, '\t-- Write %s' % (stream_name)
        print >> self.out, '\t------------------------------------------'
        print >> self.out, '\treport "Writing channel %s (%d)";' % (stream_name, channel)
        print >> self.out, "\triffa_channel_write(0, data_%s_%d, '1', clk, riffa_rx_m2s(%d), riffa_rx_s2m(%d));" % (stream_name, test_point, channel, channel)

    def channelRead(self, stream_name, channel, test_point):
        print >> self.out, '\t------------------------------------------'
        print >> self.out, '\t-- Read %s' % (stream_name)
        print >> self.out, '\t------------------------------------------'
        print >> self.out, '\treport "Reading channel %s (%d)";' % (stream_name, channel)
        print >> self.out, "\triffa_channel_read(data_%s_%d_offset, data_%s_%d_len, data_%s_%d, data_%s_%d_last, clk, riffa_tx_m2s(%d), riffa_tx_s2m(%d));" % (stream_name, test_point, stream_name, test_point, stream_name, test_point, stream_name, test_point, channel, channel)

    def channelVerify(self, stream_name, channel, test_point):
        print >> self.out, '\t------------------------------------------'
        print >> self.out, '\t-- Read %s' % (stream_name)
        print >> self.out, '\t------------------------------------------'
        print >> self.out, '\treport "Verify channel %s (%d)";' % (stream_name, channel)
        print >> self.out, "\tverify_memory(data_%s_%d, data_%s_%d_len, data_%s_%d_expected, test_ok);" % (stream_name, test_point, stream_name, test_point, stream_name, test_point)

    def registersInSignals(self, registers, test_point, test_vectors):
        print >> self.out, '\t------------------------------------------'
        print >> self.out, '\t-- Write Registers'
        print >> self.out, '\t------------------------------------------'
        count = 1
        for (i, register) in enumerate(registers):
            if register.short_name is not "rst" and register.short_name is not "stall":
                count = count + 1
        print >> self.out, "\tsignal registers_in_%d : word_vector_t(0 to %d-1) := (" % (test_point, count)
        offset = 0
        print >> self.out, "\t  std_logic_vector(to_unsigned(0, C_PCI_DATA_WIDTH))%s" % (',' if offset < count - 1 else '')
        offset += 1
        for (i, register) in enumerate(registers):
            if register.short_name is not "rst" and register.short_name is not "stall":
                value = test_vectors[register.short_name][test_point]
                print >> self.out, "\t  std_logic_vector(to_unsigned(%d, C_PCI_DATA_WIDTH))%s" % (value, ',' if offset < count - 1 else '')
                offset += 1
        print >> self.out, "\t);"

    def registersOutSignals(self, registers, test_point, test_vectors):
        print >> self.out, '\t------------------------------------------'
        print >> self.out, '\t-- Read Registers'
        print >> self.out, '\t------------------------------------------'
        count = 1
        for (i, register) in enumerate(registers):
            if register.short_name is not "rst" and register.short_name is not "stall":
                count = count + 1
        print >> self.out, "\tsignal registers_out_%d : word_vector_t(0 to %d-1);" % (test_point, count)
        print >> self.out, "\tsignal registers_out_%d_offset : natural;" % test_point
        print >> self.out, "\tsignal registers_out_%d_len : natural;" % test_point
        print >> self.out, "\tsignal registers_out_%d_last : std_logic;" % test_point

    def registersInWrite(self, test_point):
        print >> self.out, '\t------------------------------------------'
        print >> self.out, '\t-- Write Registers'
        print >> self.out, '\t------------------------------------------'
        print >> self.out, '\treport "Writing registers channel";'
        print >> self.out, "\triffa_channel_write(0, registers_in_%d, '1', clk, riffa_rx_m2s(0), riffa_rx_s2m(0));" % test_point

    def registersOutRead(self, test_point):
        print >> self.out, '\t------------------------------------------'
        print >> self.out, '\t-- Read Registers'
        print >> self.out, '\t------------------------------------------'
        print >> self.out, '\treport "Reading registers channel";'
        print >> self.out, "\triffa_channel_read(registers_out_%d_offset, registers_out_%d_len, registers_out_%d, registers_out_%d_last, clk, riffa_tx_m2s(0), riffa_tx_s2m(0));" % (test_point, test_point, test_point, test_point)

    def registersResetWrite(self):
        print >> self.out, '\treport "Trigger reset";'
        print >> self.out, "\triffa_channel_write(0, registers_reset, '1', clk, riffa_rx_m2s(0), riffa_rx_s2m(0));"
        print >> self.out, "\twait for clk_period * 10;"
    
    def verifyFunctionEntry(self, instance, test_points, test_vectors):
        for test_point in range(test_points):
            for stream in instance.streams:
                if stream.in_stream:
                    self.channelWrite(stream.in_name, stream.memory.index + 1, test_point)
            self.registersInWrite(test_point)
            self.registersOutRead(test_point)
            for stream in instance.streams:
                if stream.out_stream:
                    self.channelRead(stream.out_name, stream.memory.index + 1, test_point)
            for stream in instance.streams:
                if stream.out_stream:
                    self.channelVerify(stream.out_name, stream.memory.index + 1, test_point)
            self.registersResetWrite()
    def printSignals(self, test_vectors):
        for instance in self.functions:
            for test_point in range(test_vectors[instance.name].test_points):
                if instance.name in test_vectors:
                    for stream in instance.streams:
                        if stream.in_stream:
                            self.channelInSignals(stream.in_name, stream.memory.index, test_point, test_vectors[instance.name].test_vectors[stream.in_name][test_point])
                            #Inject virtual register value
                            if not stream.in_name+"_size" in test_vectors[instance.name].test_vectors:
                                test_vectors[instance.name].test_vectors[stream.in_name+"_size"] = []
                            test_vectors[instance.name].test_vectors[stream.in_name+"_size"].append(len(test_vectors[instance.name].test_vectors[stream.in_name][test_point]))
                        if stream.out_stream:
                            self.channelOutSignals(stream.out_name, stream.memory.index, test_point, test_vectors[instance.name].test_vectors[stream.in_name][test_point])
                            #Inject virtual register value
                            if not stream.out_name+"_size" in test_vectors[instance.name].test_vectors:
                                test_vectors[instance.name].test_vectors[stream.out_name+"_size"] = []
                            test_vectors[instance.name].test_vectors[stream.in_name+"_size"].append(len(test_vectors[instance.name].test_vectors[stream.in_name][test_point]))
                    self.registersInSignals(self.registers_map.block_in_registers[instance.name], test_point, test_vectors[instance.name].test_vectors)
                    self.registersOutSignals(self.registers_map.block_out_registers[instance.name], test_point, test_vectors[instance.name].test_vectors)

    def printTb(self, test_vectors):
        for instance in self.functions:
            if instance.name in test_vectors:
                print >> self.out
                print >> self.out, '\t--*****************************************************************************'
                print >> self.out, '\t-- APPLICATION: SIMULATION  PATTERN  -- Function %s' % instance.name
                print >> self.out, '\t--*****************************************************************************'
                print >> self.out
                self.verifyFunctionEntry(instance, test_vectors[instance.name].test_points, test_vectors[instance.name].test_vectors)
    
    def write(self, test_vectors):
        #TODO: hardcoded name
        self.tb_template = load_template('tb.vhdl')
        self.designer.add_file(gen_path, "tb.vhdl", synth=False)
        self.out = open(os.path.join(gen_path, 'vhdl', 'tb.vhdl'), 'w' )
        for line in self.tb_template:
            if '%%%SIGNALS%%%' in line:
                self.printSignals(test_vectors)
            elif '%%%STIMULATE%%%' in line:
                self.printTb(test_vectors)
            else:
                print >> self.out, line,
        self.out.close()
