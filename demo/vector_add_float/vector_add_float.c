
#pragma poroto memory test_A float 100
#pragma poroto memory test_B float 100
#pragma poroto memory test_Out float 100

#pragma poroto stream::roccc_bram_in VectorAddFloat::A(test_A, N)
#pragma poroto stream::roccc_bram_in VectorAddFloat::B(test_B, N)
#pragma poroto stream::roccc_bram_out VectorAddFloat::Out(test_Out, N)

void VectorAddFloat(int N, float* A, float* B, float* Out)
{
	int i;
	for(i = 0; i < N; ++i)
	{
		Out[i] = A[i] + B[i];
	}
}
