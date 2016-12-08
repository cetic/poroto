#pragma poroto memory test_A int 100
#pragma poroto memory test_B int 100
#pragma poroto memory test_R int 100

#pragma poroto stream::roccc_bram_in VectorMatrix::A(test_A, count)
#pragma poroto stream::roccc_bram_in VectorMatrix::B(test_B, count)
#pragma poroto stream::roccc_bram_out VectorMatrix::R(test_R, count*count)

void VectorMatrix(unsigned int count, int* A, int* B, int **R)
{
	unsigned int i;
	unsigned int j;
	for(i = 0; i < count; ++i)
	{
	    for(j = 0; j < count; ++j)
	    {
	        R[i][j] = A[i] + B[j];
	    }
	}
}
