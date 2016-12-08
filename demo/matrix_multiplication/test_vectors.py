from poroto.test import TestVector

test_vectors = {
 'MatrixMultiplication':
 TestVector(1,{
               'height_A':  [3],
               'width_A_height_B': [2],
               'width_B': [4],
               'A': [[1, 2,
                      3, 4,
                      5, 6]],
               'B': [[1, 2, 3, 4,
                      5, 6, 7, 8]],
               'C': [[ 11, 14, 17, 20,
                       23, 30, 37, 44,
                       35, 46, 57, 68]],
              }),
}
