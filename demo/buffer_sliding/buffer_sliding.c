#pragma poroto memory test_A int 100
#pragma poroto memory test_B int 100

#pragma poroto stream::roccc_bram_in Buffer_Sliding::A(test_A, (height+2)*(width+2))
#pragma poroto stream::roccc_bram_out Buffer_Sliding::B(test_B, height*width)

void Buffer_Sliding(int** A, int height, int width, int** B)
{
  int i;
  int j;

  int row1;
  int row2;
  int row3;

  int windowMax ;

  for (i = 0 ; i < height ; ++i)
  {
    for (j = 0 ; j < width ; ++j)
    {
        row1 = A[i][j] + A[i][j+1] + A[i][j+2];
        row2 = A[i+1][j] + A[i+1][j+1] + A[i+1][j+2];
        row3 = A[i+2][j] + A[i+2][j+1] + A[i+2][j+2];
        B[i][j] = row1 + row2 + row3;
    }
  }
}
