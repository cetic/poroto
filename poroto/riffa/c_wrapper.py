import os
from poroto.config import gen_path
from pycparser import c_generator

class CWrapper:
    def __init__(self, functions, mmap, streams_map, debug):
        self.functions = functions
        self.registers_map = mmap
        self.streams_map = streams_map
        self.debug = debug

    def wrapFunction(self, instance):
        if self.debug: print "Adding C wrapper for function %s" % instance.name
        generator = c_generator.CGenerator()
        print >> self.header, "extern", generator.visit(instance.decl), ';'
        for stream in instance.streams:
            for line in stream.get_c_decl():
                print >> self.code, line
        print >> self.code, generator.visit(instance.decl)
        print >> self.code, '{'
        for stream in instance.streams:
            print >> self.code, "\tuint32_t %s_size = %s;" % (stream.name, stream.size)
        for register in self.registers_map.block_in_registers[instance.name]:
            if register.short_name == 'rst':
                print >> self.code, "\tpFpgaSpace[0x%x] = 1; //reset block" % (register.offset/4)
        for stream in instance.streams:
            if stream.in_stream:
                print >> self.code, "\tfpga_write_vector(%d, (%s)*4, %s);" % (stream.memory.index, stream.size, stream.name)
        for register in self.registers_map.block_in_registers[instance.name]:
            if register.short_name == 'rst':
                pass
            elif register.short_name == 'stall':
                pass
            else:
                print >> self.code, "\tpFpgaSpace[0x%x] = (uint32_t)%s;" % (register.offset/4, register.short_name)
            #print >> self.code, "\t//pFpgaSpace[0x%x] = 1; //set inputReady <= 1" % (offset/4)
        for register in self.registers_map.block_out_registers[instance.name]:
            if register.short_name == 'resultReady':
                print >> self.code, "\twhile (pFpgaSpace[0x%x] == 0) ; //Wait for resultReady" % (register.offset/4)
            else:
                print >> self.code, "\t%s = pFpgaSpace[0x%x];" % (register.short_name, register.offset/4)
        for stream in instance.streams:
            if stream.out_stream:
                print >> self.code, "\tfpga_read_vector(%d, (%s)*4, %s);" % (stream.memory.index, stream.size, stream.name)
        print >> self.code, '}'

    def generate(self):
        self.header = open(os.path.join(gen_path, 'c', 'c_wrapper.h'), 'w' )
        self.code = open(os.path.join(gen_path, 'c', 'c_wrapper.cpp'), 'w' )
        print >> self.code, "#include <inttypes.h>"
        print >> self.code, '#include "fpga.h"'
        for function in self.functions:
            self.wrapFunction(function)
        self.code.close()
        self.header.close()
