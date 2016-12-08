class Register:
    def __init__(self, block, name, size, offset, direction, data_type):
        self.name = block + '_' + name
        self.short_name = name
        self.size = size
        self.offset = offset
        self.type = direction
        self.data_type = data_type

class RegisterMap:
    def __init__(self, debug):
        self.debug = debug
        self.last_in_register_offset=0
        self.last_out_register_offset=2**(16-1)
        self.in_registers = {}
        self.in_registers_list = []
        self.out_registers = {}
        self.out_registers_list = []
        self.block_in_registers = {}
        self.block_out_registers = {}
        self.blocks_list = []
        self.register_size = 4

    def set_register_size(self, size):
        self.register_size = size

    def add_in_register(self, block, name, size=32, data_type='int'):
        register = Register(block, name, size, self.last_in_register_offset, 'in', data_type)
        if self.debug: print "Registering in register %s" % register.name
        if register.name in self.in_registers:
            raise Exception("In-register %s exists already" % register.name)
        self.in_registers[register.name] = register
        self.in_registers_list.append(register)
        if block not in self.block_in_registers:
            if block not in self.blocks_list:
                self.blocks_list.append(block)
            self.block_in_registers[block] = []
        self.block_in_registers[block].append(register)
        self.last_in_register_offset += self.register_size
        return register.offset

    def add_out_register(self, block, name, size=32, data_type='int'):
        register = Register(block, name, size, self.last_out_register_offset, 'out', data_type)
        if self.debug: print "Registering out register %s" % register.name
        if register.name in self.out_registers:
            raise Exception("Out-register %s exists already" % register.name)
        self.out_registers[register.name] = register
        self.out_registers_list.append(register)
        if block not in self.block_out_registers:
            if block not in self.blocks_list:
                self.blocks_list.append(block)
            self.block_out_registers[block] = []
        self.block_out_registers[block].append(register)
        self.last_out_register_offset += self.register_size
        return register.offset
    
    def in_register_address(self, name):
        return self.in_registers[name]
    
    def out_register_address(self, name):
        return self.out_registers[name]

    def add_function(self, instance):
        self.add_in_register(instance.name, 'rst', 1)
        for port in instance.in_ports:
            if not port.register: continue
            if port.internal: continue
            self.add_in_register(instance.name, port.name, port.bitwidth, port.data_type)
        self.add_out_register(instance.name, 'resultReady', 1)
        for port in instance.out_ports:
            if not port.register: continue
            if port.internal: continue
            if not port.name in instance.params: continue
            self.add_out_register(instance.name, port.name, port.bitwidth, port.data_type)

