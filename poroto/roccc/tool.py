'''
Created on 11 oct. 2012

@author: ld
'''
import subprocess
import os.path
import re
import sys

from ..common import root_path
from . import config

from db import add_module, update_module, get_roccc_version

timing_list = [ 'AND', 'Add', 'Compare', 'Copy', 'MaxFanoutRegistered', 'Mult', 'Mux', 'OR', 'Shift', 'Sub', 'XOR', 'OperationsPerPipelineStage' ]

def invoke_add_module(module_name, latency, in_ports, out_ports):
    add_module(module_name, latency, in_ports, out_ports)
    module_filename = os.path.join(config.roccc_root, 'newComponent.ROCCC')
    module_file = open(module_filename, 'w')
    print >> module_file, module_name
    print >> module_file, latency
    for port in in_ports:
        (name, size, data_type) = port
        print >> module_file,  "%s IN %d %s" % (name, size, data_type)
    for port in out_ports:
        (name, size, data_type) = port
        print >> module_file,  "%s OUT %d %s" % (name, size, data_type)
    module_file.close()
    print "roccc < %s" % module_name
    subprocess.call("%s %s" % (os.path.join(root_path, 'scripts/add_module.sh'), module_filename), shell=True)

def invoke_roccc(name, path, filename, options, lo_options, timing_options):
    timing_info_file = open(os.path.join(path, '.ROCCC', '.timingInfo'), 'w')
    for (operation) in timing_list:
        if operation in timing_options:
            print >> timing_info_file, "%s %s" % (operation, str(timing_options[operation]))
    timing_info_file.close()
    module_id = update_module(name)
    ci = open(os.path.join(path, '.ROCCC', '.compileInfo'), 'w')
    print >> ci, module_id
    ci.close()
    options_filename = os.path.join(path, '.ROCCC', '%s.opt' % name)
    options_file = open(options_filename, 'w')
    for option in options:
        print >> options_file, option
    options_file.close()
    lo_options_filename = os.path.join(path, '.ROCCC', '.optlo')
    lo_options_file = open(lo_options_filename, 'w')
    for option in lo_options:
        print >> lo_options_file, option
    lo_options_file.close()
    debug_filename = os.path.join(path, '.ROCCC', '%s.debug' % name)
    debug_file = open(debug_filename, 'w')
    debug_file.close()
    preference_filename = os.path.join(path, '.ROCCC', '.preferenceFile')
    preference_file = open(preference_filename, 'w')
    print >> preference_file, "COMPILER_VERSION %s" % get_roccc_version()
    preference_file.close()
    print "roccc < %s" % filename
    print "Options:", options
    print "Low Options:", lo_options
    print "Timing Options:", timing_options
    subprocess.call("%s %s %s" % (os.path.join(root_path, 'scripts/roccc.sh'), name, filename), shell=True)
        
def fix_module(instance):
    os.rename("gen/vhdl/%s.vhdl" % instance.name, "gen/vhdl/%s_orig.vhdl" % instance.name)
    source = open("gen/vhdl/%s_orig.vhdl" % instance.name, 'r')
    dest = open("gen/vhdl/%s_tmp.vhdl"% instance.name, 'w')
    skip_line=0
    for line in source:
        if line == "has_had_input <= '0' when (rst = '1') else\n":
            print >> dest, """
process(clk, rst)
begin
  if (rst = '1') then
    has_had_input <= '0';
  elsif( clk'event and clk = '1' ) then
    if inputReady = '1' then
        has_had_input <= '1';
    end if;
  end if;
end process;
"""
            skip_line=2
        elif skip_line == 0:
            print >> dest, line,
        elif skip_line > 0:
            skip_line -= 1
    source.close()
    dest.close()
    os.rename("gen/vhdl/%s_tmp.vhdl" % instance.name, "gen/vhdl/%s.vhdl" % instance.name)

microfifo_component="""component MicroFifo is
generic (
    DATA_WIDTH : integer := 0;
    ADDRESS_WIDTH : integer := 0;
    ALMOST_FULL_COUNT : integer := 0;
    ALMOST_EMPTY_COUNT : integer := 0
    );
port (
    clk : in STD_LOGIC;
    rst : in STD_LOGIC;
    data_in : in STD_LOGIC_VECTOR(DATA_WIDTH-1 downto 0);
    valid_in : in STD_LOGIC;
    full_out : out STD_LOGIC;
    data_out : out STD_LOGIC_VECTOR(DATA_WIDTH-1 downto 0);
    read_enable_in : in STD_LOGIC;
    empty_out : out STD_LOGIC
    );
end component;"""

def fix_microfifo(source):
    dest = []
    skip_line=0
    component_added=False
    for line in source:
        if 'component MicroFifo' in line:
            skip_line=17
            if not component_added:
                dest.append(microfifo_component)
                component_added=True
        elif skip_line == 0:
            if 'MicroFifo' in line:
                line = re.sub('MicroFifo\d+', 'MicroFifo', line)
            dest.append(line)
        elif skip_line > 0:
            skip_line -= 1
    return dest
def fix_bramfifo(source):
    dest = []
    add_generic=False
    for line in source:
        if add_generic:
            dest.append(line)
            dest.append("\tDATA_SIZE : integer := 32;\n")
            add_generic=False
        elif 'component InferredBRAMFifo' in line:
            line = re.sub('InferredBRAMFifo(\d+)', 'InferredBRAMFifo', line)
            dest.append(line)
            add_generic=True
        elif 'InferredBRAMFifo' in line:
            line = re.sub('InferredBRAMFifo(\d+)\s*generic\s+map\s*\(', 'InferredBRAMFifo generic map(DATA_SIZE => \\1, ', line)
            dest.append(line)
        else:
            dest.append(line)
    return dest

def fix_controllers(instance):
    os.rename("gen/vhdl/%s_OutputController.vhdl" % instance.name, "gen/vhdl/%s_OutputController_orig.vhdl" % instance.name)
    source_file = open("gen/vhdl/%s_OutputController_orig.vhdl" % instance.name, 'r')
    source = source_file.readlines()
    source_file.close()
    source = fix_microfifo(source)
    source = fix_bramfifo(source)
    dest_file = open("gen/vhdl/%s_OutputController.vhdl"% instance.name, 'w')
    dest_file.writelines(source)
    dest_file.close()

    os.rename("gen/vhdl/%s_InputController.vhdl" % instance.name, "gen/vhdl/%s_InputController_orig.vhdl" % instance.name)
    source_file = open("gen/vhdl/%s_InputController_orig.vhdl" % instance.name, 'r')
    source = source_file.readlines()
    source_file.close()
    source = fix_microfifo(source)
    source = fix_bramfifo(source)
    dest_file = open("gen/vhdl/%s_InputController.vhdl"% instance.name, 'w')
    dest_file.writelines(source)
    dest_file.close()

def add_signals(instance, signals):
    source = open("gen/vhdl/%s.vhdl" % instance.name, 'r')
    dest = open("gen/vhdl/%s_tmp.vhdl"% instance.name, 'w')
    current_component=None
    for line in source:
        if current_component:
            print >> dest, line,
            for item in signals[current_component]:
                signals_def = item.get_user_signals()
                for signal_def in signals_def:
                    print >> dest, '\t', signal_def
            current_component=None
        else:
            print_line = True
            for component_name in signals:
                m = re.match( r'^(.+): %s port map \((.+)\) ;$' % component_name, line)
                if m:
                    print "*** Found portmap %s" % component_name
                    port_map_text=''
                    for item in signals[component_name]:
                        port_map = item.get_port_map()
                        if len(port_map) > 0:
                            port_map_text = port_map_text + ', '.join(port_map) + ', '
                    print >> dest, "%s: %s port map(%s%s);" % (m.group(1), component_name, port_map_text, m.group(2))
                    print_line = False                    
                    break
                elif line == 'entity %s is\n' % component_name:
                    print "*** Found entity %s" % component_name
                    current_component = component_name
                    break
                elif line == 'component %s is\n' % component_name:
                    print "*** Found component %s" % component_name
                    current_component = component_name
                    break
            if print_line:
                print >> dest, line,
    dest.close()
    source.close()
    os.rename("gen/vhdl/%s_tmp.vhdl" % instance.name, "gen/vhdl/%s.vhdl" % instance.name)
