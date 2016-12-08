from pycparser import c_ast
from transform.visitor import AstModifier

class CompoundSimplifier(c_ast.NodeVisitor):
    def visit_While(self, node):
        if not isinstance( node.stmt, c_ast.Compound):
            node.stmt = c_ast.Compound([node.stmt])
        self.generic_visit(node)
            
    def visit_DoWhile(self, node):
        if not isinstance( node.stmt, c_ast.Compound):
            node.stmt = c_ast.Compound([node.stmt])
        self.generic_visit(node)
            
    def visit_For(self, node):
        if not isinstance( node.stmt, c_ast.Compound):
            node.stmt = c_ast.Compound([node.stmt])
        self.generic_visit(node)
            
    def visit_If(self, node):
        if node.iftrue is not None and not isinstance( node.iftrue, c_ast.Compound):
            node.iftrue = c_ast.Compound([node.iftrue])
        if node.iffalse is not None and not isinstance( node.iffalse, c_ast.Compound):
            node.iffalse = c_ast.Compound([node.iffalse])
        self.generic_visit(node)
