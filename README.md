# POROTO

The POROTO toolchain covers the transformation steps as well as the generation
of a ready-to-synthetise and implement project from a C based algorithm.
The toolchain generates all the code and support files needed to compile the
project, to test the generated code, and to perform simulation as well as
validation tests.

Poroto is implemented in Python and it realizes the following
steps :

 - The C source code is parsed and adapted for being fed to ROCCC tool. This step takes into account various configurations and constraints of ROCCC. In case the tool can not infer some characteristics of the input code, low level pragmas are used to guide the code generation.
 - Automation of ROCCC compilation process
 - VHDL code for interfaces, memories and FPGA glue is generated for offloaded kernels
 - Generation of test set-ups for the FPGA design and also for the CPU design
 - Automation of the compilation process for FPGA (Target dependent, in our case: Xilinx synthesis tools)
 - Generation of the code for CPU that interfaces with the FPGA implementation
(sending the bit stream to program the FPGA (target dependent), transferring the data,
execute the remote code and retrieve back the result data).

## Installation

The Poroto tool is intended to be installed and run on the following development platforms:

+ Recent Linux like distributions such as Debian Jessie (or later) or Ubuntu 14.04 (or higher)
+ Recent OS X based machine: Mac-OS Yosemite

### Dependencies

The Poroto tool has the following open-source dependencies:

- The Python interpreter (version 2.7 or above)
- PyCParser and PLY libraries (Included in Poroto)
- ROCCC compiler (version 0.7.6)
- GCC compiler
- RIFFA Framework (Version 2.0 or above, Optional)
- GHDL (Version 0.31 or above, Optional)

Besides leveraging the ROCCC compiler for the generation of VHDL code, our tool makes use of the proprietary components that are associated with the target platforms, like the AlphaData (ADM-XRC-6T1) :

- AlphaData VHDL Library, C SDK and Driver
- Xilinx PlanAhead compilation suite
- Xilinx IP Cores for the generation of memory blocks, FIFO, computational
IP (integer multiplication and division, floating point support, ...)

The above tools, API are not packaged with our tool for IPR reasons. The
templates are not provided for the same reason but can be disclosed to interested
parties that already have acquired a similar platform and associated tools

### Instructions

The tool does not require any installation steps. To launch the tool, the following
two environment variables must be set :

- ROCCC_ROOT : points to the top directory of the ROCCC tool
- POROTO_ROOT : points to the top directory of the Poroto tool

In order to simplify the usage, a Makefile support file is included in Poroto
distribution to set up the correct environment and select the right configuration
parameters.


### Usage

After installing the Poroto software and all its dependencies (see above), one can
use the simple demo provided to check the Toolchain. The demo is a simple code
that calculate the sum of two vectors, element by element. The demo source code,
available in the tool demo directory, is:

```c
#pragma poroto memory test_A int 100
#pragma poroto memory test_B int 100
#pragma poroto memory test_Out int 100
#pragma poroto stream::roccc_bram_in VectorAdd::A(test_A, N)
#pragma poroto stream::roccc_bram_in VectorAdd::B(test_B, N)
#pragma poroto stream::roccc_bram_out
VectorAdd::Out(test_Out, N)
void VectorAdd(int N, int* A, int* B, int* Out)
{
  int i;
  for(i = 0; i < N; ++i)
  {
    Out[i] = A[i] + B[i];
  }
}
```

In order to test the correctness of the generated code, we provide test vectors :

```python
from poroto.test import TestVector
test_vectors = {
’VectorAdd’:
TestVector(1,{
               ’N’: [12],
               ’A’: [[0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11]],
               ’B’: [[10, 11, 12, 13, 14, 15, 16, 17, 18, 19,
                      20, 21]],
               ’Out’: [[10, 12, 14, 16, 18, 20, 22, 24, 26,
                        28, 30, 32]],
               }),
}
```

The demo uses a simple Makefile to invoke Poroto :
````make
POROTO_ROOT=../..
FILES=vector_add.c
include $(POROTO_ROOT)/poroto.mak
```
The tool can be invoked using the Makefile provided in the demo
````make
make clean
make gen
make compile
make run
```


The gen target will read the source code, apply specific code transformation
and optimisation and then invoke the ROCCC tool for each module to be converted
into VHDL. Next, it generates all the dependencies needed by the modules, like
memory blocks, IP blocks, data streams and test benches. If the target is able
to communicate to a host environment, the tool will also generate the required
wrappers to invoke the FPGA from the host environment.

For the GHDL target, it is possible to compile the generated VHDL and perform
a run of the test bench on a simulated environment, this is done using the
compile and run targets.

To specify a hardware target, one must add either in the Makefile or on the
command line the TARGET parameter, e.g. if we want to use the alphadata FPGA
based accelerator board :
````bash
make TARGET=alphadata clean
make TARGET=alphadata gen
```

The generated project is found under the project/ directory and can be imported
as is in the FPGA backend tool for synthesis and implementation, for instance the
Xilinx PlanAhead suite. Also, the wrapper and C testbench for the host environment
have been generated as such :
```c
#include <inttypes.h>
#include "fpga.h"
void VectorAdd(int N, int *A, int *B, int *Out)
{
fpga_write_vector(0, (N)*4, A);
fpga_write_vector(1, (N)*4, B);
pFpgaSpace[0x1] = (uint32_t)N;
while (pFpgaSpace[0x2000] == 0) ; //Wait for resultReady
fpga_read_vector(2, (N)*4, Out);
}
```

The existing host code can simply invoke the transformed function without
changing the current code since the C wrapper keeps the same function signature
(i.e it implements a function with the same name and parameter but this time it
trigger the offloaded part rather than executing within the CPU).

Poroto software come with several other examples. Below a list of the ones
available in the distribution:
+ simple_add : A simple adder block with no data streaming
+ vector_add : A simple vector addition
+ vector_add_ip : A simple vector addition using an external IP block to perform
the operation
+ vector_add_float : A simple vector addition based on float elements
+ matrix_multiplication : A generic multiplication of integer matrices
+ buffer_sliding : A 3x3 moving window over a matrix
+ vector_avg : A n-element wide moving window over a vector
+ vector_add_reduce : An reduce operation performed on a vector using an
add operator

The code generated by Poroto can be optimized further using dedicated pragmas.
With these pragmas, the user can control the transformation path performed
by ROCCC, like partial loop unrolling, arithmetic balancing, pipelining optimisation,
etc., as well as the performance of the data streams generated by Poroto.

Furthermore, some other advanced code transformation can be applied like code or
variable inlining, data bitsize customisation, loop fusion, etc. 

For more details you can use command line help through: *poroto –help* .
