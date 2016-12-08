#pragma poroto memory test_A int 100
#pragma poroto memory test_R int 100

#pragma poroto stream::roccc_bram_in VectorAvg::A(test_A, count+1)
#pragma poroto stream::roccc_bram_out VectorAvg::R(test_R, count)

void VectorAvg(unsigned int count, int* A, int* R)
{
	unsigned int i;
	for(i = 0; i < count; i += 2)
	{
		R[i] = (A[i] + A[i+1])/2;
	}
}
