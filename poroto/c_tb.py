import os
from .common import load_template
from .config import gen_path, c_path
from pycparser import c_ast

class CTestBench:
    def __init__(self, functions, mmap, streams_map, debug):
        self.functions = functions
        self.debug = debug
        self.registers_map = mmap
        self.streams_map = streams_map
        self.dma_channel = 0

    def dmaWrite(self, stream_name, addr_block, test_point):
        #data_name = "%s_%d" % (stream_name, test_point)
        #print >> self.out, '\tfpga_write_vector(%d, sizeof(%s), %s);' % (addr_block, data_name, data_name)
        pass

    def dmaReadAndVerify(self, stream_name, addr_block, test_point, data_len):
        data_name = "%s_%d" % (stream_name, test_point)
        data_expected_name = "%s_expected_%d" % (stream_name, test_point)
        #print >> self.out, '\tfpga_read_vector(%d, sizeof(%s), %s);' % (addr_block, data_name, data_name)
        print >> self.out, '\tprintf("%s: ");' % data_name
        print >> self.out, '\tfor (i = 0; i < %d; ++i) {' % data_len
        print >> self.out, '\t\tprintf("%%d ", %s[i]);' % data_name
        print >> self.out, '\t}'
        print >> self.out, '\tprintf("\\n");'
        print >> self.out, '\tif ( memcmp(%s, %s, %d*4) != 0 ) {' % ( data_name, data_expected_name, data_len)
        print >> self.out, '\t\tprintf( "Retrieved data %s is not correct\\n" );' % data_name
        print >> self.out, '\t\ttest_successful = 0;'
        print >> self.out, '\t}'


    def declareStream(self, stream, stream_name, test_point, data):
        print >> self.out, '\t%s %s_%d[%d] = {' % (stream.data_type, stream_name, test_point, len(data))
        print >> self.out, '\t\t', ', '.join(str(item) for item in data)
        print >> self.out, '\t};'

    def declareEmptyStream(self, stream, stream_name, test_point, data):
        #print >> self.out, '\t%s %s_%d[%d];' % (stream.data_type, stream_name, test_point, len(data))            
        print >> self.out, '\t%s %s_%d[%d] = {' % (stream.data_type, stream_name, test_point, len(data))
        print >> self.out, '\t\t', ', '.join(str(-1) for item in data)
        print >> self.out, '\t};'

    def declareVars(self, registers):
        for register in registers:
            print >> self.out, '\tuint32_t %s;' % register.short_name

    def writeData(self, registers, test_vectors, test_point):    
        for register in registers:
            if register.short_name in test_vectors:
                print >> self.out, '\t%s = %d;' % (register.short_name, test_vectors[register.short_name][test_point])
            else:
                print >> self.out, '\t//%s not set' % register.short_name
            
    def call(self, function, test_point):
        for stream in function.streams:
            for line in stream.get_set_data(stream.in_name+'_%d'%test_point):
                print >> self.out, '\t'+line
        params = []
        for arg in function.args.params:
            if isinstance(arg.type, c_ast.PtrDecl):
                params.append( '%s_%d' % (arg.name, test_point ) )
            else:
                params.append( arg.name )
        print >>self.out, '\t', function.name, '(', ', '.join(params), ');'        
        for stream in function.streams:
            for line in stream.get_get_data(stream.out_name+'_%d'%test_point):
                print >> self.out, '\t'+line

    def verifyData(self, registers, test_vectors, test_point):    
        for register in registers:
            if register.short_name in test_vectors:
                print >> self.out, '\tif (%s != %d ) {' % (register.short_name, test_vectors[register.short_name][test_point])
                print >> self.out, '\t\tprintf( "%s: Got %%d iso %d\\n", %s);' % (register.short_name, test_vectors[register.short_name][test_point], register.short_name)
                print >> self.out, '\t\ttest_successful = 0;'
                print >> self.out, '\t}'
            else:
                print >> self.out, '\t//%s not verified' % register.short_name
    
    def verifyFunctionEntry(self, instance, test_points, test_vectors):
        for test_point in range(test_points):
            for stream in instance.streams:
                if stream.in_stream:
                    self.declareStream(stream, stream.in_name, test_point, test_vectors[stream.in_name][test_point])
                if stream.out_stream:
                    self.declareStream(stream, stream.out_name + '_expected', test_point, test_vectors[stream.out_name][test_point])
                    self.declareEmptyStream(stream, stream.out_name, test_point, test_vectors[stream.out_name][test_point])
        self.declareVars(self.registers_map.block_in_registers[instance.name])
        self.declareVars(self.registers_map.block_out_registers[instance.name])
        for test_point in range(test_points):
            print >> self.out, "\n\t// Test point %d\n" % test_point
            for stream_name in instance.streams:
                if stream.in_stream:
                    self.dmaWrite(stream_name, stream.memory.index, test_point)
            self.writeData(self.registers_map.block_in_registers[instance.name], test_vectors, test_point)
            self.call(instance, test_point)
            self.verifyData(self.registers_map.block_out_registers[instance.name], test_vectors, test_point)
            for stream in instance.streams:
                if stream.out_stream:
                    self.dmaReadAndVerify(stream.out_name, stream.memory.index, test_point, len(test_vectors[stream.out_name][test_point]))

    def printTb(self, test_vectors):
        for instance in self.functions:
            if instance.name in test_vectors:
                print >> self.out
                print >> self.out, '\t//*****************************************************************************'
                print >> self.out, '\t// APPLICATION: SIMULATION  PATTERN  -- Function %s' % instance.name
                print >> self.out, '\t//*****************************************************************************'
                print >> self.out
                self.verifyFunctionEntry(instance, test_vectors[instance.name].test_points, test_vectors[instance.name].test_vectors)
    
    def printTbInit(self, test_vectors):
        for instance in self.functions:
            for stream in instance.streams:
                for line in stream.get_c_def():
                    print >> self.out, line

    def write(self, test_vectors):
        self.tb_template = load_template('tb.c', top_dir=c_path)
        self.out = open(os.path.join(gen_path, 'c', 'tb.cpp'), 'w' )
        for line in self.tb_template:
            if '%%%TB%%%' in line:
                self.printTb(test_vectors)
            elif '%%%INIT%%%' in line:
                self.printTbInit(test_vectors)
            else:
                print >> self.out, line,
        self.out.close()
