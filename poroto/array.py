from pycparser import c_ast
from copy import deepcopy
from poroto.common import get_bus_size, get_bus_sign
from poroto.bram import BramTemplate, BromTemplate
from transform.attributes import get_extra_attr
from transform.visitor import AstModifier
from poroto.common import get_bit_width
from .modules import Template, Instance
from .pragma import PragmaHandler
from .transform.attributes import get_extra_attr, set_extra_attr
from .bram_wrapper import ExternalBramWrapperGenerator, InternalBramWrapperGenerator

class ArrayRefConverter(AstModifier):
    def __init__(self, debug):
        AstModifier.__init__(self, debug)
        self.id = 0;

    def get_array_name(self, node):
        it = node.name
        while not isinstance(it, c_ast.ID):
            it = it.name
        return it.name
    def visit_Assignment(self, node):
        if isinstance(node.rvalue, c_ast.ArrayRef) and self.get_array_name(node.rvalue)+'_get' in self.registry.function_templates:
            if self.debug:
                print "Converting array reference %s" % self.get_array_name(node.rvalue)
            self.remove_node('Compound')
            decl = c_ast.FuncCall(c_ast.ID(self.get_array_name(node.rvalue)+'_get'), c_ast.ExprList([node.rvalue.subscript, node.lvalue]))
            self.insert_node_after(decl, 'Compound')
        elif isinstance(node.rvalue, c_ast.ArrayRef) and self.get_array_name(node.rvalue) in self.registry.function_templates:
            if self.debug:
                print "Converting array reference %s" % self.get_array_name(node.rvalue)
            self.remove_node('Compound')
            decl = c_ast.FuncCall(c_ast.ID(self.get_array_name(node.rvalue)), c_ast.ExprList([node.rvalue.subscript, node.lvalue]))
            self.insert_node_after(decl, 'Compound')
        elif isinstance(node.lvalue, c_ast.ArrayRef) and self.get_array_name(node.lvalue)+'_set' in self.registry.function_templates:
            if self.debug:
                print "Converting array assignment %s" % self.get_array_name(node.lvalue)
            self.remove_node('Compound')
            template = self.registry.function_templates[self.get_array_name(node.lvalue)+'_set']
            dummy_name='dummy_%d' % self.id
            self.id += 1
            decl=c_ast.Decl('',
                           [],
                           [],
                           [],
                           c_ast.TypeDecl(dummy_name, [], c_ast.IdentifierType(template.array_type.split())),
                           None,
                           None)
            self.insert_node_after(decl, 'Compound')
            decl = c_ast.FuncCall(c_ast.ID(self.get_array_name(node.lvalue)+'_set'), c_ast.ExprList([node.lvalue.subscript, c_ast.Constant('int', '1'), node.rvalue, c_ast.ID(dummy_name)]))
            self.insert_node_after(decl, 'Compound')

class EmbeddedArrayRefConverter(AstModifier):
    tmp_array_id = 0

    def get_array_name(self, node):
        it = node.name
        while not isinstance(it, c_ast.ID):
            it = it.name
        return it.name
    def visit_ArrayRef(self, node):
        if self.get_array_name(node)+'_get' in self.registry.function_templates:
            template=self.registry.function_templates[self.get_array_name(node)+'_get']
            if self.debug:
                print "Converting embedded array reference %s" % self.get_array_name(node)
            tmp_name=self.get_array_name(node)+'_result_%d' % self.tmp_array_id
            self.tmp_array_id += 1
            decl=c_ast.Decl('',
                           [],
                           [],
                           [],
                           c_ast.TypeDecl(tmp_name, [], c_ast.IdentifierType(template.array_type.split())),
                           None,
                           None)
            self.insert_node_before(decl, 'Compound')
            self.replace_expr(c_ast.ID(tmp_name))
            decl = c_ast.FuncCall(c_ast.ID(self.get_array_name(node)+'_get'), c_ast.ExprList([node.subscript, c_ast.ID(tmp_name)]))
            self.insert_node_before(decl, 'Compound')

class ArrayParser(AstModifier):
    def __init__(self, debug):
        AstModifier.__init__(self, debug)
        self.in_function = False

    def create(self, mem_name, mem_type, mem_size, mem_init):
        if not mem_size:
            raise Exception("Could not find size of %d" % mem_name)
        stream_address_size=get_bit_width(mem_size)
        if self.debug:
            print "Found array %s" % mem_name
        decl_get_name = mem_name+'_get'
        decl_set_name = mem_name+'_set'
        out_type = c_ast.IdentifierType(deepcopy(mem_type.type.names))
        out_type.names += '&'
        data_size=get_bus_size(mem_type)
        data_sign=get_bus_sign(mem_type)
        if not mem_init:
            out_type = c_ast.IdentifierType(deepcopy(mem_type.type.names))
            dummy_name='dummy_' + mem_name
        array_type=' '.join(mem_type.type.names)
        if mem_init:
            self.registry.addTemplateToRegistry(BromTemplate(mem_name, array_type, mem_size, data_size, mem_init, True, self.mems_map, self.platform, self.debug))
            self.registry.addTemplateToRegistry(InternalArrayWrapperTemplate(decl_get_name, array_type, mem_size, stream_address_size, data_size, data_sign, mem_name, self.registry, self.debug))
        else:
            internal = False
            self.registry.addTemplateToRegistry(BramTemplate(mem_name, array_type, mem_size, data_size, self.mems_map, self.platform, self.debug))
            self.registry.addTemplateToRegistry(ExternalArrayWrapperTemplate(decl_get_name, array_type, mem_size, stream_address_size, data_size, data_sign, mem_name, self.streams_map, self.debug))
            self.registry.addTemplateToRegistry(ExternalArrayWrapperTemplate(decl_set_name, array_type, mem_size, stream_address_size, data_size, data_sign, mem_name, self.streams_map, self.debug))

    def visit_FuncDef(self, node):
        self.in_function = True
        self.generic_visit(node)
        self.in_function = False

    def visit_Decl(self, node):
        if not isinstance(node.type, c_ast.ArrayDecl):
            return
        if not get_extra_attr(node, 'convert_array', False):
            return
        if node.init:
            size = len(node.init.exprs)
            self.create(node.name, node.type.type, size, node.init)
        else:
            size = int(node.type.dim.value)
            self.create(node.name, node.type.type, size, None)
        self.remove_node()
        #self.insert_node_after(decl_get, 'FileAST')
        #if not node.init:
        #    self.insert_node_after(decl_set, 'FileAST')

class ExternalArrayWrapperTemplate(Template):
    def __init__(self, name, array_type, size, stream_address_size, data_size, data_sign, mem_name, streams_map, debug):
        Template.__init__(self, name, debug)
        self.array_type = array_type
        self.size = size
        self.stream_address_size=stream_address_size
        self.data_size = data_size
        self.data_sign = data_sign
        self.mem_name = mem_name
        self.streams_map = streams_map

    def instanciate(self, instance_name, from_instance):
        instance = ExternalArrayWrapperInstance(instance_name, self.mem_name, self.size, self.stream_address_size, self.data_size, self.data_sign, self.debug)
        mem_stream = self.streams_map.get_stream_info(from_instance.name, self.mem_name)
        if not mem_stream:
            raise Exception("Could not find stream for %s in %s" % (self.mem_name, from_instance.name))
        if '_get' in self.name:
            stream_class = self.streams_map.stream_class('internal_bram_get')
            bram_stream = stream_class(self.mem_name, mem_stream.memory_name, mem_stream.size, self.data_size, mem_stream, self.debug)
        elif '_set' in self.name:
            stream_class = self.streams_map.stream_class('internal_bram_set')
            bram_stream = stream_class(self.mem_name, mem_stream.memory_name, mem_stream.size, self.data_size, mem_stream, self.debug)
        instance.add_stream(bram_stream)
        return instance

    def check_usage(self, ref_count):
        if self.nb_instances > 1 or ref_count > 1:
            raise Exception("Too many instances of %s" % self.name)

class InternalArrayWrapperTemplate(Template):
    def __init__(self, name, array_type, size, stream_address_size, data_size, data_sign, mem_name, functions, debug):
        Template.__init__(self, name, debug)
        self.array_type = array_type
        self.size = size
        self.stream_address_size=stream_address_size
        self.data_size = data_size
        self.data_sign = data_sign
        self.mem_name = mem_name
        functions.register_manual_reference(name, mem_name)

    def instanciate(self, instance_name, from_instance):
        instance = InternalArrayWrapperInstance(instance_name, self.mem_name, self.size, self.stream_address_size, self.data_size, self.data_sign, self.debug)
        return instance

    def check_usage(self, ref_count):
        if self.nb_instances > 1 or ref_count > 1:
            raise Exception("Too many instances of %s" % self.name)

class ExternalArrayWrapperInstance(Instance):
    def __init__(self, instance_name, mem_name, size, stream_address_size, data_size, data_sign, debug):
        Instance.__init__(self, debug)
        self.mem_name=mem_name
        self.size = size
        self.stream_address_size=stream_address_size
        self.data_size = data_size
        self.data_sign = data_sign
        self.name = instance_name

    def generate(self, designer):
        array_converter = ExternalBramWrapperGenerator(designer, self.debug)
        array_converter.generate(self)

class InternalArrayWrapperInstance(Instance):
    def __init__(self, instance_name, mem_name, size, address_size, data_size, data_sign, debug):
        Instance.__init__(self, debug)
        self.name = instance_name
        self.mem_name=mem_name
        self.size = size
        self.address_size=address_size
        self.data_size = data_size
        self.data_sign = data_sign

    def generate(self, designer):
        array_converter = InternalBramWrapperGenerator(designer, self.debug)
        array_converter.generate(self)
        self.converter.add_ip(self.name, array_converter.latency,  [('address', self.address_size, 'int')], [('value', self.data_size, 'int')])

class ArrayPragmaHandler(PragmaHandler):
    def parse_pragma(self, node, tokens, next_stmt):
        line = ' '.join(tokens[2:])
        if line == "brom":
            convert_array=True
            internal_array=True
        elif line == "lut":
            convert_array=False
            internal_array=True
        else:
            raise Exception("Unknown poroto array pragma")
        if not isinstance(next_stmt, c_ast.Decl) or not isinstance(next_stmt.type, c_ast.ArrayDecl):
            raise Exception("Array pragma can only be applied on array definition")
        set_extra_attr(next_stmt, 'convert_array', convert_array)
        set_extra_attr(next_stmt, 'internal_array', internal_array)

def init(platform, converter, functions, mems_map, streams_map):
    ArrayParser.platform = platform
    ArrayParser.registry = functions
    ArrayParser.mems_map = mems_map
    ArrayParser.streams_map = streams_map
    ArrayRefConverter.registry = functions
    EmbeddedArrayRefConverter.registry = functions
    InternalArrayWrapperInstance.converter = converter
    ExternalBramWrapperGenerator.converter = converter
converters=[ArrayParser, ArrayRefConverter, EmbeddedArrayRefConverter]