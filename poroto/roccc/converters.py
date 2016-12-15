from pycparser import c_ast
from ..transform.attributes import set_extra_attr, get_extra_attr
from ..transform.variables import NameAllocator, create_simple_var
from ..transform.visitor import AstModifier
from copy import deepcopy

class InitConverter(AstModifier):
    def __init__(self, debug):
        AstModifier.__init__(self, debug)

    def visit_Decl(self, node):
        if node.init and self._currentFunc and not 'const' in node.quals and not isinstance(node.type, c_ast.ArrayDecl):
            self.insert_node_after(c_ast.Assignment('=', c_ast.ID(node.name), node.init), 'Compound')
            node.init = None
        self.generic_visit(node)

class InterLoopCode(AstModifier):
    def __init__(self, debug):
        AstModifier.__init__(self, debug)
        self.inner = 0
        self.inner_for = None
        self.inner_index = None
        self.inner_limit = None
        self.inner_begin_block = None
        self.inner_end_block = None
        self.begin = True
    def visit_Assignment(self, node):
        if self.inner_for:
            self.remove_node()
            if self.begin:
                if not self.inner_begin_block:
                    self.inner_begin_block = c_ast.Compound([])
                    code = c_ast.If(c_ast.BinaryOp("==", self.inner_index, c_ast.Constant('int', '0')), self.inner_begin_block, None)
                    self.inner_for.stmt.block_items.insert(0, code)
                self.inner_begin_block.block_items.append(node)
            else:
                if not self.inner_end_block:
                    self.inner_end_block = c_ast.Compound([])
                    code = c_ast.If(c_ast.BinaryOp("==", self.inner_index, c_ast.BinaryOp('-', self.inner_limit, c_ast.Constant('int', '1'))), self.inner_end_block, None)
                    self.inner_for.stmt.block_items.append(code)
                self.inner_end_block.block_items.append(node)
    def visit_For(self, node):
        if node == self.inner_for:
            self.begin = False
        inner_for=None
        for stmt in node.stmt.block_items:
            if isinstance(stmt, c_ast.Label):
                stmt = stmt.stmt
            if isinstance(stmt, c_ast.For):
                inner_for=stmt
        if inner_for:
            old_inner = self.inner_for
            old_index = self.inner_index
            old_limit = self.inner_limit
            old_begin_block = self.inner_begin_block
            old_end_block = self.inner_end_block
            old_begin = self.begin
            self.inner_for = inner_for
            self.inner_index = inner_for.init.lvalue
            self.inner_limit = inner_for.cond.right
            self.inner_block = None
            self.begin = True
            self.inner += 1
            self.visit_Compound(node.stmt)
            self.inner -= 1
            self.inner_for = old_inner
            self.inner_index = old_index
            self.inner_limit = old_limit
            self.inner_begin_block = old_begin_block
            self.inner_end_block = old_end_block
            self.begin = old_begin

class LogicalOpConverter(c_ast.NodeVisitor):
    def __init__(self, debug):
        self.debug = debug

    def visit_BinaryOp(self, node):
        if node.op == '&&':
            node.op = '&'
        elif node.op == '||':
            node.op = '|'
        self.generic_visit(node)

simplifierNameAllocator = NameAllocator()

class FunctionSimplifier(AstModifier):
    def __init__(self, debug):
        AstModifier.__init__(self, debug)
        self.functions = {}
        self.tmp_name = 'tmp'
    def createTmpName(self, name):
        full_name = simplifierNameAllocator.getTmpNameFor(self._currentFunc.decl.name, name)
        return c_ast.ID(full_name)
    def visit_Decl(self, node):
        if not isinstance(node.type, c_ast.FuncDecl): return
        func_decl = node.type
        if not isinstance(func_decl.type, c_ast.TypeDecl) or not isinstance(func_decl.type.type, c_ast.IdentifierType) or func_decl.type.type.names != ['void']:
            self.functions[node.name] = node
            return_type=func_decl.type
            #node.return_type = return_type
            set_extra_attr(node, 'return_type', func_decl.type)
            #update declname
            it=return_type
            while it is not None:
                if isinstance(it, c_ast.TypeDecl):
                    it.declname = 'return_of_the_jedi'
                    it = None
                else:
                    if hasattr(it, 'type'):
                        it = it.type
                    else:
                        it = None
            func_decl.type = c_ast.TypeDecl(node.name, [], c_ast.IdentifierType(['void']))
            result_type=deepcopy(return_type)
            result_type.type.names += '&'
            decl = create_simple_var(result_type, 'return_of_the_jedi', None)
            if func_decl.args is None:
                func_decl.args = c_ast.ParamList([])
            #Handle the int f(void) case
            if len(func_decl.args.params) == 1 \
              and isinstance(func_decl.args.params[0], c_ast.Typename) \
              and isinstance(func_decl.args.params[0].type.type, c_ast.IdentifierType) \
              and func_decl.args.params[0].type.type.names[0] == 'void':
                func_decl.args.params.pop()
            func_decl.args.params.append(decl)
    def visit_Return(self, node):
        if node.expr is not None:
            decl = c_ast.Assignment('=', c_ast.ID('return_of_the_jedi'), node.expr)
            self.insert_node_before(decl)
            node.expr = None
            if hasattr(self._currentFunc.decl, 'poroto_type'):
                return_type = self._currentFunc.decl.poroto_type.dereference()
                reference_type = c_ast.PtrDecl([], return_type.user_type_tree)
                reference_type.type.poroto_type = return_type
                poroto_type = types.PointerDescriptor(reference_type, None, None)
                decl.lvalue.poroto_type = poroto_type
    def visit_Assignment(self, node):
        if isinstance(node.rvalue, c_ast.FuncCall) and isinstance(node.rvalue.name, c_ast.ID) and node.rvalue.name.name in self.functions:
            func_decl = self.functions[node.rvalue.name.name]
            return_value = self.createTmpName(self.tmp_name)
            return_value_decl = create_simple_var(get_extra_attr(func_decl, 'return_type'), return_value, None)
            self.insert_node_before(return_value_decl)
            if node.rvalue.args is None:
                node.rvalue.args = c_ast.ExprList([])
            node.rvalue.args.exprs.append(return_value)
            self.insert_node_before(node.rvalue)
            if return_value_decl:
                node.rvalue = return_value
            else:
                self.remove_node()
            if hasattr(func_decl, 'poroto_type'):
                return_type = func_decl.poroto_type.dereference()
                if return_value_decl:
                    return_value_decl.poroto_type = return_type
                return_value.poroto_type = return_type
                reference_type = c_ast.PtrDecl([], c_ast.TypeDecl(return_value.name, [], return_type.user_type_tree))
                reference_type.type.poroto_type = return_type
                return_value.poroto_type = types.PointerDescriptor(reference_type, None, None)

class FunctionSignatureSimplifier(AstModifier):
    def __init__(self, debug):
        AstModifier.__init__(self, debug)
    def visit_Decl(self, node):
        if not isinstance(node.type, c_ast.FuncDecl): return
        func_decl = node.type
        set_extra_attr(node, 'orig_decl', deepcopy(node.type))
        for arg in func_decl.args.params:
            if isinstance(arg.type, c_ast.ArrayDecl):
                depth = 0
                inner_type = arg.type
                while isinstance(inner_type, c_ast.ArrayDecl):
                    depth += 1
                    inner_type = inner_type.type
                new_type=inner_type
                while depth > 0:
                    new_type=c_ast.PtrDecl([], new_type, arg.type.coord)
                    depth -= 1
                arg.type=new_type

class InstanciateInlineVar(AstModifier):
    def __init__(self, debug):
        AstModifier.__init__(self, debug)
        self.inline = {}

    def visit_ID(self, node):
        if node.name in self.inline:
            self.replace_expr(deepcopy(self.inline[node.name]))

    def visit_Decl(self, node):
        if not isinstance(node.type, c_ast.FuncDecl) and 'inline' in node.funcspec:
            self.remove_node('Compound')
            self.inline[node.name] = node.init
        self.generic_visit(node)

converters=[InitConverter, LogicalOpConverter, InterLoopCode, FunctionSimplifier, FunctionSignatureSimplifier, InstanciateInlineVar]
