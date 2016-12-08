from transform.visitor import AstModifier
from pycparser import c_ast

class PragmaRegistry():
    def __init__(self, debug):
        self.debug = debug
        self.registry = {}
        
    def add_pragma_type(self, pragma_type, pragma_handler):
        self.registry[pragma_type] = pragma_handler

    def call_handler_for(self, pragma_type, node, tokens, next_stmt):
        if '::' in pragma_type:
            pragma_type = pragma_type.split('::')[0]
        if pragma_type in self.registry:
            self.registry[pragma_type].parse_pragma(node, tokens, next_stmt)
        else:
            raise Exception("Invalid pragma '%s' : %s'" % (pragma_type, node.string))

class PragmaHandler():
    def __init__(self, debug):
        self.debug = debug

    def parse_pragma(self, node, tokens, next_stmt):
        pass

class ParsePorotoPragma(AstModifier):
    def __init__(self, registry, debug):
        AstModifier.__init__(self)
        self.registry = registry
        self.debug = debug

    def find_next_statement(self):
        stat = None
        for stat in self.next_nodes():
            if not isinstance(stat, c_ast.Pragma):
                break
        if not stat:
            raise Exception("No statement applicable for pragma")
        return stat
    def visit_Pragma(self, node):
        tokens = node.string.split()
        if len(tokens) < 2 or tokens[0] != 'poroto':
            raise Exception("Invalid pragma '%s'" % node.string)
        next_stmt = self.find_next_statement()
        self.registry.call_handler_for(tokens[1], node, tokens, next_stmt)
