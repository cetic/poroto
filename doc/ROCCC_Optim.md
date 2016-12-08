# ROCCC Optimisations

## Code optimisations

### MaximizePrecision

Bitwidth is increased during calculation and truncation happens only as assignation

![MaximizePrecision](images/MaximizePrecision.png)

### TemporalCommonSubExpressionElimination

Data that are calculed several time to the same result in iterations are factored

![TemporalCommonSubExpressionElimination](images/TemporalCommonSubExpressionElimination.png)

### MultiplyByConstElimination

Replace multiplications by additions and shifts

![MultiplyByConstElimination](images/MultiplyByConstElimination.png)

### DivisionByConstElimination

Replace divisions by additions and shifts

![DivisionByConstElimination](images/DivisionByConstElimination.png)

### ArithmeticBalancing

Arithmetic expression are parallelised to optimise execution time

![ArithmeticBalancing](images/ArithmeticBalancing.png)

### CopyReduction

In pipelining, instead of copying values from stages to stages, they are recalculated when needed.

![CopyReduction](images/CopyReduction.png)

## Loop optimisations

### LoopFusion

Loops with same boundaries and no dependencies are merged into one loop

![LoopFusion](images/LoopFusion.png)

### LoopInterchange

Switch loop variables of two nested loops

![LoopInterchange](images/LoopInterchange.png)

### LoopUnrolling

Unroll loops until the given bound

![LoopUnrolling](images/LoopUnrolling.png)

### InlineModule

Inline a given module at the given place

![InlineModule](images/InlineModule.png)

### InlineAllModules

Inline recursively all modules used

![InlineAllModules](images/InlineAllModules.png)

## Low level optimisation

### FanoutTreeGeneration

When pipelining, control the amount of parallelised operation vs the depth of the pipelining

![FanoutTreeGeneration](images/FanoutTreeGeneration.png)

### OperationsPerPipelineStage

When pipelining, control the maximum of operations per pipeline stage

### MaxFanoutRegistered

Control the fanout of unregistered values before using a register, i.e. control the average size of a pipeline step

## Not supported or irrelevant optimisations

### FullyUnroll

Force loop unrolling, automatically applied when module is detected

### Redundancy

Enable double or triple redundancy of a module. Not supported by POROTO

### SystolicArrayGeneration

Perform data iteration as a diagonal wavefront. Not supported by POROTO
