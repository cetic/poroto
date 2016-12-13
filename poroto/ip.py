from .modules import Template, Instance
from .common import get_bus_size, get_data_type
from .transform.attributes import get_extra_attr, set_extra_attr
from .pragma import PragmaHandler
from .config import gen_path, ipcore_path
from .template import FileTemplate
from pycparser import c_ast
import re
import os

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
        self.files = get_extra_attr(fundecl, "files", [])
        self.templates = get_extra_attr(fundecl, "templates", [])

    def generate(self, designer):
        print "generating %s" % (self.name)
        for entry in self.files:
            print "Adding file '%s' to '%s" % (entry[1], entry[0])
            designer.add_file(entry[0], entry[1])
        for entry in self.templates:
            print "Adding template '%s' to '%s" % (entry[1], entry[0])
            if entry[0] == ipcore_path:
                root=os.path.splitext(entry[1])[0]
                FileTemplate(entry[1]).generate(gen_path, entry[0], root, entry[1])
                designer.add_file(entry[0], os.path.join(root, entry[1]))
            else:
                FileTemplate(entry[1]).generate(gen_path, entry[0], entry[1])
                designer.add_file(entry[0], entry[1])
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
    def parse_pragma(self, node, tokens, next_stmt):
        if len(tokens) < 4:
            raise Exception("Invalid file pragma '%s'" % node.string)
        files = get_extra_attr(next_stmt.type, "files", [])
        files.append([tokens[2], tokens[3]])
        set_extra_attr(next_stmt.type, 'files', files)

class TemplatePragmaHandler(PragmaHandler):
    def parse_pragma(self, node, tokens, next_stmt):
        if len(tokens) < 4:
            raise Exception("Invalid template pragma '%s'" % node.string)
        files = get_extra_attr(next_stmt.type, "templates", [])
        files.append([tokens[2], tokens[3]])
        set_extra_attr(next_stmt.type, 'templates', files)

class LatencyPragmaHandler(PragmaHandler):
    def parse_pragma(self, node, tokens, next_stmt):
        line = ' '.join(tokens[1:])
        m=re.match( r'latency\s+(\d+)', line)
        if not m:
            raise Exception("Invalid poroto latency pragma")
        if not isinstance(next_stmt, c_ast.Decl) or not isinstance(next_stmt.type, c_ast.FuncDecl):
            raise Exception("Latency pragma can only be applied on function declaration")
        set_extra_attr(next_stmt.type, 'latency', m.group(1))
