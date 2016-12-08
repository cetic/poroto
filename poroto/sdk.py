class SDK:
    def __init__(self, debug):
        self.debug = debug

    def add_function_ports(self, function):
        pass

    def create_mem_wrapper(self, mem_type, name, data_type, size, init):
        raise Exception("No memory wrapper implemented")

    def generate_wrappers(self):
        raise Exception("Method not implemented")
