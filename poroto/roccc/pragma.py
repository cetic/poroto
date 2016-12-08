from poroto.pragma import PragmaHandler
from poroto.transform.attributes import set_extra_attr, get_extra_attr
from pycparser import c_ast
import config

class RocccPragmaHandler(PragmaHandler):
    def parse_pragma(self, node, tokens, next_stmt):
        roccc_option=None
        roccc_lo_option=None
        roccc_timing_option=None
        roccc_timing_option_value=None
        enable=True
        if len(tokens) < 3:
            raise Exception("Invalid roccc pragma '%s'" % node.string)
        if tokens[2] in ["TemporalCommonSubExpressionElimination",
                         "LoopFusion",
                         "MultiplyByConstElimination",
                         "DivisionByConstElimination"]:
            roccc_option = tokens[2]
            if len(tokens) > 3:
                if tokens[3] == 'enable':
                    enable=True
                elif tokens[3] == 'disable':
                    enable=False
                else:
                    raise Exception("Invalid roccc pragma '%s'" % node.string)
        elif tokens[2] in ["MaximizePrecision",
                         "ArithmeticBalancing",
                         "CopyReduction"]:
            roccc_lo_option = tokens[2]
            if len(tokens) > 3:
                if tokens[3] == 'enable':
                    enable=True
                elif tokens[3] == 'disable':
                    enable=False
                else:
                    raise Exception("Invalid roccc pragma '%s'" % node.string)
        elif tokens[2] == "FanoutTreeGeneration" and len(tokens) == 4:
            roccc_lo_option = ' '.join(tokens[2:4])
        elif tokens[2] in ['AND',
                           'Add',
                           'Compare',
                           'Copy',
                           'MaxFanoutRegistered',
                           'Mult',
                           'Mux',
                           'OR',
                           'Shift',
                           'Sub',
                           'XOR',
                           'OperationsPerPipelineStage'] and len(tokens) == 4:
            roccc_timing_option = tokens[2]
            roccc_timing_option_value = tokens[3]
        elif tokens[2] == "LoopUnrolling" and len(tokens) == 5:
            roccc_option = ' '.join(tokens[2:5])
        elif tokens[2] == "LoopInterchange" and len(tokens) == 5:
            roccc_option = ' '.join(tokens[2:5])
        elif tokens[2] == "InlineModule" and len(tokens) == 4:
            roccc_option = ' '.join(tokens[2:4])
        elif tokens[2] == "InlineAllModules" and len(tokens) == 4:
            roccc_option = ' '.join(tokens[2:4])
        elif tokens[2] in ["FullyUnroll", "Export"]:
            print "Ignoring roccc pragma '%s'" % node.string
        elif tokens[2] in ["SystolicArrayGeneration", "ComposedSystem", "Redundancy"]:
            raise Exception("Not supported roccc pragma '%s'" % node.string)
        else:
            raise Exception("Invalid roccc pragma '%s'" % node.string)
        if not isinstance(next_stmt, c_ast.FuncDef):
            raise Exception("ROCCC pragma can only be applied on function definition")
        if roccc_option:
            current=get_extra_attr(next_stmt, 'roccc_options', config.default_options)
            if enable:
                if not roccc_option in current:
                    current.append(roccc_option)
            else:
                if roccc_option in current:
                    current.remove(roccc_option)
            set_extra_attr(next_stmt, 'roccc_options', current)
        if roccc_lo_option:
            current=get_extra_attr(next_stmt, 'roccc_lo_options', config.default_lo_options)
            if enable:
                if not roccc_lo_option in current:
                    current.append(roccc_lo_option)
            else:
                if roccc_lo_option in current:
                    current.remove(roccc_lo_option)
            set_extra_attr(next_stmt, 'roccc_lo_options', current)
        if roccc_timing_option:
            current=get_extra_attr(next_stmt, 'roccc_timing_options', config.default_timing_options)
            current[roccc_timing_option] = roccc_timing_option_value
            set_extra_attr(next_stmt, 'roccc_timing_options', current)

