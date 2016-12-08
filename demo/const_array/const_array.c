
#pragma poroto memory test_A int 100
#pragma poroto memory test_Out int 100

#pragma poroto stream::roccc_bram_in const_array::A(test_A, N)
#pragma poroto stream::roccc_bram_out const_array::Out(test_Out, N)

void const_array(int N, int* A, int* Out)
{
        #pragma poroto array lut
        int source[16] = {0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15};
	int i;
	for(i = 0; i < N; ++i)
	{
		Out[i] = A[i] + source[i];
	}
}
