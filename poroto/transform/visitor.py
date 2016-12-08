'''
Created on 31 juil. 2012

@author: ld
'''

from pycparser import c_ast

class AstModifier(c_ast.NodeVisitor):
    def __init__(self, debug=None):
        self.debug = debug
        self.node_stack = []
        self._current_node = None
        self._right_op = False
        self.context_stack = {}
        self._i = {}
        self._c_len = {}
        self._node_list = {}
        self._currentFunc = None
        self.current_context = None

    def push_local_context(self, node):
        self.node_stack.append( (self._current_node, self._right_op))
        self._current_node = node
        self._right_op = False

    def pop_local_context(self):
        node = self.node_stack.pop()
        self._current_node, self._right_op = node

    def push_context(self, node, node_type, node_list):
        self.push_local_context(node)
        if node_type not in self.context_stack:
            self.context_stack[node_type] = []
            self._i[node_type] = 0
            self._c_len[node_type] = 0
            self._node_list[node_type] = None
        self.context_stack[node_type].append( (self.current_context, self._i[node_type], self._c_len[node_type], self._node_list[node_type]))
        self._i[node_type] = 0
        self._c_len[node_type] = len(node_list)
        self._node_list[node_type] = node_list
        self.current_context = node_type

    def pop_context(self, context_type):
        self.pop_local_context()
        context = self.context_stack[context_type].pop()
        self.current_context, self._i[context_type], self._c_len[context_type], self._node_list[context_type] = context

    def remove_node(self, context=None):
        if not context:
            context = self.current_context
        if context in self._node_list:
            self._node_list[context].pop(self._i[context])
            self._i[context]-=1
            self._c_len[context]-=1
        else:
            raise Exception("Can not remove node in %s" % context)

    def replace_expr(self, node):
        if isinstance(self._current_node, c_ast.UnaryOp) or isinstance(self._current_node, c_ast.Return):
            self._current_node.expr = node
        elif isinstance(self._current_node, c_ast.BinaryOp):
            if self._right_op:
                self._current_node.right = node
            else:
                self._current_node.left = node
        elif isinstance(self._current_node, c_ast.Assignment):
            if self._right_op:
                self._current_node.rvalue = node
            else:
                self._current_node.lvalue = node
        elif isinstance(self._current_node, c_ast.ExprList):
            self.replace_node(node, 'ExprList')
        elif isinstance(self._current_node, c_ast.If):
            self._current_node.cond = node
        elif isinstance(self._current_node, c_ast.Decl):
            self._current_node.init = node
        elif isinstance(self._current_node, c_ast.ArrayRef):
            if self._right_op:
                self._current_node.subscript = node
            else:
                self._current_node.name = node
        else:
            raise Exception("Unsupported construction %s" % self._current_node.__class__.__name__)

    def replace_node(self, node, context=None):
        if not context:
            context = self.current_context
        self._node_list[context][self._i[context]] = node

    def insert_node_before(self, node, context=None):
        if not context:
            context = self.current_context
        if context in self._node_list:
            self._node_list[context].insert(self._i[context], node)
            self._i[context]+=1
            self._c_len[context]+=1
        else:
            raise Exception("Can not insert node in %s" % context)

    def insert_node_after(self, node, context=None):
        if not context:
            context = self.current_context
        if context in self._node_list:
            self._node_list[context].insert(self._i[context]+1, node)
            self._i[context]+=1
            self._c_len[context]+=1
        else:
            raise Exception("Can not insert node in %s" % context)

    def next_nodes(self, context=None):
        if not context:
            context = self.current_context
        if self._i[context]+1 == self._c_len[context]:
            return []
        else:
            return self._node_list[context][self._i[context]+1:]

    def generic_visit(self, node):
        self.push_local_context(node)
        for c_name, c in node.children():
            self.visit(c)
        self.pop_local_context()

    def visit_FuncDef(self, node):
        self._currentFunc = node
        self.generic_visit(node)
        self._currentFunc = None

    def visit_BinaryOp(self, node):
        self.push_local_context(node)
        self.visit(node.left)
        self._right_op = True
        self.visit(node.right)
        self.pop_local_context()

    def visit_Assignment(self, node):
        self.push_local_context(node)
        self.visit(node.lvalue)
        self._right_op = True
        self.visit(node.rvalue)
        self.pop_local_context()

    def visit_ArrayRef(self, node):
        self.push_local_context(node)
        self.visit(node.name)
        self._right_op = True
        self.visit(node.subscript)
        self.pop_local_context()

    def visit_NodeList(self, node, node_type, node_list):
        if node_list is None: return
        self.push_context(node, node_type, node_list)
        while self._i[node_type] < self._c_len[node_type]:
            child = self._node_list[node_type][self._i[node_type]]
            self.visit(child)
            self._i[node_type]+=1
        self.pop_context(node_type)

    def visit_Compound(self, node):
        self.visit_NodeList(node, 'Compound', node.block_items)
    
    def visit_ParamList(self, node):
        self.visit_NodeList(node, 'ParamList', node.params)

    def visit_ExprList(self, node):
        self.visit_NodeList(node, 'ExprList', node.exprs)
        
    def visit_FileAST(self, node):
        self.visit_NodeList(node, 'FileAST', node.ext)