import string
import os

from .common import load_template
from .config import gen_path
from .template import FileTemplate

bram_latency = 3

class InternalBramWrapperGenerator:
    latency = 1
    def __init__(self, debug):
        self.debug = debug
        self.wrapper_template = None
    def generate(self, wrapper, designer):
        if not self.wrapper_template:
            self.wrapper_template = FileTemplate('int_bram_get_wrapper.vhdl')
        keys={ 'WRAPPER_NAME': wrapper.name,
               'BROM_NAME': wrapper.mem_name + '_brom',
               'ADDR_LEN': str(wrapper.address_size),
               'DATA_SIZE': str(wrapper.data_size),
              }
        self.wrapper_template.set_keys(keys)
        self.wrapper_template.generate(os.path.join(gen_path, 'vhdl', "%s.vhdl" % wrapper.name))
        designer.add_file(gen_path, "%s.vhdl" % wrapper.name)
        return self.latency

class ExternalBramWrapperGenerator:
    def __init__(self, designer, debug):
        self.designer = designer
        self.debug = debug
        self.set_wrapper_template = None
        self.get_wrapper_template = None

    def generateWrapper(self, wrapper, template):
        if not self.set_wrapper_template:
            self.set_wrapper_template = load_template('ext_bram_set_wrapper.vhdl')
        if not self.get_wrapper_template:
            self.get_wrapper_template = load_template('ext_bram_get_wrapper.vhdl')
        out = open(os.path.join(gen_path, 'vhdl', "%s.vhdl" % wrapper.name), 'w' )
        for line in template:
            if '%%%WRAPPER_NAME%%%' in line:
                line = string.replace(line, '%%%WRAPPER_NAME%%%', wrapper.name)
            elif '%%%BRAM_NAME%%%' in line:
                line = string.replace(line, '%%%BRAM_NAME%%%', wrapper.mem_name)
            elif '%%%ADDR_WIDTH%%%' in line:
                line = string.replace(line, '%%%ADDR_WIDTH%%%', str(wrapper.stream_address_size))
            elif '%%%DATA_SIZE%%%' in line:
                line = string.replace(line, '%%%DATA_SIZE%%%', str(wrapper.data_size))
            elif '%%%EXT%%%' in line:
                line = string.replace(line, '%%%EXT%%%', 'SXT' if wrapper.data_sign else 'EXT')
            print >> out, line,
        out.close()
        self.designer.add_file(gen_path, "%s.vhdl" % wrapper.name)

    def generate(self, wrapper):
        if '_get' in wrapper.name:
            template = self.get_wrapper_template
        else:
            template = self.set_wrapper_template
        self.generateWrapper(wrapper, template)
        if '_get' in wrapper.name:
            self.converter.add_ip(wrapper.name, bram_latency,  [('address', wrapper.stream_address_size, 'int')], [('value', wrapper.data_size, 'int')])
        else:
            dummy_name='dummy_' + wrapper.mem_name
            self.converter.add_ip(wrapper.name, bram_latency,  [('address', wrapper.stream_address_size, 'int'), ('enable', 1, 'int'), ('value', wrapper.data_size, 'int')], [(dummy_name, 32, 'int')])
