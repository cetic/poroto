import string
from poroto.common import load_template, mkdir_safe
import os

class FileTemplate:
    platform = None
    def __init__(self, template_file):
        self.template_file = template_file
        self.clear_keys()
        self.template = load_template(self.template_file)

    def clear_keys(self):
        self.map = {}
        if self.platform:
            self.map.update(self.platform.get_keys())

    def set_keys(self, keys):
        self.map.update(keys)

    def generate(self, *klist):
        if len(klist) > 1:
            out_file_name = os.path.join(*klist)
        else:
            out_file_name = klist[0]
        mkdir_safe(os.path.dirname(out_file_name))
        out = open(out_file_name, 'w' )
        for line in self.template:
            for (key, value) in self.map.iteritems():
                tag = "%%%" + key + "%%%" 
                if tag in line:
                    if isinstance(value, list):
                        line = ""
                        for item in value:
                            print >> out, item
                    else:
                        try:
                            line = string.replace(line, tag, str(value))
                        except TypeError:
                            print "Tag '%s' has not a string value '%s'" % (tag, value)
                            raise Exception("Invalid tag value")
            print >> out, line,
        out.close()
