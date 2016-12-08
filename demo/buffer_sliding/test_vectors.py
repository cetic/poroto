from poroto.test import TestVector

test_vectors = {
 'Buffer_Sliding':
 TestVector(1,{
               'height':  [1],
               'width': [2],
               'A': [[  1,   2,   3,   4,
                       10,  20,  30,  40,
                      100, 200, 300, 400 ]],
               'B': [[666, 999]],
              }),
}
