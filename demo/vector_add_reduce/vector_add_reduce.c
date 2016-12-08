
#pragma poroto memory test_A int 100

#pragma poroto stream::roccc_bram_in VectorAddReduce::A(test_A, N)

void VectorAddReduce(int N, int* A, int Out)
{
	int i;
	for(i = 0; i < N; ++i)
	{
		Out = Out + A[i];
	}
}
