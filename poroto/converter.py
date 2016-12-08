class Converter():
    def __init__(self, debug):
        self.debug = debug

    @classmethod
    def register_arguments(cls, arg_parser):
        pass

    @classmethod
    def parse_arguments(cls, args):
        pass

    def init(self, pragma_registry):
        pass

    def first_pass_validators(self):
        return []
    
    def second_pass_validators(self):
        return []
    
    def converters(self):
        return []

    def add_ip(self, name, latency, in_ports, out_ports):
        pass
