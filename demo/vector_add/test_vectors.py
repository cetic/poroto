from poroto.test import TestVector

test_vectors = {
 'VectorAdd':
 TestVector(1,{
               'N':  [12],
               'A': [[0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11]],
               'B': [[10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21]],
               'Out': [[10, 12, 14, 16, 18, 20, 22, 24, 26, 28, 30, 32]],
              }),
}
