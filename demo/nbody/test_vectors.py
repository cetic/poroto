from poroto.test import TestVector
from random import random
from math import sqrt

N=30
SOFTENING=1e-9
dt=1.0

x=[random() for i in xrange(N)]
y=[random() for i in xrange(N)]
z=[random() for i in xrange(N)]

vx_in=[random() for i in xrange(N)]
vy_in=[random() for i in xrange(N)]
vz_in=[random() for i in xrange(N)]

vx_out=range(N)
vy_out=range(N)
vz_out=range(N)

for i in xrange(N):
    for j in xrange(N):
        dx = x[j] - x[i]
        dy = y[j] - y[i]
        dz = z[j] - z[i]
        distSqr = dx*dx + dy*dy + dz*dz + SOFTENING
        sqrVal = sqrt(distSqr)
        invDist = 1.0 / sqrVal
        invDist3 = invDist * invDist * invDist
        if(j == 0):
            Fx = 0.0
            Fy = 0.0
            Fz = 0.0
        Fx = Fx + dx * invDist3
        Fy = Fy + dy * invDist3
        Fz = Fz + dz * invDist3
        vx_out[i] = vx_in[i] + dt*Fx
        vy_out[i] = vy_in[i] + dt*Fy
        vz_out[i] = vz_in[i] + dt*Fz
    
test_vectors = {
 'nbody':
 TestVector(1,{
               'n':  [N],
               'dt': [dt],
               'x': [x],
               'y': [y],
               'z': [z],
               'xp': [x],
               'yp': [y],
               'zp': [z],
               'vx_i': [vx_in],
               'vy_i': [vy_in],
               'vz_i': [vz_in],
               'vx_o': [vx_out],
               'vy_o': [vy_out],
               'vz_o': [vz_out],
              }),
}
