import os
import re
import math
import struct
import config

root_path=os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

def mkdir_safe(name):
    try:
        os.makedirs(name)
    except OSError:
        pass

def get_path_for(file_path, file_name, top_dir=config.vhdl_path):
    if config.platform_vendor:
        if config.platform:
            if config.target:
                path=os.path.join(root_path, top_dir, config.platform_vendor, config.platform, config.target, file_path, file_name)
                if os.path.exists(path): return path
            path=os.path.join(root_path, top_dir, config.platform_vendor, config.platform, file_path, file_name)
            if os.path.exists(path): return path
        path=os.path.join(root_path, top_dir, config.platform_vendor, file_path, file_name)
        if os.path.exists(path): return path
    if config.device_vendor:
        if config.device:
            path=os.path.join(root_path, top_dir, config.device_vendor, config.device, file_path, file_name)
            if os.path.exists(path): return path
        path=os.path.join(root_path, top_dir, config.device_vendor, file_path, file_name)
        if os.path.exists(path): return path
    if config.sdk:
        if config.platform:
            if config.target:
                path=os.path.join(root_path, top_dir, config.sdk, config.platform, config.target, file_path, file_name)
                if os.path.exists(path): return path
            path=os.path.join(root_path, top_dir, config.sdk, config.platform, file_path, file_name)
            if os.path.exists(path): return path
        path=os.path.join(root_path, top_dir, config.sdk, file_path, file_name)
        if os.path.exists(path): return path
    path=os.path.join(root_path, top_dir, file_path, file_name)
    if os.path.exists(path): return path
    return None

def load_template(file_name, top_dir=config.vhdl_path):
    array = []
    template_file = open(get_path_for(config.templates_path, file_name, top_dir), 'r' )
    for line in template_file:
        array.append(line)
    template_file.close()
    return array

def get_bus_size(arg_type):
    if not isinstance(arg_type, str):
        arg_type = ' '.join(arg_type.type.names)
    m=re.match( r'ROCCC_u?int(\d+)$', arg_type)
    if m:
        return int(m.group(1))
    else:
        return 32

def get_bus_sign(arg_type):
    if not isinstance(arg_type, str):
        arg_type = ' '.join(arg_type.type.names)
    m=re.match( r'ROCCC_uint\d+$', arg_type)
    if m:
        return False
    else:
        return True

def get_bit_width(size):
    return int(math.ceil(math.log(size, 2)))

def is_integer(arg_type):
    if not isinstance(arg_type, str):
        arg_type = ' '.join(arg_type.type.names)
    if arg_type == "int" or arg_type == "unsigned type":
        return True
    m=re.match( r'ROCCC_u?int(\d+)$', arg_type)
    if m:
        return True
    else:
        return False
    
def get_data_type(arg_type):
    if not isinstance(arg_type, str):
        if arg_type.type.names[-1] == '&':
            arg_type = ' '.join(arg_type.type.names[0:-1])
        else:
            arg_type = ' '.join(arg_type.type.names)
    if arg_type == "int" or arg_type == "unsigned type":
        return 'int'
    m=re.match( r'ROCCC_u?int(\d+)$', arg_type)
    if m:
        return 'int'
    if arg_type == "float":
        return 'float'
    print "Type '%s' unknown, returning 'int'" % arg_type
    return 'int'

def convert(data_type, value):
    if is_integer(data_type):
        return value
    else:
        x=struct.unpack('<I', struct.pack('<f', value))
        return x[0]

def convert_format_hex(data_type, value, width=32):
    format_str='0%dX' % int((width + 3) / 4)
    return 'X"%s"' % format(convert(data_type, value), format_str)

def convert_format_bin(data_type, value, width=32):
    format_str='0%db' % width
    string=format(convert(data_type, value), format_str)
    return '"%s"' % string
