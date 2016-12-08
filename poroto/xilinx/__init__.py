from poroto.platform import Platform
from poroto.common import load_template, mkdir_safe
from poroto.config import gen_path, src_path, ipcore_path
from poroto import roccc

from .bram import BramMemory, BromMemory
from .fifo import Fifo

class XilinxPlatform(Platform):
    def __init__(self, designer, debug):
        Platform.__init__(self, designer, debug)
        designer.add_file(src_path, "HwBramFifo.vhdl")
        roccc.intrinsics.add_fp_add(latency=11)
        roccc.intrinsics.add_fp_sub(latency=11)
        roccc.intrinsics.add_fp_mul(latency=8)
        roccc.intrinsics.add_fp_div(latency=28)
        roccc.intrinsics.add_int_div(latency=13)

    def create_mem(self, mem_type, name, data_type, size, init):
        if mem_type == 'bram':
            return BramMemory(name, data_type, size, init, self.debug)
        elif mem_type == 'brom':
            return BromMemory(name, data_type, size, init, self.debug)

    def create_fifo(self):
        return Fifo(self.debug)

    def add_intrinsic(self, designer, intrinsic):
        designer.add_file(src_path, "%s.vhdl" % intrinsic)
        designer.add_file(ipcore_path, "%s_impl/%s_impl.xco" % (intrinsic, intrinsic))
