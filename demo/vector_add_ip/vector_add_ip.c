#pragma poroto memory test_A int 100
#pragma poroto memory test_B int 100
#pragma poroto memory test_R int 100

#pragma poroto stream::roccc_bram_in AddFunc::A(test_A, count)
#pragma poroto stream::roccc_bram_in AddFunc::B(test_B, count)
#pragma poroto stream::roccc_bram_out AddFunc::R(test_R, count)

#pragma poroto latency 2
void adder(int a_in, int b_in, int & r_out_out);

void AddFunc(unsigned int count, int* A, int* B, int* R)
{
	unsigned int i;
	for(i = 0; i < count; ++i)
	{
	    int internal;
		adder(A[i],B[i], internal);
		R[i] = internal;
	}
}
