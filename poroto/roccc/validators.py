from pycparser import c_ast

class IDValidator(c_ast.NodeVisitor):
    def __init__(self, debug):
        c_ast.NodeVisitor.__init__(self)
        self.debug = debug

    def visit_ID(self, node):
        if 'index' in node.name:
            raise Exception("'index' found in identifier %s" % node.name)
        if node.name.startswith('_'):
            raise Exception("identifier %s can not start with '_'" % node.name)

class FuncValidator(c_ast.NodeVisitor):
    def __init__(self, debug):
        c_ast.NodeVisitor.__init__(self)
        self.debug = debug

    def visit_Decl(self, node):
        if isinstance(node.type, c_ast.FuncDecl) and node.type.type.type.names[0] != 'void' and 'inline' not in node.funcspec:
            raise Exception("'%s': Function can not return a value" % node.name)

class LoopValidator(c_ast.NodeVisitor):
    def __init__(self, debug):
        c_ast.NodeVisitor.__init__(self)
        self.debug = debug
    def visit_While(self, node):
        raise Exception("While loop not supported")
    def visit_DoWhile(self, node):
        raise Exception("Do...While loop not supported")
    def visit_For(self, node):
        if not isinstance(node.init, c_ast.Assignment):
            raise Exception("Init statement of for loop must be assignment")
        if not isinstance(node.cond, c_ast.BinaryOp) or node.cond.op != '<':
            raise Exception("Cond statement of for loop must be less than inequality")
        self.generic_visit(node)

first_pass_validators=[IDValidator, LoopValidator]
second_pass_validators=[FuncValidator]
