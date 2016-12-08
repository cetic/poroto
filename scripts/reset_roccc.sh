#!/bin/bash

set -e

# The tasks that the reset script must do are as follows:
#  - Copy the blank.suif file over the repository.suif file
#  - Copy the blank.h file over the roccc-library.h file
#  - Remove the vhdlLibrary.sql3 file
#  - Touch a new vhdlLibrary file
#  - Run the initializeFP binary program

if [[ "$ROCCC_ROOT" == "" ]]; then
	echo "ROCCC_ROOT not set"
	exit 1
fi

export ROCCC_LIBRARY_PATH=$ROCCC_ROOT/LocalFiles

if [[ ! -e $ROCCC_LIBRARY_PATH ]]; then
	echo "ROCCC distribution not found"
	exit 1
fi

cp -f $ROCCC_LIBRARY_PATH/blank.suif $ROCCC_LIBRARY_PATH/repository.suif
cp -f $ROCCC_LIBRARY_PATH/blank.h $ROCCC_LIBRARY_PATH/roccc-library.h
		
rm -f $ROCCC_LIBRARY_PATH/vhdlLibrary.sql3
		
touch $ROCCC_LIBRARY_PATH/vhdlLibrary.sql3

$ROCCC_ROOT/bin/initializeFP $ROCCC_LIBRARY_PATH/vhdlLibrary.sql3

echo "ROCCC Database Reset"
