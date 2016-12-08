#pragma poroto memory test_A int 100
#pragma poroto memory test_B int 100
#pragma poroto memory test_C int 100

#pragma poroto stream::roccc_bram_in MatrixMultiplication::A(test_A, height_A*width_A_height_B)
#pragma poroto stream::roccc_bram_in MatrixMultiplication::B(test_B, width_A_height_B*width_B)
#pragma poroto stream::roccc_bram_out MatrixMultiplication::C(test_C, height_A*width_B)

void MatrixMultiplication(int** A, int** B, int height_A, int width_A_height_B, int width_B, int** C)
{
  int i;
  int j;
  int k;

  for(i = 0; i < height_A; ++i)
  {
    for (j = 0; j < width_B; ++j)
    {
      int currentSum = 0;
      for (k = 0; k < width_A_height_B; ++k)
      {
        currentSum += A[i][k] * B[k][j];
      }
      C[i][j] = currentSum;
    }
  }
}
