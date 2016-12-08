from poroto.designer import Designer
from poroto.common import get_path_for
from poroto.config import lib_path, ipcore_path, src_path, gen_path, cfg_path, use_unisim, design_tool
import os
import string

class Ghdl(Designer):
    dest_path = {
        lib_path: 'lib',
        ipcore_path: 'ipcore_dir',
        src_path: 'src',
        gen_path: 'gen',
        cfg_path: ''
        }
    def __init__(self):
        Designer.__init__(self)
        
    def load_templates(self):
        self.template = []
        template_file = open(get_path_for(os.path.join(design_tool, self.dest_path[cfg_path]), 'Makefile'), 'r' )
        for line in template_file:
            self.template.append(line)
        template_file.close()

    def get_file_path(self, file):
        return os.path.join(self.dest_path[file['cat']], file['file'])
    
    def get_files(self):
        files = []
        for file in self.files:
            files.append(self.get_file_path(file))
        return files
        
    def generate(self, project_path):
        self.load_templates()
        print "Updating Makefile"
        self.out=open(os.path.join(project_path, self.dest_path[cfg_path], 'Makefile'), 'w' )
        for line in self.template:
            if '%%%GEN_FILES%%%' in line:
                line = string.replace(line, '%%%GEN_FILES%%%', ' '.join(self.get_files()))
            elif '%%%UNISIM%%%' in line:
                line = string.replace(line, '%%%UNISIM%%%', str(int(use_unisim)))
            print >> self.out, line,
        self.out.close()
            
