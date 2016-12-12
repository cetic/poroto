from .modules import Template, Instance
from .transform.visitor import AstModifier
from .ip import IPTemplate
from pycparser import c_ast
from copy import deepcopy

function_instance_generator = None

class InstanciateInline(AstModifier):
    def __init__(self, args_map, debug):
        AstModifier.__init__(self, debug)
        self.args_map = args_map

    def visit_ID(self, node):
        if node.name in self.args_map:
            self.replace_expr(deepcopy(self.args_map[node.name]))

class ReplaceReturn(AstModifier):
    def __init__(self, name, debug):
        AstModifier.__init__(self, debug)
        self.name = name
    def visit_Return(self, node):
        self.replace_node(c_ast.Assignment('=', c_ast.ID(self.name), node.expr), 'Compound')

tmp_id=0

class InlineFunctionCall(AstModifier):
    def __init__(self, functions, debug):
        AstModifier.__init__(self)
        self.functions = functions
        self.debug = debug
        
    def visit_FuncCall(self, node):
        global tmp_id
        template=None
        if node.name.name in self.functions.function_templates:
            template = self.functions.function_templates[node.name.name]
        if template and template.inline:
            if self.debug: print "Inlining function %s" % node.name.name
            if template.inline_return:
                name = 'poroto_tmp_%d' % tmp_id
                tmp_id += 1
                return_type = deepcopy(template.inline_return)
                return_type.declname = name
                self.insert_node_before( c_ast.Decl(name,
                      [],
                      [],
                      [],
                      return_type,
                      None,
                      None), 'Compound')
                self.insert_node_before(template.instanciate_inline(node, name), 'Compound')
                self.replace_expr(c_ast.ID(name))
            else:
                self.replace_node(template.instanciate_inline(node), 'Compound')
        self.generic_visit(node)

class FunctionTemplate(Template):
    def __init__(self, name, code, inline, functions, platform, debug):
        Template.__init__(self, name, debug)
        self.code = code
        self.inline = inline
        self.functions=functions
        self.platform = platform
        self.export = True
        if self.inline:
            if self.code.decl.type.type.type.names[0] != 'void':
                self.inline_return = self.code.decl.type.type
            else:
                self.inline_return = None
    
    def instanciate(self, instance_name, from_instance):
        return function_instance_generator(instance_name, self, from_instance, self.functions, self.platform, self.debug)

    def instanciate_inline(self, call_node, return_name=None):
        body = deepcopy(self.code.body)
        args_map = {}
        for i, arg in enumerate(call_node.args.exprs):
            args_map[self.code.decl.type.args.params[i].name] = arg
        v = InstanciateInline(args_map, self.debug)
        v.visit(body)
        v = ReplaceReturn(return_name, self.debug)
        v.visit(body)
        v = InlineFunctionCall(self.functions, self.debug)
        v.visit(body)
        return body

class FuncCallUpdater(c_ast.NodeVisitor):
    def __init__(self, template_name, instance_name, debug):
        self.template_name = template_name
        self.instance_name = instance_name
        self.debug = debug

    def visit_FuncCall(self, node):
        if node.name.name == self.template_name:
            node.name.name = self.instance_name

class FunctionInstance(Instance):
    def __init__(self, instance_name, template, from_instance, functions, platform, debug):
        Instance.__init__(self, debug)
        self.template=template
        self.from_instance=from_instance
        self.platform=platform
        self.code = deepcopy(template.code)
        self.code.decl.name = instance_name
        self.code.decl.type.type.declname = instance_name
        self.name = self.code.decl.name
        self.args = self.code.decl.type.args
        self.decl = self.code.decl
        for arg in self.args.params:
            self.params[arg.name] = arg
        v = InlineFunctionCall(functions, self.debug)
        v.visit(self.code.body)

    def define_ports(self, sdk):
        pass

    def update_code(self):
        FuncCallUpdater(self.template.name, self.name, self.debug).visit(self.code)

class FunctionCallVisitor(AstModifier):
    def __init__(self, functions, current_function, debug):
        AstModifier.__init__(self)
        self.functions = functions
        self.current_function = current_function
        self.debug = debug

    def visit_FuncCall(self, node):
        if self.debug: print "Detected function call %s" % node.name.name
        template=None
        if node.name.name in self.functions.function_templates:
            template = self.functions.function_templates[node.name.name]
        if template and template.inline:
#            if self.debug: print "Inlining function %s" % node.name.name
#            if template.inline_return:
#                name = 'poroto_tmp_%d' % FunctionCallVisitor.tmp_id
#                FunctionCallVisitor.tmp_id += 1
#                return_type = deepcopy(template.inline_return)
#                return_type.declname = name
#                self.insert_node_before( c_ast.Decl(name,
#                      [],
#                      [],
#                      [],
#                      return_type,
#                      None,
#                      None), 'Compound')
#                self.insert_node_before(template.instanciate_inline(node, name), 'Compound')
#                self.replace_expr(c_ast.ID(name))
#            else:
#                self.replace_node(template.instanciate_inline(node), 'Compound')
            self.functions.clone_reference(self.current_function, node.name.name)
        else:
            self.functions.register_reference(self.current_function, node.name.name)
        self.generic_visit(node)

class FunctionParser(c_ast.NodeVisitor):
    def __init__(self, registry, platform, debug):
        c_ast.NodeVisitor.__init__(self)
        self.registry = registry
        self.platform = platform
        self.debug= debug
        self._current_function = None

    def visit_FuncDecl(self, node):
        if self._current_function:
            #We are in a function definition
            return
        if node.type.declname in self.registry.function_templates:
            #function already registered, maybe as Array
            return
        if self.debug: print "Detected function declaration %s" % node.type.declname
        self.registry.addTemplateToRegistry(IPTemplate(node.type.declname, node, self.debug))

    def visit_FuncDef(self, node):
        inline = 'inline' in node.decl.funcspec
        if self.debug:
            if inline: print "Detected inline function %s" % node.decl.name
            else: print "Detected function %s" % node.decl.name
        self._current_function = node
        self.registry.addTemplateToRegistry(FunctionTemplate(node.decl.name, node, inline, self.registry, self.platform, self.debug))
        v = FunctionCallVisitor(self.registry, self._current_function.decl.name, self.debug)
        v.visit(node)
        self._current_function = None
