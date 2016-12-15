from poroto.roccc.tool import invoke_roccc
from poroto.roccc import config
from poroto.common import mkdir_safe
import os
import sys

config.set_roccc_root(os.environ["ROCCC_ROOT"])
name = sys.argv[1]
filename = sys.argv[2]
type = sys.argv[3]
if type == 'system':
    options = ['MultiplyByConstElimination',
                'DivisionByConstElimination',
                ]
else:
    options = ['MultiplyByConstElimination',
               'DivisionByConstElimination',
               'Export',
               'FullyUnroll']
print "Generating %s %s (%s)" % (type, name, filename)
mkdir_safe('.ROCCC')
invoke_roccc(name, '.', filename, options, config.default_lo_options, config.default_timing_options)
