#!/bin/bash

set -e

MODULE=$1
FILE=$2

CWD=`pwd`

if [[ `uname` == "Darwin" ]]; then
LIB_EXT=dylib
export DYLD_LIBRARY_PATH=$ROCCC_ROOT/lib:$DYLD_LIBRARY_PATH
else
LIB_EXT=so.0
export LD_LIBRARY_PATH=$ROCCC_ROOT/lib:$LD_LIBRARY_PATH
fi

#The steps for compilation are the following:
#  - Export the environment variables
#  - Create the vhdl directory if it does not already exist
#  - Run createScript
#  - Actually run the generated script
#  - Remove the script
#  - Compile through LLVM
#  - Clean up extra files

#  - Export the environment variables

export ROCCC_LIBRARY_PATH=$ROCCC_ROOT/LocalFiles
export ROCCC_HOME=$ROCCC_ROOT
export NCIHOME=$ROCCC_ROOT
export MACHSUIFHOME=$ROCCC_ROOT
export ARCH=`uname`
export PATH=$ROCCC_ROOT/bin:$PATH
export DATABASE_PATH=$ROCCC_ROOT/LocalFiles/

ROCCC_SCRIPT=$ROCCC_ROOT/bin/createScript

#  - Create the vhdl directory if it does not already exist
DIR=`dirname $CWD/$FILE`
mkdir -p $DIR/vhdl
ROCCC=$DIR/.ROCCC

LO_OPTIONS=$ROCCC/.optlo

#  - Run createScript

$ROCCC_SCRIPT $CWD/$FILE $ROCCC/$MODULE.opt $ROCCC/.moduleInfo $ROCCC/.preferenceFile $ROCCC/$MODULE.debug $ROCCC_ROOT

# The previous step will have created a one shot script for us to run and stored it in the tmp directory under the distribution directory

chmod 700 $ROCCC_ROOT/tmp/compile_suif2hicirrf.sh

#  - Actually run the generated script
pushd $DIR
$ROCCC_ROOT/tmp/compile_suif2hicirrf.sh $ROCCC_ROOT
popd

#  - Remove the script
#rm -f $ROCCC_ROOT/tmp/compile_suif2hicirrf.sh


# Now compile to VHDL (this used to be done with compile_llvmtovhdl.sh and consists of the following steps)
#  - run llvm-gcc on hi-cirrf.c
#  - Create the passes that will be used as the low level optimizations

LLVM_GCC=$ROCCC_ROOT/bin/llvmGcc/llvm-gcc

PATH=$ROCCC_ROOT/bin/llvmGcc:$PATH $LLVM_GCC -c -emit-llvm $DIR/hi_cirrf.c -o $DIR/hi_cirrf.c.bc

#  - Create the passes that will be used as the low level optimizations
PASSES=""
if grep -q MaximizePrecision $LO_OPTIONS; then
	PASSES="$PASSES -maximizePrecision"
fi
PASSES="$PASSES -renameMem -mem2reg -removeExtends -ROCCCfloat -lutDependency"
if grep -q ArithmeticBalancing $LO_OPTIONS; then
	PASSES="$PASSES -rocccFunctionInfo -flattenOperations -dce"
fi
PASSES="$PASSES -undefDetect -functionVerify -rocccCFGtoDFG -detectLoops"
if grep -q FanoutTreeGeneration $LO_OPTIONS; then
	PASSES="$PASSES -fanoutTree"
fi
PASSES="$PASSES -fanoutAnalysis -pipeline -retime"
if grep -q CopyReduction $LO_OPTIONS; then
	PASSES="$PASSES -minimizeCopies"
fi
PASSES="$PASSES -insertCopy -arrayNorm -vhdl -systemToSystem -printPortNames -componentInfo -deleteAll"

pushd $DIR
$ROCCC_ROOT/bin/opt \
  -load $ROCCC_ROOT/lib/FloatPass.$LIB_EXT \
  -load $ROCCC_ROOT/lib/PipelinePass.$LIB_EXT \
  -load $ROCCC_ROOT/lib/VHDLOutput.$LIB_EXT \
  -load $ROCCC_ROOT/lib/RocccIntrinsic.$LIB_EXT \
  $PASSES \
  -f -o /dev/null hi_cirrf.c.bc
popd

rm -f $DIR/hi_cirrf* $DIR/roccc.h
mv -f $DIR/*.suif $DIR/.ROCCC/

#Remove obsolete files or files we provide our own version
rm -f $DIR/MicroFifo*.v
rm -f $DIR/vhdl/InferredBRAMFifo*.vhdl
