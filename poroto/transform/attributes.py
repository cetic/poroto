from copy import deepcopy

extra_attr = {}

def set_extra_attr(obj, attr, value):
    if not obj in extra_attr:
        extra_attr[obj] = {}
    extra_attr[obj][attr] = value

def get_extra_attr(obj, attr, default=None):
    if not obj in extra_attr:
        return deepcopy(default)
    if not attr in extra_attr[obj]:
        return deepcopy(default)
    return extra_attr[obj][attr]
