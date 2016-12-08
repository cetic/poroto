from .db import removeIntrinsics, add_intrinsic

intrinsics_map={}

def remove_all():
    removeIntrinsics()

def add_fp_add(latency, bitsize=32, name=None):
    if not name: name="fp_add%d" % bitsize
    in_ports=[["a", bitsize, "float"],
              ["b", bitsize, "float"]]
    out_ports=[["result", bitsize, "float"]]
    add_intrinsic(name, 'FP_ADD', latency, in_ports, out_ports)
    intrinsics_map[name]=1
    
def add_fp_sub(latency, bitsize=32, name=None):
    if not name: name="fp_sub%d" % bitsize
    in_ports=[["a", bitsize, "float"],
              ["b", bitsize, "float"]]
    out_ports=[["result", bitsize, "float"]]
    add_intrinsic(name, 'FP_SUB', latency, in_ports, out_ports)
    intrinsics_map[name]=1

def add_fp_mul(latency, bitsize=32, name=None):
    if not name: name="fp_mul%d" % bitsize
    in_ports=[["a", bitsize, "float"],
              ["b", bitsize, "float"]]
    out_ports=[["result", bitsize, "float"]]
    add_intrinsic(name, 'FP_MUL', latency, in_ports, out_ports)
    intrinsics_map[name]=1
    intrinsics_map[name]=1

def add_fp_div(latency, bitsize=32, name=None):
    if not name: name="fp_div%d" % bitsize
    in_ports=[["a", bitsize, "float"],
              ["b", bitsize, "float"]]
    out_ports=[["result", bitsize, "float"]]
    add_intrinsic(name, 'FP_DIV', latency, in_ports, out_ports)
    intrinsics_map[name]=1

def add_int_div(latency, bitsize=32, name=None):
    if not name: name="int_div%d" % bitsize
    in_ports=[["a", bitsize, "int"],
              ["b", bitsize, "int"]]
    out_ports=[["result", bitsize, "int"]]
    add_intrinsic(name, 'INT_DIV', latency, in_ports, out_ports)
    intrinsics_map[name]=1

def find_intrinsics_in(instance):
    source = open("gen/vhdl/%s.vhdl" % instance.name, 'r')
    used={}
    for line in source:
        for intrinsic in intrinsics_map.iterkeys():
            if ": %s port map (" % intrinsic in line:
                used[intrinsic]=1
    source.close()
    return used.keys()