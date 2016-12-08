from poroto.platform import Platform
from bram import BramMemory, BromMemory
from poroto.config import src_path, use_unisim

class SimPlatform(Platform):
    def __init__(self, designer, debug):
        Platform.__init__(self, designer, debug)
        designer.add_file(src_path, "bram.vhdl")
        if use_unisim:
            designer.add_file(src_path, "HwBramFifo.vhdl")
        else:
            designer.add_file(src_path, "SyncFifoWrapper.vhdl")
            designer.add_file(src_path, "SyncFifo.vhdl")
    def create_mem(self, mem_type, name, data_type, size, init):
        if mem_type == 'bram':
            return BramMemory(name, data_type, size, init, self.debug)
        elif mem_type == 'brom':
            return BromMemory(name, data_type, size, init, self.debug)

    def create_fifo(self):
        raise Exception("FIFO not supported yet for this platform")
