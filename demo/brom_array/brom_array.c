
#pragma poroto memory test_A int 100
#pragma poroto memory test_Out int 100

#pragma poroto stream::roccc_bram_in brom_array::A(test_A, N)
#pragma poroto stream::roccc_bram_out brom_array::Out(test_Out, N)

void brom_array(int N, int* A, int* Out)
{
        #pragma poroto array brom
        int source[16] = {0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15};
	int i;
	for(i = 0; i < N; ++i)
	{
		Out[i] = A[i] + source[i];
	}
}
