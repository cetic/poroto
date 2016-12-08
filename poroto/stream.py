from .config import user_signals
from .common import get_bus_size, get_bus_sign
from .pragma import PragmaHandler
import re

class Stream:
    def __init__(self, name, memory_name, size, data_size, debug):
        self.name = name
        self.debug = debug
        self.instance=None
        self.memory_name = memory_name
        self.size = size
        self.data_size = data_size
        self.in_stream=False
        self.out_stream=False
        self.in_name=None
        self.out_name=None

    def assign_instance(self, instance, from_instance):
        self.full_name = instance.name + '_' + self.name
        self.instance=instance
        if instance.name not in user_signals:
            user_signals[instance.name] = []
        user_signals[instance.name].append(self)

    def resolve_stream(self, mems_map):
        print "Resolving stream %s" % self.name
        self.memory = mems_map.mems[self.memory_name]
        self.data_type = self.memory.data_type
        if not self.memory_name in mems_map.mems:
            Exception("Memory block %s unknown" % self.memory_name)
        if self.data_size == -1:
            self.data_size=self.memory.data_size
        if self.data_size != self.memory.data_size:
            Exception("Data size of memory not compatible with stream")
        if self.in_stream and self.out_stream:
            self.in_name=self.name+'_in'
            self.out_name=self.name+'_out'
        else:
            self.in_name=self.name
            self.out_name=self.name

    def register_reference(self, functions, function):
        pass
    def get_user_signals(self):
        return []
    def get_temp_signals(self):
        return []
    def get_port_map(self):
        return []
    def get_adapter_instance(self):
        return []
    def get_c_decl(self):
        return []
    def get_c_def(self):
        return []
    def get_set_data(self, src):
        return []
    def get_get_data(self, target):
        return []

class StreamMap:
    def __init__(self, mems_map, functions, debug):
        self.debug = debug
        self.streams_types = {}
        self.mems_map = mems_map
        self.functions = functions
        self.blocks = {}
        self.functions.streams_map = self #TODO: Circular references

    def register_stream_type(self, stream_id, stream_class):
        if stream_id not in self.streams_types:
            self.streams_types[stream_id] = stream_class
        else:
            raise Exception("Stream %s already registered" % stream_id)
    def add_stream(self, block, stream):
        if self.debug: print "Registering stream %s for %s" % (stream.name, block)
        if block not in self.blocks:
            self.blocks[block] = {}
        self.blocks[block][stream.name] = stream
        self.functions.register_manual_reference(block, stream.memory_name)
        stream.register_reference(self.functions, block)
        return self.blocks[block][stream.name]

    def get_stream_info(self, block, stream):
        if block in self.blocks:
            if stream in self.blocks[block]:
                return self.blocks[block][stream]
        return None

    def stream_class(self, stream_type):
        if stream_type in self.streams_types:
            return self.streams_types[stream_type]
        else:
            raise Exception("Unknown stream type %s" % stream_type)

    def consolidate(self):
        for block in self.blocks.itervalues():
            for stream in block.itervalues():
                if stream.memory_name not in self.functions.function_templates:
                    raise Exception("Stream %s: Memory %s not found" % (stream.name, stream.memory_name))

class StreamPragmaHandler(PragmaHandler):
    def __init__(self, streams_map, debug):
        self.streams_map = streams_map
        self.debug = debug
    def parse_pragma(self, node, tokens, next_stmt):
        line = ' '.join(tokens[1:])
        m=re.match( r'stream::(\w+)\s+(\w+)::(\w+)\s*\(\s*(.+)\s*\)', line)
        if not m:
            raise Exception("Invalid poroto stream pragma")
        function_name=m.group(2)
        stream_name=m.group(3)
        stream_type=m.group(1)
        params=re.split('\s*,\s*', m.group(4))
        size=params[1]
        memory_name=params[0]
        if len(params) > 2:
            data_type=params[2]
            data_size=get_bus_size(data_type)
            data_sign=get_bus_sign(data_type)
        else:
            data_size=-1
            data_sign=True
        if self.debug:
            print "Adding stream %s %s : %s (%s:%d) -> %s" % (function_name, stream_type, stream_name, size, data_size, memory_name)
        stream_class=self.streams_map.stream_class(stream_type)
        stream = stream_class(stream_name, memory_name, size, data_size, self.debug)
        self.streams_map.add_stream(function_name, stream)
