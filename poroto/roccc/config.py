import os

register = True

roccc_root=None
roccc_db=None
roccc_db_relative="LocalFiles/vhdlLibrary.sql3"

default_options=['MultiplyByConstElimination', 'DivisionByConstElimination']
default_lo_options=['ArithmeticBalancing', 'CopyReduction']
default_timing_options = {
               'AND': 17,
               'Add': 23,
               'Compare': 21,
               'Copy': 12,
               'MaxFanoutRegistered': 100,
               'Mult': 42,
               'Mux': 14,
               'OR': 17,
               'Shift': 12,
               'Sub': 23,
               'XOR': 17,
               'OperationsPerPipelineStage': 3.3333333
               }

def set_roccc_root(new_root):
    global roccc_root
    global roccc_db
    roccc_root=new_root
    roccc_db=os.path.join(roccc_root, roccc_db_relative)