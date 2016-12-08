from .common import get_bus_size, get_bit_width
from .pragma import PragmaHandler
from .bram import BramTemplate

class Memory:
    def __init__(self, name, data_type, size, init, debug):
        self.name = name
        self.data_type = data_type
        self.size = size
        self.init = init
        self.debug = debug
        self.data_size = get_bus_size(data_type)
        self.address_size = get_bit_width(size)

    def set_index(self, index):
        self.index = index

    def get_component(self):
        return []
    def get_instance(self):
        return []
    def generate(self, designer):
        pass

class MemoryMap:
    def __init__(self, debug):
        self.debug = debug
        self.mems = {}
        self.last_memory_index = 0

    def add_memory(self, memory):
        if self.debug:
            print "Adding memory block %s size: %d -> index: %d" % (memory.name, memory.size, self.last_memory_index)
        self.mems[memory.name] = memory
        memory.set_index(self.last_memory_index)
        self.last_memory_index += 1

class MemoryPragmaHandler(PragmaHandler):
    def __init__(self, registry, mems_map, sdk, debug):
        self.registry = registry
        self.mems_map = mems_map
        self.sdk = sdk
        self.debug = debug
    def parse_pragma(self, node, tokens, next_stmt):
        if len(tokens) < 5:
            raise Exception("Invalid memory pragma '%s'" % node.string)
        mem_name = tokens[2]
        data_type = tokens[3]
        mem_size = int(tokens[4])
        data_size=get_bus_size(data_type)
        if self.debug: print "Adding memory %s" % mem_name
        template = BramTemplate(mem_name, data_type, mem_size, data_size, self.mems_map, self.sdk, self.debug)
        self.registry.addTemplateToRegistry(template)
