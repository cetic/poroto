#include <c_wrapper.h>
#include <poroto.h>
#include <stdio.h>
#include <string.h>

%%%INIT%%%

int main() {
	int test_successful = 1;
	int i;
	int res = poroto_fpga_init();
	printf("Done : %x\n", res);

	//%%%TB%%%

	poroto_fpga_close();
	return test_successful ? 0 : 1;
}
