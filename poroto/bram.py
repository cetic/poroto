from .modules import Template, Instance

class BromTemplate(Template):
    def __init__(self, name, array_type, size, data_size, init, internal, mems_map, platform, debug):
        Template.__init__(self, name, debug)
        self.platform = platform
        self.mems_map = mems_map
        self.array_type = array_type
        self.size = size
        self.data_size = data_size
        self.init = init
        self.internal = internal

    def instanciate(self, instance_name, from_instance):
        memory = self.platform.create_mem('brom', self.name, self.array_type, self.size, self.init)
        if not self.internal:
            self.mems_map.add_memory(memory)
        return BromInstance(memory, self.debug)

class BramTemplate(Template):
    def __init__(self, name, array_type, size, data_size, mems_map, sdk, debug):
        Template.__init__(self, name, debug)
        self.sdk = sdk
        self.mems_map = mems_map
        self.array_type = array_type
        self.size = size
        self.data_size = data_size

    def instanciate(self, instance_name, from_instance):
        memory = self.sdk.create_mem_wrapper('bram', self.name, self.array_type, self.size, None)
        self.mems_map.add_memory(memory)
        return BramInstance(memory, self.debug)

class BromInstance(Instance):
    def __init__(self, memory, debug):
        Instance.__init__(self, debug)
        self.memory = memory

    def generate(self, designer):
        self.memory.generate(designer)

class BramInstance(Instance):
    def __init__(self, memory, debug):
        Instance.__init__(self, debug)
        self.memory = memory

    def generate(self, designer):
        self.memory.generate(designer)
