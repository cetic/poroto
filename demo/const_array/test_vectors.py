from poroto.test import TestVector

test_vectors = {
 'const_array':
 TestVector(1,{
               'N':  [12],
               'A': [[0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11]],
               'Out': [[0, 2, 4, 6, 8, 10, 12, 14, 16, 18, 20, 22]],
              }),
}
