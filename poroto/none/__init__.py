from poroto.sdk import SDK

from c_wrapper import CWrapper
from vhdl_wrapper import VhdlWrapper
from vhdl_tb import VhdlTestBench
from c_tb import CTestBench
from streams import RocccBramInStream, RocccBramOutStream, BramStream, BramGetStream, BramSetStream
from .bram_wrapper import BramMemoryWrapper

class NoneSDK(SDK):
    def __init__(self, platform, designer, functions, registers_map, mems_map, streams_map, test_vectors, debug):
        SDK.__init__(self, debug)
        self.platform = platform
        self.test_vectors = test_vectors
        self.c_wrapper = CWrapper(functions, registers_map, streams_map, self.debug)
        self.vhdl_wrapper = VhdlWrapper(designer, functions, registers_map, mems_map, streams_map, self.debug)
        if test_vectors:
            self.vhdl_tb_generator = VhdlTestBench(designer, functions, registers_map, mems_map, streams_map, self.debug)
            self.c_tb_generator = CTestBench(functions, registers_map, streams_map, self.debug)
        else:
            self.vhdl_tb_generator = None
            self.c_tb_generator = None
        streams_map.register_stream_type('bram', BramStream)
#             stream.in_stream=True
#             stream.out_stream=True
        streams_map.register_stream_type('bram_get', BramStream)
#             stream.in_stream=True
        streams_map.register_stream_type('bram_set', BramStream)
#             stream.out_stream=True
        streams_map.register_stream_type('roccc_bram_in', RocccBramInStream)
        streams_map.register_stream_type('roccc_bram_out', RocccBramOutStream)
        streams_map.register_stream_type('internal_bram_get', BramGetStream)
        streams_map.register_stream_type('internal_bram_set', BramSetStream)

    def generate_wrappers(self):
        self.c_wrapper.generate()
        self.vhdl_wrapper.generate()
        if self.vhdl_tb_generator:
            self.vhdl_tb_generator.write(self.test_vectors)
        if self.c_tb_generator:
            self.c_tb_generator.write(self.test_vectors)

    def create_mem_wrapper(self, mem_type, name, data_type, size, init):
        if mem_type == 'bram':
            tmp = BramMemoryWrapper(name, data_type, size, init, self.debug)
            tmp.platform = self.platform
            return tmp
        else:
            raise Exception("Memory type '%s' not supported", mem_type)

    def add_intrinsic(self, designer, intrinsic):
        print "Warning: Intrinsics not supported"