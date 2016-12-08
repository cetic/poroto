from poroto.test import TestVector

test_vectors = {
 'VectorMatrix':
 TestVector(1,{
               'count':  [4],
               'A': [[0, 10, 20, 30]],
               'B': [[0,  1,  2,  3]],
               'R': [[ 0,  1,  2,  3,
                      10, 11, 12, 13,
                      20, 21, 22, 23,
                      30, 31, 32, 33]],
              }),
}
