#ifndef POROTO_H
#define POROTO_H

#include <stdint.h>

#ifdef __cplusplus
extern "C" {
#endif

extern volatile uint32_t* pFpgaSpace;

int poroto_fpga_init(void);

void poroto_fpga_write_vector(int index, unsigned long size, void const * data);
void poroto_fpga_read_vector(int index, unsigned long size, void * data);

void poroto_fpga_close(void);

#ifdef __cplusplus
}
#endif

#endif /* POROTO_H */
