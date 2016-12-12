import string
from poroto.common import load_template

class FileTemplate:
    def __init__(self, template_file):
        self.template_file = template_file
        self.map = {}
        self.template = load_template(self.template_file)

    def clear_keys(self):
        self.map = {}

    def set_keys(self, keys):
        self.map.update(keys)

    def generate(self, out_file_name):
        out = open(out_file_name, 'w' )
        for line in self.template:
            for (key, value) in self.map.iteritems():
                tag = "%%%" + key + "%%%" 
                if tag in line:
                    if isinstance(value, list):
                        for item in value:
                            print >> out, item
                        continue
                    else:
                        line = string.replace(line, tag, value)
            print >> out, line,
        out.close()
