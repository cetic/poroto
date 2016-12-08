class Port:
    def __init__(self, name, register, vhdl_name, bitwidth=32, data_type='int', internal=False, virtual=False):
        self.name=name
        self.register=register
        self.vhdl_name=vhdl_name
        self.bitwidth=bitwidth
        self.data_type=str(data_type)
        self.internal=internal
        self.virtual=virtual
