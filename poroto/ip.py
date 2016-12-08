from .modules import Template, Instance
from .common import get_bus_size, get_data_type
from .transform.attributes import get_extra_attr, set_extra_attr
from .pragma import PragmaHandler
from pycparser import c_ast
import re

class IPTemplate(Template):
    def __init__(self, name, decl, debug):
        Template.__init__(self, name, debug)
        self.decl = decl
        self.export = True

    def instanciate(self, instance_name, from_instance):
        return IPInstance(instance_name, from_instance, self.decl, self.debug)

class IPInstance(Instance):
    def __init__(self, instance_name, from_instance, fundecl, debug):
        Instance.__init__(self, debug)
        self.name = fundecl.type.declname
        self.from_instance=from_instance
        self.args = fundecl.args
        for arg in self.args.params:
            if isinstance(arg.type, c_ast.PtrDecl):
                self.system=True
            self.params[arg.name] = arg
        self.latency = get_extra_attr(fundecl, "latency", -1)
        if self.latency == -1:
            raise Exception("No latency defined for %s" % self.name)

    def generate(self, designer):
        print "generating %s" % (self.name)
        in_registers = []
        out_registers = []
        for arg in self.args.params:
            if arg.type.type.names[-1] == '&':
                continue
            in_registers.append((arg.name, get_bus_size(arg.type), get_data_type(arg.type)))
        for arg in self.args.params:
            if not arg.type.type.names[-1] == '&':
                continue
            out_registers.append((arg.name, get_bus_size(arg.type), get_data_type(arg.type)))
        self.converter.add_ip(self.name, self.latency, in_registers, out_registers)

class FilePragmaHandler(PragmaHandler):
    def __init__(self, designer, debug):
        self.designer = designer
        self.debug = debug
    def parse_pragma(self, node, tokens, next_stmt):
        if len(tokens) < 4:
            raise Exception("Invalid file pragma '%s'" % node.string)
        print "Adding file '%s' to '%s" % (tokens[3], tokens[2])
        self.designer.add_file(tokens[2], tokens[3])

class LatencyPragmaHandler(PragmaHandler):
    def parse_pragma(self, node, tokens, next_stmt):
        line = ' '.join(tokens[1:])
        m=re.match( r'latency\s+(\d+)', line)
        if not m:
            raise Exception("Invalid poroto latency pragma")
        if not isinstance(next_stmt, c_ast.Decl) or not isinstance(next_stmt.type, c_ast.FuncDecl):
            raise Exception("Latency pragma can only be applied on function declaration")
        set_extra_attr(next_stmt.type, 'latency', m.group(1))
