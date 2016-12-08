from .designer import Designer
from .common import get_path_for
from .config import design_tool, design_version, lib_path, ipcore_path, src_path, gen_path, cfg_path
import os

class PlanAhead(Designer):
#     'ise': {lib_path: 'lib',
#          ipcore_path: 'ipcore_dir',
#          src_path: 'src',
#          gen_path: 'gen'
#          }
    dest_path = {
        lib_path: 'poroto.srcs/sources_1/lib',
        ipcore_path: 'poroto.srcs/sources_1/ip',
        src_path : 'poroto.srcs/sources_1/src',
        gen_path: 'poroto.srcs/sources_1/gen',
        cfg_path: 'poroto.data/sources_1'
        }

    def __init__(self):
        Designer.__init__(self)
        
    def load_templates(self):
        self.template = []
        template_file = open(get_path_for(os.path.join(design_tool, design_version, self.dest_path[cfg_path]), 'fileset.xml'), 'r' )
        for line in template_file:
            self.template.append(line)
        template_file.close()

    def get_file_path(self, file):
        return os.path.join(self.dest_path[file['cat']], file['file'])

    def do_add_files(self):
        for file in self.files:
            file_path=os.sep.join(self.get_file_path(file).split(os.sep)[1:])
            
            print >> self.out, '    <File Path="$PSRCDIR/%s">' % file_path 
            print >> self.out, '      <FileInfo>'
            print >> self.out, '        <Attr Name="UsedInSynthesis" Val="%d"/>' % file['synth']
            print >> self.out, '        <Attr Name="UsedInImplementation" Val="%d"/>' % file['synth']
            print >> self.out, '        <Attr Name="UsedInSimulation" Val="%d"/>' % file['sim']
            print >> self.out, '      </FileInfo>'
            print >> self.out, '    </File>'

    def generate(self, project_path):
        self.load_templates()
        print "Updating fileset"
        self.out=open(os.path.join(project_path, self.dest_path[cfg_path], 'fileset.xml'), 'w' )
        for line in self.template:
            if '%%%GEN_FILES%%%' in line:
                self.do_add_files()
            else:
                print >> self.out, line,
        self.out.close()
            
