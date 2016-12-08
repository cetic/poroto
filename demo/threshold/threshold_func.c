#pragma poroto memory input_mem int 16984
#pragma poroto memory output_mem int 16984

#pragma poroto stream::roccc_bram_in threshold::input_image(input_mem, N*N, ROCCC_int9)
#pragma poroto stream::roccc_bram_out threshold::output_image(output_mem, N*N, ROCCC_int9)

typedef int ROCCC_int9;

void threshold(int N, ROCCC_int9 **input_image, ROCCC_int9 threshold_v, ROCCC_int9 **output_image)
{
  int c;
  int r;
  ROCCC_int9 aux;

  for (r = 0; r < N; r++) {
    for (c = 0; c < N; c++) {
      if (input_image[r][c] < threshold_v) {
        aux = 0;
      } else {
        aux = 255;
      }
      output_image[r][c]= aux;
    }
  }
}
