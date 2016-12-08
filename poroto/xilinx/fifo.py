from poroto.config import ipcore_path

class Fifo:
    def __init__(self, designer, debug):
        self.designer = designer
        self.debug = debug

    def generate(self, wrapper):
        self.designer.add_file(ipcore_path, "hw_fifo_32/hw_fifo_32.xco")
