#ifndef _ALPHADATA_H_
#define _ALPHADATA_H_

#include <stdint.h>

#ifdef __cplusplus
extern "C" {
#endif

extern volatile uint32_t* pFpgaSpace;

int fpga_init(void);

void fpga_write_vector(int index, unsigned long size, void const * data);
void fpga_read_vector(int index, unsigned long size, void * data);

void fpga_close(void);

#ifdef __cplusplus
}
#endif

#endif
