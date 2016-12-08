from ..function import FunctionInstance
from ..transform.attributes import get_extra_attr, set_extra_attr
from ..config import src_path, gen_path, c_header, user_signals, create_fifo, create_stream, create_converted, validate_converted
from pycparser import c_ast, c_generator
import config
import tool
import db
import intrinsics
import os
import subprocess

class RocccFunctionInstance(FunctionInstance):
    def __init__(self, instance_name, template, from_instance, functions, platform, debug):
        FunctionInstance.__init__(self, instance_name, template, from_instance, functions, platform, debug)
        for arg in self.args.params:
            if isinstance(arg.type, c_ast.PtrDecl):
                self.system=True
        self.options=get_extra_attr(template.code, 'roccc_options', config.default_options)
        if not self.system:
            self.options.append('FullyUnroll')
        self.lo_options=get_extra_attr(template.code, 'roccc_lo_options', config.default_lo_options)
        self.timing_options=get_extra_attr(template.code, 'roccc_timing_options', config.default_timing_options)

    def define_ports(self, sdk):
        self.in_ports = db.get_module_in_ports(self.name)
        self.out_ports = db.get_module_out_ports(self.name)
        self.roccc_in_streams = db.get_module_in_streams(self.name)
        self.roccc_out_streams = db.get_module_out_streams(self.name)
        sdk.add_function_ports(self)
        if create_stream:
            for stream_name in self.roccc_in_streams:
                if stream_name not in self.streams_map:
                    raise Exception("Stream %s not defined in %s" % (stream_name, self.name))
            for stream_name in self.roccc_out_streams:
                if stream_name not in self.streams_map:
                    raise Exception("Stream %s not defined in %s" % (stream_name, self.name))

    def generate(self, designer):
        print "generating %s" % (self.name)
        filename = os.path.join(gen_path, "%s.c" % self.name)
        out = open( filename, 'w' )
        if c_header:
            print >> out, c_header
        print >> out, '#include "roccc-library.h"'
        generator = c_generator.CGenerator()
        generated = generator.visit(self.code)
        print >> out, generated
        out.close()
        if config.register:
            tool.invoke_roccc(self.name, gen_path, filename, self.options, self.lo_options, self.timing_options)
        tool.fix_module(self)
        if self.system:
            tool.fix_controllers(self)
        tool.add_signals(self, user_signals )
        designer.add_file(gen_path, "%s.vhdl" % self.name)
        designer.add_file(src_path, "input_bram_wrapper.vhdl")
        designer.add_file(src_path, "output_bram_wrapper.vhdl")
        designer.add_file(src_path, "ROCCChelper.vhdl")
        if self.system:
            designer.add_file(gen_path, "%s_InputController.vhdl" % self.name)
            designer.add_file(gen_path, "%s_OutputController.vhdl" % self.name)
            designer.add_file(src_path, "SynchInterfaceGeneric.vhdl")
            designer.add_file(src_path, "BurstAddressGeneric.vhdl")
            designer.add_file(src_path, "MicroFifo.vhdl")
        if create_fifo:
            fifo = self.platform.create_fifo()
            fifo.generate(designer)
        for intrinsic in intrinsics.find_intrinsics_in(self):
            print "Adding intrinsic %s" % intrinsic
            self.platform.add_intrinsic(designer, intrinsic)

    def printComponents(self, out):
        print >> out, "\tcomponent %s is" % self.name
        print >> out, "\tport ("
        print >> out, "\t\tclk : in std_logic;"
        print >> out, "\t\trst : in std_logic;"
        print >> out, "\t\tinputReady : in std_logic;"
        print >> out, "\t\toutputReady : out std_logic;"
        print >> out, "\t\tstall : in std_logic;"
        for stream in self.streams:
            for signal_def in stream.get_user_signals():
                print >> out, '\t\t%s' % signal_def
        for port in self.in_ports:
            if port.virtual: continue
            if port.bitwidth == 1:
                print >> out, "\t\t%s : in std_logic;" % port.vhdl_name
            else:
                print >> out, "\t\t%s : in std_logic_vector(%d-1 downto 0);" % (port.vhdl_name, port.bitwidth)
        for port in self.out_ports:
            if port.virtual: continue
            if port.bitwidth == 1:
                print >> out, "\t\t%s : out std_logic;" % port.vhdl_name
            else:
                print >> out, "\t\t%s : out std_logic_vector(%d-1 downto 0);" % (port.vhdl_name, port.bitwidth)
        print >> out, "\t\tdone : out std_logic"
        print >> out, "\t\t);"
        print >> out, "\tend component;"

    def printSignals(self, out):
        print >> out, "\tsignal %s_inputReady : std_logic := '0';" % self.name
        print >> out, "\tsignal %s_outputReady : std_logic;" % self.name
        print >> out, "\tsignal %s_rst : std_logic := '1';" % self.name
        print >> out, "\tsignal %s_stall : std_logic := '0';" % self.name
        print >> out, "\tsignal %s_done : std_logic;" % self.name
        for port in self.in_ports:
            if port.vhdl_name.endswith('Clk'): continue
            if port.bitwidth == 1:
                print >> out, "\tsignal %s_%s : std_logic := '0';" % (self.name, port.name)
            else:
                print >> out, "\tsignal %s_%s : std_logic_vector(%d-1 downto 0) := (others => '0');" % (self.name, port.name, port.bitwidth)
        for port in self.out_ports:
            if port.bitwidth == 1:
                print >> out, "\tsignal %s_%s : std_logic;" % (self.name, port.name)
            else:
                print >> out, "\tsignal %s_%s : std_logic_vector(%d-1 downto 0) := (others => '0');" % (self.name, port.name, port.bitwidth)
        for stream in self.streams:
            for signal_def in stream.get_temp_signals():
                print >> out, '\t%s' % signal_def
            print >> out

    def printPortMap(self, out, clock):
        for stream in self.streams:
            for line in stream.get_adapter_instance():
                print >> out, '\t%s' % line
            print >> out
        print >> out, "i_%s : %s" % (self.name, self.name)
        print >> out, "port map("
        print >> out, "\tclk\t\t=> %s," % clock
        print >> out, "\trst\t\t=> %s_rst," % self.name
        print >> out, "\tinputReady\t=> %s_inputReady," % self.name
        print >> out, "\toutputReady\t=> %s_outputReady," % self.name
        print >> out, "\tstall\t\t=> %s_stall," % self.name
        for stream in self.streams:
            for signal in stream.get_port_map():
                print >> out, '\t%s,' % signal
        for port in self.in_ports:
            if port.virtual: continue
            if port.vhdl_name.endswith('Clk'):
                arg = 'usr_clk'
            else:
                arg = "%s_%s" % (self.name, port.name)
            if port.bitwidth == 32 or port.bitwidth == 1:
                print >> out, "\t%s\t=> %s," % (port.vhdl_name, arg)
            else:
                print >> out, "\t%s\t=> %s(%d downto 0)," % (port.vhdl_name, arg, port.bitwidth-1)
        for port in self.out_ports:
            if port.virtual: continue
            arg = "%s_%s" % (self.name, port.name)
            if port.bitwidth == 32 or port.bitwidth == 1:
                print >> out, "\t%s\t=> %s," % (port.vhdl_name, arg)
            else:
                print >> out, "\t%s\t=> %s(%d downto 0)," % (port.vhdl_name, arg, port.bitwidth-1)
        print >> out, "\tdone\t\t=> %s_done" % self.name
        print >> out, ");"

    def validate(self):
        filename = os.path.join(gen_path, "%s.c" % self.name)
        if validate_converted:
            subprocess.call("g++ -I. -I$ROCCC_ROOT/LocalFiles -c %s -o /dev/null" % filename, shell=True)
        if not create_converted:
            os.unlink(filename)
