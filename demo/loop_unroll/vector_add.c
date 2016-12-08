
#pragma poroto memory test_A int 100
#pragma poroto memory test_B int 100
#pragma poroto memory test_Out int 100

#pragma poroto stream::roccc_bram_in VectorAdd::A(test_A, N)
#pragma poroto stream::roccc_bram_in VectorAdd::B(test_B, N)
#pragma poroto stream::roccc_bram_out VectorAdd::Out(test_Out, N)

#pragma poroto roccc LoopUnrolling L1 4

void VectorAdd(int N, int* A, int* B, int* Out)
{
	int i;
	L1:
	for(i = 0; i < N; ++i)
	{
		Out[i] = A[i] + B[i];
	}
}
