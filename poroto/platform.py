class Platform:
    def __init__(self, designer, debug):
        self.designer = designer
        self.debug = debug

    def generate_wrappers(self):
        raise Exception("Method not implemented")

    def create_mem(self, mem_type, name, data_type, size, init):
        raise Exception("Method not implemented")

    def create_mem_from(self, mem_type, memory):
        return self.create_mem(mem_type, memory.name, memory.data_type, memory.size, memory.init)

    def create_fifo(self):
        raise Exception("Method not implemented")

    def add_intrinsic(self, designer, intrinsic):
        raise Exception("Method not implemented")

    def get_keys(self):
        return {}
