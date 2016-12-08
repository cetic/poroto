#define SOFTENING 1e-9f

#pragma poroto file src sqrt.vhdl
#pragma poroto file ipcore_dir sqrt_impl/sqrt_impl.xco
#pragma poroto latency 28
void sqrt(float a, float &result);

#pragma poroto memory x float 1024
#pragma poroto memory y float 1024
#pragma poroto memory z float 1024
#pragma poroto memory xp float 1024
#pragma poroto memory yp float 1024
#pragma poroto memory zp float 1024
#pragma poroto memory vx_in float 1024
#pragma poroto memory vy_in float 1024
#pragma poroto memory vz_in float 1024
#pragma poroto memory vx_out float 1024
#pragma poroto memory vy_out float 1024
#pragma poroto memory vz_out float 1024

#pragma poroto stream::roccc_bram_in nbody::x(x, n)
#pragma poroto stream::roccc_bram_in nbody::y(y, n)
#pragma poroto stream::roccc_bram_in nbody::z(z, n)
#pragma poroto stream::roccc_bram_in nbody::xp(xp, n)
#pragma poroto stream::roccc_bram_in nbody::yp(yp, n)
#pragma poroto stream::roccc_bram_in nbody::zp(zp, n)
#pragma poroto stream::roccc_bram_in nbody::vx_i(vx_in, n)
#pragma poroto stream::roccc_bram_in nbody::vy_i(vy_in, n)
#pragma poroto stream::roccc_bram_in nbody::vz_i(vz_in, n)
#pragma poroto stream::roccc_bram_out nbody::vx_o(vx_out, n)
#pragma poroto stream::roccc_bram_out nbody::vy_o(vy_out, n)
#pragma poroto stream::roccc_bram_out nbody::vz_o(vz_out, n)

#pragma poroto roccc CopyReduction disable

void nbody(float *x,float *y,float *z, float *xp,float *yp,float *zp, float *vx_i,float *vy_i,float *vz_i, float *vx_o,float *vy_o,float *vz_o, float dt, int n) {
  int i;
  int j;
  float Fx;
  float Fy;
  float Fz;

  for (i = 0; i < n; i++) {
    Fx = 0.0f;
    Fy = 0.0f;
    Fz = 0.0f;
    for (j = 0; j < n; j++) {
      float dx = xp[j] - x[i];
      float dy = yp[j] - y[i];
      float dz = zp[j] - z[i];
      float distSqr = dx*dx + dy*dy + dz*dz + SOFTENING;
      float sqrVal;
      sqrt(distSqr, sqrVal);
      float invDist = 1.0f / sqrVal;
      float invDist3 = invDist * invDist * invDist;
      Fx = Fx + dx * invDist3;
      Fy = Fy + dy * invDist3;
      Fz = Fz + dz * invDist3;
    }
    vx_o[i] = vx_i[i] + dt*Fx;
    vy_o[i] = vy_i[i] + dt*Fy;
    vz_o[i] = vz_i[i] + dt*Fz;
  }
}
