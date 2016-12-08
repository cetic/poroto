import os
from poroto.config import gen_path
from pycparser import c_generator

class CWrapper:
    def __init__(self, functions, mmap, streams_map, debug):
        self.functions = functions
        self.registers_map = mmap
        self.streams_map = streams_map
        self.debug = debug

    def def_input_registers(self, registers):
        count = 1
        for (i, register) in enumerate(registers):
            if register.short_name is not "rst" and register.short_name is not "stall":
                count = count + 1
        print >> self.code, "\tuint32_t input_registers[%d];" % count

    def write_input_registers(self, registers):
        count = 1
        for (i, register) in enumerate(registers):
            if register.short_name is not "rst" and register.short_name is not "stall":
                count = count + 1
        offset = 0
        print >> self.code, "\tinput_registers[%d] = 0;" % offset        
        offset += 1
        for (i, register) in enumerate(registers):
            if register.short_name is not "rst" and register.short_name is not "stall":
                print >> self.code, "\tinput_registers[%d] = %s;" % (offset, register.short_name)        
                offset += 1
        print >> self.code, "\tporoto_fpga_write_vector(0, sizeof(input_registers), input_registers);"

    def def_output_registers(self, registers):
        count = 0
        for (i, register) in enumerate(registers):
            if register.short_name is not "rst" and register.short_name is not "stall":
                count = count + 1
        print >> self.code, "\tuint32_t output_registers[%d];" % count

    def read_output_registers(self, registers):
        count = 0
        for (i, register) in enumerate(registers):
            if register.short_name is not "rst" and register.short_name is not "stall":
                count = count + 1
        print >> self.code, "\tporoto_fpga_read_vector(0, sizeof(output_registers), output_registers);"
        offset = 0
        print >> self.code, "\t//resultReady = output_registers[%d];" % offset        
        offset += 1
        for (i, register) in enumerate(registers):
            if register.short_name is not "resultReady":
                print >> self.code, "\t%s = output_registers[%d];" % (register.short_name, offset)        
                offset += 1

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
        self.def_input_registers(self.registers_map.block_in_registers[instance.name])
        self.def_output_registers(self.registers_map.block_out_registers[instance.name])
        for stream in instance.streams:
            if stream.in_stream:
                print >> self.code, "\tporoto_fpga_write_vector(%d, (%s)*4, %s);" % (stream.memory.index+1, stream.size, stream.name)

        self.write_input_registers(self.registers_map.block_in_registers[instance.name])
        self.read_output_registers(self.registers_map.block_out_registers[instance.name])

        for stream in instance.streams:
            if stream.out_stream:
                print >> self.code, "\tporoto_fpga_read_vector(%d, (%s)*4, %s);" % (stream.memory.index+1, stream.size, stream.name)
        print >> self.code, '}'

    def generate(self):
        self.header = open(os.path.join(gen_path, 'c', 'c_wrapper.h'), 'w' )
        self.code = open(os.path.join(gen_path, 'c', 'c_wrapper.cpp'), 'w' )
        print >> self.code, "#include <inttypes.h>"
        print >> self.code, '#include "poroto.h"'
        for function in self.functions:
            self.wrapFunction(function)
        self.code.close()
        self.header.close()
