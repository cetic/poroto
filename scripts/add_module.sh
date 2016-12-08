#!/bin/bash

set -e

MODULE=$1

CWD=`pwd`

if [[ `uname` == "Darwin" ]]; then
LIB_EXT=dylib
export DYLD_LIBRARY_PATH=$ROCCC_ROOT/lib:$DYLD_LIBRARY_PATH
else
LIB_EXT=so.0
export LD_LIBRARY_PATH=$ROCCC_ROOT/lib:$LD_LIBRARY_PATH
fi

# The steps that the script performs are as follows:
#  - Set up the environment variables
#  - Run gcc2suif on blank.c
#  - Run suifdriver with the appropriate commands

#  - Set up the environment variables

export ROCCC_LIBRARY_PATH=$ROCCC_ROOT/LocalFiles
export ROCCC_HOME=$ROCCC_ROOT
export NCIHOME=$ROCCC_ROOT
export MACHSUIFHOME=$ROCCC_ROOT
export ARCH=`uname`
export PATH=$ROCCC_ROOT/bin:$PATH
export DATABASE_PATH=$ROCCC_ROOT/LocalFiles/

#  - Run gcc2suif on blank.c
$ROCCC_ROOT/bin/gcc2suif $ROCCC_ROOT $DATABASE_PATH/blank.c

$ROCCC_ROOT/bin/suifdriver -e "\
require basicnodes suifnodes cfenodes transforms control_flow_analysis ; \
require jasonOutputPass libraryOutputPass global_transforms utility_transforms array_transforms ; \
require bit_vector_dataflow_analysis gcc_preprocessing_transforms verifyRoccc ; \
require preprocessing_transforms data_dependence_analysis ; \
require fifoIdentification ; \
load $ROCCC_ROOT/LocalFiles/blank.suif ; \
CleanRepositoryPass $DATABASE_PATH ; \
AddModulePass $MODULE $DATABASE_PATH ; \
DumpHeaderPass $DATABASE_PATH ;"
