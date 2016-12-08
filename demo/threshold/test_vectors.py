from poroto.test import TestVector
from random import random

N=6
threshold=128
input_1=[int(256*random()) for i in xrange(N*N)]
output_1=map((lambda x: 0 if x < threshold else 255), input_1)
input_2=[int(256*random()) for i in xrange(N*N)]
output_2=map((lambda x: 0 if x < threshold else 255), input_2)

test_vectors = {
 'threshold':
 TestVector(2,{
               'N':  [N, N],
               'threshold_v':  [threshold, threshold],
               'input_image': [input_1, input_2],
               'output_image':[output_1, output_2],
              }),
}
