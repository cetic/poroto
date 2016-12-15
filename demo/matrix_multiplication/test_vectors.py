from poroto.test import TestVector

test_vectors = {
 'MatrixMultiplication':
 TestVector(1,{
               'height_A':  [4],
               'width_A_height_B': [3],
               'width_B': [5],
               'A': [[ 1,  2,  3,
                       4,  5,  6,
                       7,  8,  9,
                      10, 11, 12]],
               'B': [[ 1,  2,  3,  4, 5,
                       6,  7,  8,  9, 10,
                      11, 12, 13, 14, 15 ]],
               'C': [[ 46,    52,    58,    64,    70,
                      100,   115,   130,   145,   160,
                      154,   178,   202,   226,   250,
                      208,   241,   274,   307,   340]],
              }),
}
