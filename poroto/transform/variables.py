from pycparser import c_ast
from copy import deepcopy

default_type=None

class NameAllocator:
    def __init__(self):
        self.nextFreeIndex = {}
        self.stem = 'poroto_%s'

    def getTmpNameFor(self, funcName, name):
        if funcName not in self.nextFreeIndex:
            self.nextFreeIndex[funcName] = 0
        index = self.nextFreeIndex[funcName]
        self.nextFreeIndex[funcName] += 1
        return (self.stem % index) + "_" + name

    def getTmpNameForVar(self, declName, name):
        if declName is None:
            declName = ""
        return name + "_" + (self.stem % declName)

def do_create_simple_var(c_type, name, init=None):
    if isinstance(name, c_ast.ID):
        name = name.name
    if isinstance(c_type, c_ast.TypeDecl):
        c_type = deepcopy(c_type)
        c_type.declname = name
    elif isinstance(c_type, c_ast.PtrDecl):
        c_type = deepcopy(c_type)
        c_type.type.declname = name
    elif isinstance(c_type, c_ast.ArrayDecl):
        c_type = deepcopy(c_type)
        c_type.type.declname = name
    elif isinstance(c_type, str):
        c_type = c_ast.TypeDecl(name, [], c_ast.IdentifierType([c_type]))
    else:
        c_type = c_ast.TypeDecl(name, [], c_type)
    return c_ast.Decl(name,
                      [],
                      [],
                      [],
                      c_type,
                      init,
                      None)

def create_simple_var(c_type, name, init):
#         if isinstance(c_type, types.TypeDescriptor):
#             node = do_create_simple_var(c_type.user_type_tree, name, init)
#             node.poroto_type = c_type
#             name.poroto_type = c_type
#             return node                
    if isinstance(c_type, (c_ast.IdentifierType, c_ast.TypeDecl, c_ast.PtrDecl, c_ast.ArrayDecl, c_ast.Struct)):
        return do_create_simple_var(c_type, name, init)            
    elif default_type != None:
        if init and isinstance(init, c_ast.UnaryOp) and init.op == '&':
            ptr_type = c_ast.PtrDecl([], c_ast.TypeDecl('poroto_dummy', [], c_ast.IdentifierType([default_type])))
            return do_create_simple_var(ptr_type, name, init)
        else:
            return do_create_simple_var(default_type, name, init)
    else:
        raise Exception("Unable to create type for %s" % name.name, name.coord)
