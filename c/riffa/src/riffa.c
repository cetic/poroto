#include <stdio.h>
#include <stdlib.h>
#include <riffa.h>
#include "poroto.h"

static fpga_t *fpga;

int poroto_fpga_init(void)
{
  int fid = 0;
  fpga = fpga_open(fid);
  return fpga != NULL;
}

void poroto_fpga_write_vector(int bankIndex, unsigned long size, void const * data)
{
  fpga_send(fpga, bankIndex, data, size, 0, 1, 0);
}

void poroto_fpga_read_vector(int bankIndex, unsigned long size, void * data)
{
  fpga_recv(fpga, bankIndex, data, size, 0);
}

void poroto_fpga_close(void)
{
  fpga_close(fpga);
}
