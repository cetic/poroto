from poroto.common import load_template
from poroto.config import src_path, gen_path

class VhdlWrapper:
    def __init__(self, designer, functions_list, registers_map, memories_map, streams_map, debug):
        self.designer = designer
        self.functions = functions_list
        self.registers_map = registers_map
        self.streams_map = streams_map
        self.debug = debug
    def generate(self):
        self.designer.add_file(src_path, "poroto_pkg.vhdl")
