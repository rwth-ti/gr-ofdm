#ifdef HAVE_CONFIG_H
#include "config.h"
#endif

//#include <gnuradio/math.h>
#include <ofdm/ofdmi_mod.h>
#include <gnuradio/expj.h>

#include <vector>
#include <algorithm>
#include <iostream>

// gray coded psk
void ofdmi_make_psk(std::vector<gr_complex> &constellation, unsigned char bits)
{
  assert(bits == 1 || bits == 2 || bits == 3);

  // special case: BSPK
  if(bits == 1) {
    constellation.clear();
    constellation.push_back(gr_complex(1,0));
    constellation.push_back(gr_complex(-1,0));
    return;
  }

  // special case: QPSK
  if(bits == 2) {
    constellation.clear();
    float x = 1.0 / sqrt(2.0);
    constellation.push_back(gr_complex(-x,x));
    constellation.push_back(gr_complex(-x,-x));
    constellation.push_back(gr_complex(x,x));
    constellation.push_back(gr_complex(x,-x));
    return;
  }

  float num_sym = pow(2, bits);
  std::vector<gr_complex> c(static_cast<size_t>(num_sym));

  const int binary_to_gray[] = { 0,1,3,2,6,7,5,4 };

  for(int sym = 0; sym < num_sym; ++sym) {
    c[binary_to_gray[sym]] = gr_expj(static_cast<float>(sym) / num_sym * 2*M_PI);
  }

  constellation = c;
}

/*
simconst = init_simulation();
for i = 1:length(simconst.Constellation{n})
disp(sprintf('constellation.push_back(gr_complex(%+.8e,%+.8e));',real(simconst.Constellation{n}(i)),imag(simconst.Constellation{n}(i))))
end
*/

// gray-coded 16 Square-QAM, average power = 1.0
void ofdmi_make_16qam(std::vector<gr_complex> &constellation)
{
  constellation.push_back(gr_complex(-9.48683298e-01,+9.48683298e-01));
  constellation.push_back(gr_complex(-9.48683298e-01,+3.16227766e-01));
  constellation.push_back(gr_complex(-9.48683298e-01,-9.48683298e-01));
  constellation.push_back(gr_complex(-9.48683298e-01,-3.16227766e-01));
  constellation.push_back(gr_complex(-3.16227766e-01,+9.48683298e-01));
  constellation.push_back(gr_complex(-3.16227766e-01,+3.16227766e-01));
  constellation.push_back(gr_complex(-3.16227766e-01,-9.48683298e-01));
  constellation.push_back(gr_complex(-3.16227766e-01,-3.16227766e-01));
  constellation.push_back(gr_complex(+9.48683298e-01,+9.48683298e-01));
  constellation.push_back(gr_complex(+9.48683298e-01,+3.16227766e-01));
  constellation.push_back(gr_complex(+9.48683298e-01,-9.48683298e-01));
  constellation.push_back(gr_complex(+9.48683298e-01,-3.16227766e-01));
  constellation.push_back(gr_complex(+3.16227766e-01,+9.48683298e-01));
  constellation.push_back(gr_complex(+3.16227766e-01,+3.16227766e-01));
  constellation.push_back(gr_complex(+3.16227766e-01,-9.48683298e-01));
  constellation.push_back(gr_complex(+3.16227766e-01,-3.16227766e-01));
}

// gray-coded 32 Cross-QAM, average power = 1.0
void ofdmi_make_32qam(std::vector<gr_complex> &constellation)
{
  constellation.push_back(gr_complex(-6.70820393e-01,+1.11803399e+00));
  constellation.push_back(gr_complex(-2.23606798e-01,+1.11803399e+00));
  constellation.push_back(gr_complex(-6.70820393e-01,-1.11803399e+00));
  constellation.push_back(gr_complex(-2.23606798e-01,-1.11803399e+00));
  constellation.push_back(gr_complex(-1.11803399e+00,+6.70820393e-01));
  constellation.push_back(gr_complex(-1.11803399e+00,+2.23606798e-01));
  constellation.push_back(gr_complex(-1.11803399e+00,-6.70820393e-01));
  constellation.push_back(gr_complex(-1.11803399e+00,-2.23606798e-01));
  constellation.push_back(gr_complex(-2.23606798e-01,+6.70820393e-01));
  constellation.push_back(gr_complex(-2.23606798e-01,+2.23606798e-01));
  constellation.push_back(gr_complex(-2.23606798e-01,-6.70820393e-01));
  constellation.push_back(gr_complex(-2.23606798e-01,-2.23606798e-01));
  constellation.push_back(gr_complex(-6.70820393e-01,+6.70820393e-01));
  constellation.push_back(gr_complex(-6.70820393e-01,+2.23606798e-01));
  constellation.push_back(gr_complex(-6.70820393e-01,-6.70820393e-01));
  constellation.push_back(gr_complex(-6.70820393e-01,-2.23606798e-01));
  constellation.push_back(gr_complex(+6.70820393e-01,+1.11803399e+00));
  constellation.push_back(gr_complex(+2.23606798e-01,+1.11803399e+00));
  constellation.push_back(gr_complex(+6.70820393e-01,-1.11803399e+00));
  constellation.push_back(gr_complex(+2.23606798e-01,-1.11803399e+00));
  constellation.push_back(gr_complex(+1.11803399e+00,+6.70820393e-01));
  constellation.push_back(gr_complex(+1.11803399e+00,+2.23606798e-01));
  constellation.push_back(gr_complex(+1.11803399e+00,-6.70820393e-01));
  constellation.push_back(gr_complex(+1.11803399e+00,-2.23606798e-01));
  constellation.push_back(gr_complex(+2.23606798e-01,+6.70820393e-01));
  constellation.push_back(gr_complex(+2.23606798e-01,+2.23606798e-01));
  constellation.push_back(gr_complex(+2.23606798e-01,-6.70820393e-01));
  constellation.push_back(gr_complex(+2.23606798e-01,-2.23606798e-01));
  constellation.push_back(gr_complex(+6.70820393e-01,+6.70820393e-01));
  constellation.push_back(gr_complex(+6.70820393e-01,+2.23606798e-01));
  constellation.push_back(gr_complex(+6.70820393e-01,-6.70820393e-01));
  constellation.push_back(gr_complex(+6.70820393e-01,-2.23606798e-01));
}

// gray-coded 64 Square-QAM, average power = 1.0
void ofdmi_make_64qam(std::vector<gr_complex> &constellation)
{
  constellation.push_back(gr_complex(-1.08012345e+00,+1.08012345e+00));
  constellation.push_back(gr_complex(-1.08012345e+00,+7.71516750e-01));
  constellation.push_back(gr_complex(-1.08012345e+00,+1.54303350e-01));
  constellation.push_back(gr_complex(-1.08012345e+00,+4.62910050e-01));
  constellation.push_back(gr_complex(-1.08012345e+00,-1.08012345e+00));
  constellation.push_back(gr_complex(-1.08012345e+00,-7.71516750e-01));
  constellation.push_back(gr_complex(-1.08012345e+00,-1.54303350e-01));
  constellation.push_back(gr_complex(-1.08012345e+00,-4.62910050e-01));
  constellation.push_back(gr_complex(-7.71516750e-01,+1.08012345e+00));
  constellation.push_back(gr_complex(-7.71516750e-01,+7.71516750e-01));
  constellation.push_back(gr_complex(-7.71516750e-01,+1.54303350e-01));
  constellation.push_back(gr_complex(-7.71516750e-01,+4.62910050e-01));
  constellation.push_back(gr_complex(-7.71516750e-01,-1.08012345e+00));
  constellation.push_back(gr_complex(-7.71516750e-01,-7.71516750e-01));
  constellation.push_back(gr_complex(-7.71516750e-01,-1.54303350e-01));
  constellation.push_back(gr_complex(-7.71516750e-01,-4.62910050e-01));
  constellation.push_back(gr_complex(-1.54303350e-01,+1.08012345e+00));
  constellation.push_back(gr_complex(-1.54303350e-01,+7.71516750e-01));
  constellation.push_back(gr_complex(-1.54303350e-01,+1.54303350e-01));
  constellation.push_back(gr_complex(-1.54303350e-01,+4.62910050e-01));
  constellation.push_back(gr_complex(-1.54303350e-01,-1.08012345e+00));
  constellation.push_back(gr_complex(-1.54303350e-01,-7.71516750e-01));
  constellation.push_back(gr_complex(-1.54303350e-01,-1.54303350e-01));
  constellation.push_back(gr_complex(-1.54303350e-01,-4.62910050e-01));
  constellation.push_back(gr_complex(-4.62910050e-01,+1.08012345e+00));
  constellation.push_back(gr_complex(-4.62910050e-01,+7.71516750e-01));
  constellation.push_back(gr_complex(-4.62910050e-01,+1.54303350e-01));
  constellation.push_back(gr_complex(-4.62910050e-01,+4.62910050e-01));
  constellation.push_back(gr_complex(-4.62910050e-01,-1.08012345e+00));
  constellation.push_back(gr_complex(-4.62910050e-01,-7.71516750e-01));
  constellation.push_back(gr_complex(-4.62910050e-01,-1.54303350e-01));
  constellation.push_back(gr_complex(-4.62910050e-01,-4.62910050e-01));
  constellation.push_back(gr_complex(+1.08012345e+00,+1.08012345e+00));
  constellation.push_back(gr_complex(+1.08012345e+00,+7.71516750e-01));
  constellation.push_back(gr_complex(+1.08012345e+00,+1.54303350e-01));
  constellation.push_back(gr_complex(+1.08012345e+00,+4.62910050e-01));
  constellation.push_back(gr_complex(+1.08012345e+00,-1.08012345e+00));
  constellation.push_back(gr_complex(+1.08012345e+00,-7.71516750e-01));
  constellation.push_back(gr_complex(+1.08012345e+00,-1.54303350e-01));
  constellation.push_back(gr_complex(+1.08012345e+00,-4.62910050e-01));
  constellation.push_back(gr_complex(+7.71516750e-01,+1.08012345e+00));
  constellation.push_back(gr_complex(+7.71516750e-01,+7.71516750e-01));
  constellation.push_back(gr_complex(+7.71516750e-01,+1.54303350e-01));
  constellation.push_back(gr_complex(+7.71516750e-01,+4.62910050e-01));
  constellation.push_back(gr_complex(+7.71516750e-01,-1.08012345e+00));
  constellation.push_back(gr_complex(+7.71516750e-01,-7.71516750e-01));
  constellation.push_back(gr_complex(+7.71516750e-01,-1.54303350e-01));
  constellation.push_back(gr_complex(+7.71516750e-01,-4.62910050e-01));
  constellation.push_back(gr_complex(+1.54303350e-01,+1.08012345e+00));
  constellation.push_back(gr_complex(+1.54303350e-01,+7.71516750e-01));
  constellation.push_back(gr_complex(+1.54303350e-01,+1.54303350e-01));
  constellation.push_back(gr_complex(+1.54303350e-01,+4.62910050e-01));
  constellation.push_back(gr_complex(+1.54303350e-01,-1.08012345e+00));
  constellation.push_back(gr_complex(+1.54303350e-01,-7.71516750e-01));
  constellation.push_back(gr_complex(+1.54303350e-01,-1.54303350e-01));
  constellation.push_back(gr_complex(+1.54303350e-01,-4.62910050e-01));
  constellation.push_back(gr_complex(+4.62910050e-01,+1.08012345e+00));
  constellation.push_back(gr_complex(+4.62910050e-01,+7.71516750e-01));
  constellation.push_back(gr_complex(+4.62910050e-01,+1.54303350e-01));
  constellation.push_back(gr_complex(+4.62910050e-01,+4.62910050e-01));
  constellation.push_back(gr_complex(+4.62910050e-01,-1.08012345e+00));
  constellation.push_back(gr_complex(+4.62910050e-01,-7.71516750e-01));
  constellation.push_back(gr_complex(+4.62910050e-01,-1.54303350e-01));
  constellation.push_back(gr_complex(+4.62910050e-01,-4.62910050e-01));
}

// gray-coded 128 Cross-QAM, average power = 1.0
void ofdmi_make_128qam(std::vector<gr_complex> &constellation)
{
  constellation.push_back(gr_complex(-7.73020683e-01,+9.93883735e-01));
  constellation.push_back(gr_complex(-7.73020683e-01,+1.21474679e+00));
  constellation.push_back(gr_complex(-1.10431526e-01,+9.93883735e-01));
  constellation.push_back(gr_complex(-1.10431526e-01,+1.21474679e+00));
  constellation.push_back(gr_complex(-7.73020683e-01,-9.93883735e-01));
  constellation.push_back(gr_complex(-7.73020683e-01,-1.21474679e+00));
  constellation.push_back(gr_complex(-1.10431526e-01,-9.93883735e-01));
  constellation.push_back(gr_complex(-1.10431526e-01,-1.21474679e+00));
  constellation.push_back(gr_complex(-5.52157630e-01,+9.93883735e-01));
  constellation.push_back(gr_complex(-5.52157630e-01,+1.21474679e+00));
  constellation.push_back(gr_complex(-3.31294578e-01,+9.93883735e-01));
  constellation.push_back(gr_complex(-3.31294578e-01,+1.21474679e+00));
  constellation.push_back(gr_complex(-5.52157630e-01,-9.93883735e-01));
  constellation.push_back(gr_complex(-5.52157630e-01,-1.21474679e+00));
  constellation.push_back(gr_complex(-3.31294578e-01,-9.93883735e-01));
  constellation.push_back(gr_complex(-3.31294578e-01,-1.21474679e+00));
  constellation.push_back(gr_complex(-9.93883735e-01,+7.73020683e-01));
  constellation.push_back(gr_complex(-9.93883735e-01,+5.52157630e-01));
  constellation.push_back(gr_complex(-9.93883735e-01,+1.10431526e-01));
  constellation.push_back(gr_complex(-9.93883735e-01,+3.31294578e-01));
  constellation.push_back(gr_complex(-9.93883735e-01,-7.73020683e-01));
  constellation.push_back(gr_complex(-9.93883735e-01,-5.52157630e-01));
  constellation.push_back(gr_complex(-9.93883735e-01,-1.10431526e-01));
  constellation.push_back(gr_complex(-9.93883735e-01,-3.31294578e-01));
  constellation.push_back(gr_complex(-1.21474679e+00,+7.73020683e-01));
  constellation.push_back(gr_complex(-1.21474679e+00,+5.52157630e-01));
  constellation.push_back(gr_complex(-1.21474679e+00,+1.10431526e-01));
  constellation.push_back(gr_complex(-1.21474679e+00,+3.31294578e-01));
  constellation.push_back(gr_complex(-1.21474679e+00,-7.73020683e-01));
  constellation.push_back(gr_complex(-1.21474679e+00,-5.52157630e-01));
  constellation.push_back(gr_complex(-1.21474679e+00,-1.10431526e-01));
  constellation.push_back(gr_complex(-1.21474679e+00,-3.31294578e-01));
  constellation.push_back(gr_complex(-1.10431526e-01,+7.73020683e-01));
  constellation.push_back(gr_complex(-1.10431526e-01,+5.52157630e-01));
  constellation.push_back(gr_complex(-1.10431526e-01,+1.10431526e-01));
  constellation.push_back(gr_complex(-1.10431526e-01,+3.31294578e-01));
  constellation.push_back(gr_complex(-1.10431526e-01,-7.73020683e-01));
  constellation.push_back(gr_complex(-1.10431526e-01,-5.52157630e-01));
  constellation.push_back(gr_complex(-1.10431526e-01,-1.10431526e-01));
  constellation.push_back(gr_complex(-1.10431526e-01,-3.31294578e-01));
  constellation.push_back(gr_complex(-3.31294578e-01,+7.73020683e-01));
  constellation.push_back(gr_complex(-3.31294578e-01,+5.52157630e-01));
  constellation.push_back(gr_complex(-3.31294578e-01,+1.10431526e-01));
  constellation.push_back(gr_complex(-3.31294578e-01,+3.31294578e-01));
  constellation.push_back(gr_complex(-3.31294578e-01,-7.73020683e-01));
  constellation.push_back(gr_complex(-3.31294578e-01,-5.52157630e-01));
  constellation.push_back(gr_complex(-3.31294578e-01,-1.10431526e-01));
  constellation.push_back(gr_complex(-3.31294578e-01,-3.31294578e-01));
  constellation.push_back(gr_complex(-7.73020683e-01,+7.73020683e-01));
  constellation.push_back(gr_complex(-7.73020683e-01,+5.52157630e-01));
  constellation.push_back(gr_complex(-7.73020683e-01,+1.10431526e-01));
  constellation.push_back(gr_complex(-7.73020683e-01,+3.31294578e-01));
  constellation.push_back(gr_complex(-7.73020683e-01,-7.73020683e-01));
  constellation.push_back(gr_complex(-7.73020683e-01,-5.52157630e-01));
  constellation.push_back(gr_complex(-7.73020683e-01,-1.10431526e-01));
  constellation.push_back(gr_complex(-7.73020683e-01,-3.31294578e-01));
  constellation.push_back(gr_complex(-5.52157630e-01,+7.73020683e-01));
  constellation.push_back(gr_complex(-5.52157630e-01,+5.52157630e-01));
  constellation.push_back(gr_complex(-5.52157630e-01,+1.10431526e-01));
  constellation.push_back(gr_complex(-5.52157630e-01,+3.31294578e-01));
  constellation.push_back(gr_complex(-5.52157630e-01,-7.73020683e-01));
  constellation.push_back(gr_complex(-5.52157630e-01,-5.52157630e-01));
  constellation.push_back(gr_complex(-5.52157630e-01,-1.10431526e-01));
  constellation.push_back(gr_complex(-5.52157630e-01,-3.31294578e-01));
  constellation.push_back(gr_complex(+7.73020683e-01,+9.93883735e-01));
  constellation.push_back(gr_complex(+7.73020683e-01,+1.21474679e+00));
  constellation.push_back(gr_complex(+1.10431526e-01,+9.93883735e-01));
  constellation.push_back(gr_complex(+1.10431526e-01,+1.21474679e+00));
  constellation.push_back(gr_complex(+7.73020683e-01,-9.93883735e-01));
  constellation.push_back(gr_complex(+7.73020683e-01,-1.21474679e+00));
  constellation.push_back(gr_complex(+1.10431526e-01,-9.93883735e-01));
  constellation.push_back(gr_complex(+1.10431526e-01,-1.21474679e+00));
  constellation.push_back(gr_complex(+5.52157630e-01,+9.93883735e-01));
  constellation.push_back(gr_complex(+5.52157630e-01,+1.21474679e+00));
  constellation.push_back(gr_complex(+3.31294578e-01,+9.93883735e-01));
  constellation.push_back(gr_complex(+3.31294578e-01,+1.21474679e+00));
  constellation.push_back(gr_complex(+5.52157630e-01,-9.93883735e-01));
  constellation.push_back(gr_complex(+5.52157630e-01,-1.21474679e+00));
  constellation.push_back(gr_complex(+3.31294578e-01,-9.93883735e-01));
  constellation.push_back(gr_complex(+3.31294578e-01,-1.21474679e+00));
  constellation.push_back(gr_complex(+9.93883735e-01,+7.73020683e-01));
  constellation.push_back(gr_complex(+9.93883735e-01,+5.52157630e-01));
  constellation.push_back(gr_complex(+9.93883735e-01,+1.10431526e-01));
  constellation.push_back(gr_complex(+9.93883735e-01,+3.31294578e-01));
  constellation.push_back(gr_complex(+9.93883735e-01,-7.73020683e-01));
  constellation.push_back(gr_complex(+9.93883735e-01,-5.52157630e-01));
  constellation.push_back(gr_complex(+9.93883735e-01,-1.10431526e-01));
  constellation.push_back(gr_complex(+9.93883735e-01,-3.31294578e-01));
  constellation.push_back(gr_complex(+1.21474679e+00,+7.73020683e-01));
  constellation.push_back(gr_complex(+1.21474679e+00,+5.52157630e-01));
  constellation.push_back(gr_complex(+1.21474679e+00,+1.10431526e-01));
  constellation.push_back(gr_complex(+1.21474679e+00,+3.31294578e-01));
  constellation.push_back(gr_complex(+1.21474679e+00,-7.73020683e-01));
  constellation.push_back(gr_complex(+1.21474679e+00,-5.52157630e-01));
  constellation.push_back(gr_complex(+1.21474679e+00,-1.10431526e-01));
  constellation.push_back(gr_complex(+1.21474679e+00,-3.31294578e-01));
  constellation.push_back(gr_complex(+1.10431526e-01,+7.73020683e-01));
  constellation.push_back(gr_complex(+1.10431526e-01,+5.52157630e-01));
  constellation.push_back(gr_complex(+1.10431526e-01,+1.10431526e-01));
  constellation.push_back(gr_complex(+1.10431526e-01,+3.31294578e-01));
  constellation.push_back(gr_complex(+1.10431526e-01,-7.73020683e-01));
  constellation.push_back(gr_complex(+1.10431526e-01,-5.52157630e-01));
  constellation.push_back(gr_complex(+1.10431526e-01,-1.10431526e-01));
  constellation.push_back(gr_complex(+1.10431526e-01,-3.31294578e-01));
  constellation.push_back(gr_complex(+3.31294578e-01,+7.73020683e-01));
  constellation.push_back(gr_complex(+3.31294578e-01,+5.52157630e-01));
  constellation.push_back(gr_complex(+3.31294578e-01,+1.10431526e-01));
  constellation.push_back(gr_complex(+3.31294578e-01,+3.31294578e-01));
  constellation.push_back(gr_complex(+3.31294578e-01,-7.73020683e-01));
  constellation.push_back(gr_complex(+3.31294578e-01,-5.52157630e-01));
  constellation.push_back(gr_complex(+3.31294578e-01,-1.10431526e-01));
  constellation.push_back(gr_complex(+3.31294578e-01,-3.31294578e-01));
  constellation.push_back(gr_complex(+7.73020683e-01,+7.73020683e-01));
  constellation.push_back(gr_complex(+7.73020683e-01,+5.52157630e-01));
  constellation.push_back(gr_complex(+7.73020683e-01,+1.10431526e-01));
  constellation.push_back(gr_complex(+7.73020683e-01,+3.31294578e-01));
  constellation.push_back(gr_complex(+7.73020683e-01,-7.73020683e-01));
  constellation.push_back(gr_complex(+7.73020683e-01,-5.52157630e-01));
  constellation.push_back(gr_complex(+7.73020683e-01,-1.10431526e-01));
  constellation.push_back(gr_complex(+7.73020683e-01,-3.31294578e-01));
  constellation.push_back(gr_complex(+5.52157630e-01,+7.73020683e-01));
  constellation.push_back(gr_complex(+5.52157630e-01,+5.52157630e-01));
  constellation.push_back(gr_complex(+5.52157630e-01,+1.10431526e-01));
  constellation.push_back(gr_complex(+5.52157630e-01,+3.31294578e-01));
  constellation.push_back(gr_complex(+5.52157630e-01,-7.73020683e-01));
  constellation.push_back(gr_complex(+5.52157630e-01,-5.52157630e-01));
  constellation.push_back(gr_complex(+5.52157630e-01,-1.10431526e-01));
  constellation.push_back(gr_complex(+5.52157630e-01,-3.31294578e-01));
}

// gray-coded 256 Square-QAM, average power = 1.0
void ofdmi_make_256qam(std::vector<gr_complex> &constellation)
{
  constellation.push_back(gr_complex(-1.15044748e+00,+1.15044748e+00));
  constellation.push_back(gr_complex(-1.15044748e+00,+9.97054486e-01));
  constellation.push_back(gr_complex(-1.15044748e+00,+6.90268490e-01));
  constellation.push_back(gr_complex(-1.15044748e+00,+8.43661488e-01));
  constellation.push_back(gr_complex(-1.15044748e+00,+7.66964989e-02));
  constellation.push_back(gr_complex(-1.15044748e+00,+2.30089497e-01));
  constellation.push_back(gr_complex(-1.15044748e+00,+5.36875492e-01));
  constellation.push_back(gr_complex(-1.15044748e+00,+3.83482494e-01));
  constellation.push_back(gr_complex(-1.15044748e+00,-1.15044748e+00));
  constellation.push_back(gr_complex(-1.15044748e+00,-9.97054486e-01));
  constellation.push_back(gr_complex(-1.15044748e+00,-6.90268490e-01));
  constellation.push_back(gr_complex(-1.15044748e+00,-8.43661488e-01));
  constellation.push_back(gr_complex(-1.15044748e+00,-7.66964989e-02));
  constellation.push_back(gr_complex(-1.15044748e+00,-2.30089497e-01));
  constellation.push_back(gr_complex(-1.15044748e+00,-5.36875492e-01));
  constellation.push_back(gr_complex(-1.15044748e+00,-3.83482494e-01));
  constellation.push_back(gr_complex(-9.97054486e-01,+1.15044748e+00));
  constellation.push_back(gr_complex(-9.97054486e-01,+9.97054486e-01));
  constellation.push_back(gr_complex(-9.97054486e-01,+6.90268490e-01));
  constellation.push_back(gr_complex(-9.97054486e-01,+8.43661488e-01));
  constellation.push_back(gr_complex(-9.97054486e-01,+7.66964989e-02));
  constellation.push_back(gr_complex(-9.97054486e-01,+2.30089497e-01));
  constellation.push_back(gr_complex(-9.97054486e-01,+5.36875492e-01));
  constellation.push_back(gr_complex(-9.97054486e-01,+3.83482494e-01));
  constellation.push_back(gr_complex(-9.97054486e-01,-1.15044748e+00));
  constellation.push_back(gr_complex(-9.97054486e-01,-9.97054486e-01));
  constellation.push_back(gr_complex(-9.97054486e-01,-6.90268490e-01));
  constellation.push_back(gr_complex(-9.97054486e-01,-8.43661488e-01));
  constellation.push_back(gr_complex(-9.97054486e-01,-7.66964989e-02));
  constellation.push_back(gr_complex(-9.97054486e-01,-2.30089497e-01));
  constellation.push_back(gr_complex(-9.97054486e-01,-5.36875492e-01));
  constellation.push_back(gr_complex(-9.97054486e-01,-3.83482494e-01));
  constellation.push_back(gr_complex(-6.90268490e-01,+1.15044748e+00));
  constellation.push_back(gr_complex(-6.90268490e-01,+9.97054486e-01));
  constellation.push_back(gr_complex(-6.90268490e-01,+6.90268490e-01));
  constellation.push_back(gr_complex(-6.90268490e-01,+8.43661488e-01));
  constellation.push_back(gr_complex(-6.90268490e-01,+7.66964989e-02));
  constellation.push_back(gr_complex(-6.90268490e-01,+2.30089497e-01));
  constellation.push_back(gr_complex(-6.90268490e-01,+5.36875492e-01));
  constellation.push_back(gr_complex(-6.90268490e-01,+3.83482494e-01));
  constellation.push_back(gr_complex(-6.90268490e-01,-1.15044748e+00));
  constellation.push_back(gr_complex(-6.90268490e-01,-9.97054486e-01));
  constellation.push_back(gr_complex(-6.90268490e-01,-6.90268490e-01));
  constellation.push_back(gr_complex(-6.90268490e-01,-8.43661488e-01));
  constellation.push_back(gr_complex(-6.90268490e-01,-7.66964989e-02));
  constellation.push_back(gr_complex(-6.90268490e-01,-2.30089497e-01));
  constellation.push_back(gr_complex(-6.90268490e-01,-5.36875492e-01));
  constellation.push_back(gr_complex(-6.90268490e-01,-3.83482494e-01));
  constellation.push_back(gr_complex(-8.43661488e-01,+1.15044748e+00));
  constellation.push_back(gr_complex(-8.43661488e-01,+9.97054486e-01));
  constellation.push_back(gr_complex(-8.43661488e-01,+6.90268490e-01));
  constellation.push_back(gr_complex(-8.43661488e-01,+8.43661488e-01));
  constellation.push_back(gr_complex(-8.43661488e-01,+7.66964989e-02));
  constellation.push_back(gr_complex(-8.43661488e-01,+2.30089497e-01));
  constellation.push_back(gr_complex(-8.43661488e-01,+5.36875492e-01));
  constellation.push_back(gr_complex(-8.43661488e-01,+3.83482494e-01));
  constellation.push_back(gr_complex(-8.43661488e-01,-1.15044748e+00));
  constellation.push_back(gr_complex(-8.43661488e-01,-9.97054486e-01));
  constellation.push_back(gr_complex(-8.43661488e-01,-6.90268490e-01));
  constellation.push_back(gr_complex(-8.43661488e-01,-8.43661488e-01));
  constellation.push_back(gr_complex(-8.43661488e-01,-7.66964989e-02));
  constellation.push_back(gr_complex(-8.43661488e-01,-2.30089497e-01));
  constellation.push_back(gr_complex(-8.43661488e-01,-5.36875492e-01));
  constellation.push_back(gr_complex(-8.43661488e-01,-3.83482494e-01));
  constellation.push_back(gr_complex(-7.66964989e-02,+1.15044748e+00));
  constellation.push_back(gr_complex(-7.66964989e-02,+9.97054486e-01));
  constellation.push_back(gr_complex(-7.66964989e-02,+6.90268490e-01));
  constellation.push_back(gr_complex(-7.66964989e-02,+8.43661488e-01));
  constellation.push_back(gr_complex(-7.66964989e-02,+7.66964989e-02));
  constellation.push_back(gr_complex(-7.66964989e-02,+2.30089497e-01));
  constellation.push_back(gr_complex(-7.66964989e-02,+5.36875492e-01));
  constellation.push_back(gr_complex(-7.66964989e-02,+3.83482494e-01));
  constellation.push_back(gr_complex(-7.66964989e-02,-1.15044748e+00));
  constellation.push_back(gr_complex(-7.66964989e-02,-9.97054486e-01));
  constellation.push_back(gr_complex(-7.66964989e-02,-6.90268490e-01));
  constellation.push_back(gr_complex(-7.66964989e-02,-8.43661488e-01));
  constellation.push_back(gr_complex(-7.66964989e-02,-7.66964989e-02));
  constellation.push_back(gr_complex(-7.66964989e-02,-2.30089497e-01));
  constellation.push_back(gr_complex(-7.66964989e-02,-5.36875492e-01));
  constellation.push_back(gr_complex(-7.66964989e-02,-3.83482494e-01));
  constellation.push_back(gr_complex(-2.30089497e-01,+1.15044748e+00));
  constellation.push_back(gr_complex(-2.30089497e-01,+9.97054486e-01));
  constellation.push_back(gr_complex(-2.30089497e-01,+6.90268490e-01));
  constellation.push_back(gr_complex(-2.30089497e-01,+8.43661488e-01));
  constellation.push_back(gr_complex(-2.30089497e-01,+7.66964989e-02));
  constellation.push_back(gr_complex(-2.30089497e-01,+2.30089497e-01));
  constellation.push_back(gr_complex(-2.30089497e-01,+5.36875492e-01));
  constellation.push_back(gr_complex(-2.30089497e-01,+3.83482494e-01));
  constellation.push_back(gr_complex(-2.30089497e-01,-1.15044748e+00));
  constellation.push_back(gr_complex(-2.30089497e-01,-9.97054486e-01));
  constellation.push_back(gr_complex(-2.30089497e-01,-6.90268490e-01));
  constellation.push_back(gr_complex(-2.30089497e-01,-8.43661488e-01));
  constellation.push_back(gr_complex(-2.30089497e-01,-7.66964989e-02));
  constellation.push_back(gr_complex(-2.30089497e-01,-2.30089497e-01));
  constellation.push_back(gr_complex(-2.30089497e-01,-5.36875492e-01));
  constellation.push_back(gr_complex(-2.30089497e-01,-3.83482494e-01));
  constellation.push_back(gr_complex(-5.36875492e-01,+1.15044748e+00));
  constellation.push_back(gr_complex(-5.36875492e-01,+9.97054486e-01));
  constellation.push_back(gr_complex(-5.36875492e-01,+6.90268490e-01));
  constellation.push_back(gr_complex(-5.36875492e-01,+8.43661488e-01));
  constellation.push_back(gr_complex(-5.36875492e-01,+7.66964989e-02));
  constellation.push_back(gr_complex(-5.36875492e-01,+2.30089497e-01));
  constellation.push_back(gr_complex(-5.36875492e-01,+5.36875492e-01));
  constellation.push_back(gr_complex(-5.36875492e-01,+3.83482494e-01));
  constellation.push_back(gr_complex(-5.36875492e-01,-1.15044748e+00));
  constellation.push_back(gr_complex(-5.36875492e-01,-9.97054486e-01));
  constellation.push_back(gr_complex(-5.36875492e-01,-6.90268490e-01));
  constellation.push_back(gr_complex(-5.36875492e-01,-8.43661488e-01));
  constellation.push_back(gr_complex(-5.36875492e-01,-7.66964989e-02));
  constellation.push_back(gr_complex(-5.36875492e-01,-2.30089497e-01));
  constellation.push_back(gr_complex(-5.36875492e-01,-5.36875492e-01));
  constellation.push_back(gr_complex(-5.36875492e-01,-3.83482494e-01));
  constellation.push_back(gr_complex(-3.83482494e-01,+1.15044748e+00));
  constellation.push_back(gr_complex(-3.83482494e-01,+9.97054486e-01));
  constellation.push_back(gr_complex(-3.83482494e-01,+6.90268490e-01));
  constellation.push_back(gr_complex(-3.83482494e-01,+8.43661488e-01));
  constellation.push_back(gr_complex(-3.83482494e-01,+7.66964989e-02));
  constellation.push_back(gr_complex(-3.83482494e-01,+2.30089497e-01));
  constellation.push_back(gr_complex(-3.83482494e-01,+5.36875492e-01));
  constellation.push_back(gr_complex(-3.83482494e-01,+3.83482494e-01));
  constellation.push_back(gr_complex(-3.83482494e-01,-1.15044748e+00));
  constellation.push_back(gr_complex(-3.83482494e-01,-9.97054486e-01));
  constellation.push_back(gr_complex(-3.83482494e-01,-6.90268490e-01));
  constellation.push_back(gr_complex(-3.83482494e-01,-8.43661488e-01));
  constellation.push_back(gr_complex(-3.83482494e-01,-7.66964989e-02));
  constellation.push_back(gr_complex(-3.83482494e-01,-2.30089497e-01));
  constellation.push_back(gr_complex(-3.83482494e-01,-5.36875492e-01));
  constellation.push_back(gr_complex(-3.83482494e-01,-3.83482494e-01));
  constellation.push_back(gr_complex(+1.15044748e+00,+1.15044748e+00));
  constellation.push_back(gr_complex(+1.15044748e+00,+9.97054486e-01));
  constellation.push_back(gr_complex(+1.15044748e+00,+6.90268490e-01));
  constellation.push_back(gr_complex(+1.15044748e+00,+8.43661488e-01));
  constellation.push_back(gr_complex(+1.15044748e+00,+7.66964989e-02));
  constellation.push_back(gr_complex(+1.15044748e+00,+2.30089497e-01));
  constellation.push_back(gr_complex(+1.15044748e+00,+5.36875492e-01));
  constellation.push_back(gr_complex(+1.15044748e+00,+3.83482494e-01));
  constellation.push_back(gr_complex(+1.15044748e+00,-1.15044748e+00));
  constellation.push_back(gr_complex(+1.15044748e+00,-9.97054486e-01));
  constellation.push_back(gr_complex(+1.15044748e+00,-6.90268490e-01));
  constellation.push_back(gr_complex(+1.15044748e+00,-8.43661488e-01));
  constellation.push_back(gr_complex(+1.15044748e+00,-7.66964989e-02));
  constellation.push_back(gr_complex(+1.15044748e+00,-2.30089497e-01));
  constellation.push_back(gr_complex(+1.15044748e+00,-5.36875492e-01));
  constellation.push_back(gr_complex(+1.15044748e+00,-3.83482494e-01));
  constellation.push_back(gr_complex(+9.97054486e-01,+1.15044748e+00));
  constellation.push_back(gr_complex(+9.97054486e-01,+9.97054486e-01));
  constellation.push_back(gr_complex(+9.97054486e-01,+6.90268490e-01));
  constellation.push_back(gr_complex(+9.97054486e-01,+8.43661488e-01));
  constellation.push_back(gr_complex(+9.97054486e-01,+7.66964989e-02));
  constellation.push_back(gr_complex(+9.97054486e-01,+2.30089497e-01));
  constellation.push_back(gr_complex(+9.97054486e-01,+5.36875492e-01));
  constellation.push_back(gr_complex(+9.97054486e-01,+3.83482494e-01));
  constellation.push_back(gr_complex(+9.97054486e-01,-1.15044748e+00));
  constellation.push_back(gr_complex(+9.97054486e-01,-9.97054486e-01));
  constellation.push_back(gr_complex(+9.97054486e-01,-6.90268490e-01));
  constellation.push_back(gr_complex(+9.97054486e-01,-8.43661488e-01));
  constellation.push_back(gr_complex(+9.97054486e-01,-7.66964989e-02));
  constellation.push_back(gr_complex(+9.97054486e-01,-2.30089497e-01));
  constellation.push_back(gr_complex(+9.97054486e-01,-5.36875492e-01));
  constellation.push_back(gr_complex(+9.97054486e-01,-3.83482494e-01));
  constellation.push_back(gr_complex(+6.90268490e-01,+1.15044748e+00));
  constellation.push_back(gr_complex(+6.90268490e-01,+9.97054486e-01));
  constellation.push_back(gr_complex(+6.90268490e-01,+6.90268490e-01));
  constellation.push_back(gr_complex(+6.90268490e-01,+8.43661488e-01));
  constellation.push_back(gr_complex(+6.90268490e-01,+7.66964989e-02));
  constellation.push_back(gr_complex(+6.90268490e-01,+2.30089497e-01));
  constellation.push_back(gr_complex(+6.90268490e-01,+5.36875492e-01));
  constellation.push_back(gr_complex(+6.90268490e-01,+3.83482494e-01));
  constellation.push_back(gr_complex(+6.90268490e-01,-1.15044748e+00));
  constellation.push_back(gr_complex(+6.90268490e-01,-9.97054486e-01));
  constellation.push_back(gr_complex(+6.90268490e-01,-6.90268490e-01));
  constellation.push_back(gr_complex(+6.90268490e-01,-8.43661488e-01));
  constellation.push_back(gr_complex(+6.90268490e-01,-7.66964989e-02));
  constellation.push_back(gr_complex(+6.90268490e-01,-2.30089497e-01));
  constellation.push_back(gr_complex(+6.90268490e-01,-5.36875492e-01));
  constellation.push_back(gr_complex(+6.90268490e-01,-3.83482494e-01));
  constellation.push_back(gr_complex(+8.43661488e-01,+1.15044748e+00));
  constellation.push_back(gr_complex(+8.43661488e-01,+9.97054486e-01));
  constellation.push_back(gr_complex(+8.43661488e-01,+6.90268490e-01));
  constellation.push_back(gr_complex(+8.43661488e-01,+8.43661488e-01));
  constellation.push_back(gr_complex(+8.43661488e-01,+7.66964989e-02));
  constellation.push_back(gr_complex(+8.43661488e-01,+2.30089497e-01));
  constellation.push_back(gr_complex(+8.43661488e-01,+5.36875492e-01));
  constellation.push_back(gr_complex(+8.43661488e-01,+3.83482494e-01));
  constellation.push_back(gr_complex(+8.43661488e-01,-1.15044748e+00));
  constellation.push_back(gr_complex(+8.43661488e-01,-9.97054486e-01));
  constellation.push_back(gr_complex(+8.43661488e-01,-6.90268490e-01));
  constellation.push_back(gr_complex(+8.43661488e-01,-8.43661488e-01));
  constellation.push_back(gr_complex(+8.43661488e-01,-7.66964989e-02));
  constellation.push_back(gr_complex(+8.43661488e-01,-2.30089497e-01));
  constellation.push_back(gr_complex(+8.43661488e-01,-5.36875492e-01));
  constellation.push_back(gr_complex(+8.43661488e-01,-3.83482494e-01));
  constellation.push_back(gr_complex(+7.66964989e-02,+1.15044748e+00));
  constellation.push_back(gr_complex(+7.66964989e-02,+9.97054486e-01));
  constellation.push_back(gr_complex(+7.66964989e-02,+6.90268490e-01));
  constellation.push_back(gr_complex(+7.66964989e-02,+8.43661488e-01));
  constellation.push_back(gr_complex(+7.66964989e-02,+7.66964989e-02));
  constellation.push_back(gr_complex(+7.66964989e-02,+2.30089497e-01));
  constellation.push_back(gr_complex(+7.66964989e-02,+5.36875492e-01));
  constellation.push_back(gr_complex(+7.66964989e-02,+3.83482494e-01));
  constellation.push_back(gr_complex(+7.66964989e-02,-1.15044748e+00));
  constellation.push_back(gr_complex(+7.66964989e-02,-9.97054486e-01));
  constellation.push_back(gr_complex(+7.66964989e-02,-6.90268490e-01));
  constellation.push_back(gr_complex(+7.66964989e-02,-8.43661488e-01));
  constellation.push_back(gr_complex(+7.66964989e-02,-7.66964989e-02));
  constellation.push_back(gr_complex(+7.66964989e-02,-2.30089497e-01));
  constellation.push_back(gr_complex(+7.66964989e-02,-5.36875492e-01));
  constellation.push_back(gr_complex(+7.66964989e-02,-3.83482494e-01));
  constellation.push_back(gr_complex(+2.30089497e-01,+1.15044748e+00));
  constellation.push_back(gr_complex(+2.30089497e-01,+9.97054486e-01));
  constellation.push_back(gr_complex(+2.30089497e-01,+6.90268490e-01));
  constellation.push_back(gr_complex(+2.30089497e-01,+8.43661488e-01));
  constellation.push_back(gr_complex(+2.30089497e-01,+7.66964989e-02));
  constellation.push_back(gr_complex(+2.30089497e-01,+2.30089497e-01));
  constellation.push_back(gr_complex(+2.30089497e-01,+5.36875492e-01));
  constellation.push_back(gr_complex(+2.30089497e-01,+3.83482494e-01));
  constellation.push_back(gr_complex(+2.30089497e-01,-1.15044748e+00));
  constellation.push_back(gr_complex(+2.30089497e-01,-9.97054486e-01));
  constellation.push_back(gr_complex(+2.30089497e-01,-6.90268490e-01));
  constellation.push_back(gr_complex(+2.30089497e-01,-8.43661488e-01));
  constellation.push_back(gr_complex(+2.30089497e-01,-7.66964989e-02));
  constellation.push_back(gr_complex(+2.30089497e-01,-2.30089497e-01));
  constellation.push_back(gr_complex(+2.30089497e-01,-5.36875492e-01));
  constellation.push_back(gr_complex(+2.30089497e-01,-3.83482494e-01));
  constellation.push_back(gr_complex(+5.36875492e-01,+1.15044748e+00));
  constellation.push_back(gr_complex(+5.36875492e-01,+9.97054486e-01));
  constellation.push_back(gr_complex(+5.36875492e-01,+6.90268490e-01));
  constellation.push_back(gr_complex(+5.36875492e-01,+8.43661488e-01));
  constellation.push_back(gr_complex(+5.36875492e-01,+7.66964989e-02));
  constellation.push_back(gr_complex(+5.36875492e-01,+2.30089497e-01));
  constellation.push_back(gr_complex(+5.36875492e-01,+5.36875492e-01));
  constellation.push_back(gr_complex(+5.36875492e-01,+3.83482494e-01));
  constellation.push_back(gr_complex(+5.36875492e-01,-1.15044748e+00));
  constellation.push_back(gr_complex(+5.36875492e-01,-9.97054486e-01));
  constellation.push_back(gr_complex(+5.36875492e-01,-6.90268490e-01));
  constellation.push_back(gr_complex(+5.36875492e-01,-8.43661488e-01));
  constellation.push_back(gr_complex(+5.36875492e-01,-7.66964989e-02));
  constellation.push_back(gr_complex(+5.36875492e-01,-2.30089497e-01));
  constellation.push_back(gr_complex(+5.36875492e-01,-5.36875492e-01));
  constellation.push_back(gr_complex(+5.36875492e-01,-3.83482494e-01));
  constellation.push_back(gr_complex(+3.83482494e-01,+1.15044748e+00));
  constellation.push_back(gr_complex(+3.83482494e-01,+9.97054486e-01));
  constellation.push_back(gr_complex(+3.83482494e-01,+6.90268490e-01));
  constellation.push_back(gr_complex(+3.83482494e-01,+8.43661488e-01));
  constellation.push_back(gr_complex(+3.83482494e-01,+7.66964989e-02));
  constellation.push_back(gr_complex(+3.83482494e-01,+2.30089497e-01));
  constellation.push_back(gr_complex(+3.83482494e-01,+5.36875492e-01));
  constellation.push_back(gr_complex(+3.83482494e-01,+3.83482494e-01));
  constellation.push_back(gr_complex(+3.83482494e-01,-1.15044748e+00));
  constellation.push_back(gr_complex(+3.83482494e-01,-9.97054486e-01));
  constellation.push_back(gr_complex(+3.83482494e-01,-6.90268490e-01));
  constellation.push_back(gr_complex(+3.83482494e-01,-8.43661488e-01));
  constellation.push_back(gr_complex(+3.83482494e-01,-7.66964989e-02));
  constellation.push_back(gr_complex(+3.83482494e-01,-2.30089497e-01));
  constellation.push_back(gr_complex(+3.83482494e-01,-5.36875492e-01));
  constellation.push_back(gr_complex(+3.83482494e-01,-3.83482494e-01));
}

void ofdmi_make_qam(std::vector<gr_complex> &constellation, unsigned char bits)
{
  assert(bits >= 4 && bits <= 8);

  switch(bits){
    case 4:  ofdmi_make_16qam(constellation);  break;
    case 5:  ofdmi_make_32qam(constellation);  break;
    case 6:  ofdmi_make_64qam(constellation);  break;
    case 7:  ofdmi_make_128qam(constellation); break;
    case 8:  ofdmi_make_256qam(constellation); break;
    default:
      assert("should never get here");
  }
}

std::vector< std::vector< std::vector< char > > >
ofdmi_generate_128qam_lut()
{
  std::vector< std::vector< std::vector< char > > > lut;

  lut.resize( 7 );
  for( unsigned int i = 0; i < lut.size(); ++i )
  {
    lut[i].resize( 12 );
    for( unsigned int j = 0; j < lut[i].size(); ++j )
    {
      lut[i][j].resize( 12, 0 );
    }
  }

  lut[4][0][0] = 1;
  lut[6][0][0] = 1;
  lut[2][0][1] = 1;
  lut[3][0][1] = 1;
  lut[4][0][1] = 1;
  lut[2][0][2] = 1;
  lut[3][0][2] = 1;
  lut[4][0][2] = 1;
  lut[2][0][3] = 1;
  lut[3][0][3] = 1;
  lut[4][0][3] = 1;
  lut[6][0][3] = 1;
  lut[2][0][4] = 1;
  lut[3][0][4] = 1;
  lut[4][0][4] = 1;
  lut[5][0][4] = 1;
  lut[6][0][4] = 1;
  lut[2][0][5] = 1;
  lut[3][0][5] = 1;
  lut[4][0][5] = 1;
  lut[5][0][5] = 1;
  lut[2][0][6] = 1;
  lut[3][0][6] = 1;
  lut[5][0][6] = 1;
  lut[2][0][7] = 1;
  lut[3][0][7] = 1;
  lut[5][0][7] = 1;
  lut[6][0][7] = 1;
  lut[2][0][8] = 1;
  lut[3][0][8] = 1;
  lut[6][0][8] = 1;
  lut[2][0][9] = 1;
  lut[3][0][9] = 1;
  lut[2][0][10] = 1;
  lut[3][0][10] = 1;
  lut[6][0][11] = 1;
  lut[4][1][0] = 1;
  lut[6][1][0] = 1;
  lut[4][1][1] = 1;
  lut[2][1][2] = 1;
  lut[4][1][2] = 1;
  lut[2][1][3] = 1;
  lut[4][1][3] = 1;
  lut[6][1][3] = 1;
  lut[2][1][4] = 1;
  lut[4][1][4] = 1;
  lut[5][1][4] = 1;
  lut[6][1][4] = 1;
  lut[2][1][5] = 1;
  lut[4][1][5] = 1;
  lut[5][1][5] = 1;
  lut[2][1][6] = 1;
  lut[5][1][6] = 1;
  lut[2][1][7] = 1;
  lut[5][1][7] = 1;
  lut[6][1][7] = 1;
  lut[2][1][8] = 1;
  lut[6][1][8] = 1;
  lut[2][1][9] = 1;
  lut[6][1][11] = 1;
  lut[4][2][0] = 1;
  lut[6][2][0] = 1;
  lut[4][2][1] = 1;
  lut[1][2][2] = 1;
  lut[2][2][2] = 1;
  lut[4][2][2] = 1;
  lut[1][2][3] = 1;
  lut[2][2][3] = 1;
  lut[4][2][3] = 1;
  lut[6][2][3] = 1;
  lut[1][2][4] = 1;
  lut[2][2][4] = 1;
  lut[4][2][4] = 1;
  lut[5][2][4] = 1;
  lut[6][2][4] = 1;
  lut[1][2][5] = 1;
  lut[2][2][5] = 1;
  lut[4][2][5] = 1;
  lut[5][2][5] = 1;
  lut[1][2][6] = 1;
  lut[2][2][6] = 1;
  lut[5][2][6] = 1;
  lut[1][2][7] = 1;
  lut[2][2][7] = 1;
  lut[5][2][7] = 1;
  lut[6][2][7] = 1;
  lut[1][2][8] = 1;
  lut[2][2][8] = 1;
  lut[6][2][8] = 1;
  lut[1][2][9] = 1;
  lut[2][2][9] = 1;
  lut[6][2][11] = 1;
  lut[3][3][0] = 1;
  lut[4][3][0] = 1;
  lut[6][3][0] = 1;
  lut[3][3][1] = 1;
  lut[4][3][1] = 1;
  lut[1][3][2] = 1;
  lut[2][3][2] = 1;
  lut[3][3][2] = 1;
  lut[4][3][2] = 1;
  lut[1][3][3] = 1;
  lut[2][3][3] = 1;
  lut[3][3][3] = 1;
  lut[4][3][3] = 1;
  lut[6][3][3] = 1;
  lut[1][3][4] = 1;
  lut[2][3][4] = 1;
  lut[3][3][4] = 1;
  lut[4][3][4] = 1;
  lut[5][3][4] = 1;
  lut[6][3][4] = 1;
  lut[1][3][5] = 1;
  lut[2][3][5] = 1;
  lut[3][3][5] = 1;
  lut[4][3][5] = 1;
  lut[5][3][5] = 1;
  lut[1][3][6] = 1;
  lut[2][3][6] = 1;
  lut[3][3][6] = 1;
  lut[5][3][6] = 1;
  lut[1][3][7] = 1;
  lut[2][3][7] = 1;
  lut[3][3][7] = 1;
  lut[5][3][7] = 1;
  lut[6][3][7] = 1;
  lut[1][3][8] = 1;
  lut[2][3][8] = 1;
  lut[3][3][8] = 1;
  lut[6][3][8] = 1;
  lut[1][3][9] = 1;
  lut[2][3][9] = 1;
  lut[3][3][9] = 1;
  lut[3][3][10] = 1;
  lut[3][3][11] = 1;
  lut[6][3][11] = 1;
  lut[3][4][0] = 1;
  lut[4][4][0] = 1;
  lut[5][4][0] = 1;
  lut[6][4][0] = 1;
  lut[3][4][1] = 1;
  lut[4][4][1] = 1;
  lut[5][4][1] = 1;
  lut[1][4][2] = 1;
  lut[3][4][2] = 1;
  lut[4][4][2] = 1;
  lut[1][4][3] = 1;
  lut[3][4][3] = 1;
  lut[4][4][3] = 1;
  lut[6][4][3] = 1;
  lut[1][4][4] = 1;
  lut[3][4][4] = 1;
  lut[4][4][4] = 1;
  lut[5][4][4] = 1;
  lut[6][4][4] = 1;
  lut[1][4][5] = 1;
  lut[3][4][5] = 1;
  lut[4][4][5] = 1;
  lut[5][4][5] = 1;
  lut[1][4][6] = 1;
  lut[3][4][6] = 1;
  lut[5][4][6] = 1;
  lut[1][4][7] = 1;
  lut[3][4][7] = 1;
  lut[5][4][7] = 1;
  lut[6][4][7] = 1;
  lut[1][4][8] = 1;
  lut[3][4][8] = 1;
  lut[6][4][8] = 1;
  lut[1][4][9] = 1;
  lut[3][4][9] = 1;
  lut[3][4][10] = 1;
  lut[5][4][10] = 1;
  lut[3][4][11] = 1;
  lut[5][4][11] = 1;
  lut[6][4][11] = 1;
  lut[4][5][0] = 1;
  lut[5][5][0] = 1;
  lut[6][5][0] = 1;
  lut[4][5][1] = 1;
  lut[5][5][1] = 1;
  lut[1][5][2] = 1;
  lut[4][5][2] = 1;
  lut[1][5][3] = 1;
  lut[4][5][3] = 1;
  lut[6][5][3] = 1;
  lut[1][5][4] = 1;
  lut[4][5][4] = 1;
  lut[5][5][4] = 1;
  lut[6][5][4] = 1;
  lut[1][5][5] = 1;
  lut[4][5][5] = 1;
  lut[5][5][5] = 1;
  lut[1][5][6] = 1;
  lut[5][5][6] = 1;
  lut[1][5][7] = 1;
  lut[5][5][7] = 1;
  lut[6][5][7] = 1;
  lut[1][5][8] = 1;
  lut[6][5][8] = 1;
  lut[1][5][9] = 1;
  lut[5][5][10] = 1;
  lut[5][5][11] = 1;
  lut[6][5][11] = 1;
  lut[0][6][0] = 1;
  lut[4][6][0] = 1;
  lut[5][6][0] = 1;
  lut[6][6][0] = 1;
  lut[0][6][1] = 1;
  lut[4][6][1] = 1;
  lut[5][6][1] = 1;
  lut[0][6][2] = 1;
  lut[1][6][2] = 1;
  lut[4][6][2] = 1;
  lut[0][6][3] = 1;
  lut[1][6][3] = 1;
  lut[4][6][3] = 1;
  lut[6][6][3] = 1;
  lut[0][6][4] = 1;
  lut[1][6][4] = 1;
  lut[4][6][4] = 1;
  lut[5][6][4] = 1;
  lut[6][6][4] = 1;
  lut[0][6][5] = 1;
  lut[1][6][5] = 1;
  lut[4][6][5] = 1;
  lut[5][6][5] = 1;
  lut[0][6][6] = 1;
  lut[1][6][6] = 1;
  lut[5][6][6] = 1;
  lut[0][6][7] = 1;
  lut[1][6][7] = 1;
  lut[5][6][7] = 1;
  lut[6][6][7] = 1;
  lut[0][6][8] = 1;
  lut[1][6][8] = 1;
  lut[6][6][8] = 1;
  lut[0][6][9] = 1;
  lut[1][6][9] = 1;
  lut[0][6][10] = 1;
  lut[5][6][10] = 1;
  lut[0][6][11] = 1;
  lut[5][6][11] = 1;
  lut[6][6][11] = 1;
  lut[0][7][0] = 1;
  lut[3][7][0] = 1;
  lut[4][7][0] = 1;
  lut[5][7][0] = 1;
  lut[6][7][0] = 1;
  lut[0][7][1] = 1;
  lut[3][7][1] = 1;
  lut[4][7][1] = 1;
  lut[5][7][1] = 1;
  lut[0][7][2] = 1;
  lut[1][7][2] = 1;
  lut[3][7][2] = 1;
  lut[4][7][2] = 1;
  lut[0][7][3] = 1;
  lut[1][7][3] = 1;
  lut[3][7][3] = 1;
  lut[4][7][3] = 1;
  lut[6][7][3] = 1;
  lut[0][7][4] = 1;
  lut[1][7][4] = 1;
  lut[3][7][4] = 1;
  lut[4][7][4] = 1;
  lut[5][7][4] = 1;
  lut[6][7][4] = 1;
  lut[0][7][5] = 1;
  lut[1][7][5] = 1;
  lut[3][7][5] = 1;
  lut[4][7][5] = 1;
  lut[5][7][5] = 1;
  lut[0][7][6] = 1;
  lut[1][7][6] = 1;
  lut[3][7][6] = 1;
  lut[5][7][6] = 1;
  lut[0][7][7] = 1;
  lut[1][7][7] = 1;
  lut[3][7][7] = 1;
  lut[5][7][7] = 1;
  lut[6][7][7] = 1;
  lut[0][7][8] = 1;
  lut[1][7][8] = 1;
  lut[3][7][8] = 1;
  lut[6][7][8] = 1;
  lut[0][7][9] = 1;
  lut[1][7][9] = 1;
  lut[3][7][9] = 1;
  lut[0][7][10] = 1;
  lut[3][7][10] = 1;
  lut[5][7][10] = 1;
  lut[0][7][11] = 1;
  lut[3][7][11] = 1;
  lut[5][7][11] = 1;
  lut[6][7][11] = 1;
  lut[0][8][0] = 1;
  lut[3][8][0] = 1;
  lut[4][8][0] = 1;
  lut[6][8][0] = 1;
  lut[0][8][1] = 1;
  lut[3][8][1] = 1;
  lut[4][8][1] = 1;
  lut[0][8][2] = 1;
  lut[1][8][2] = 1;
  lut[2][8][2] = 1;
  lut[3][8][2] = 1;
  lut[4][8][2] = 1;
  lut[0][8][3] = 1;
  lut[1][8][3] = 1;
  lut[2][8][3] = 1;
  lut[3][8][3] = 1;
  lut[4][8][3] = 1;
  lut[6][8][3] = 1;
  lut[0][8][4] = 1;
  lut[1][8][4] = 1;
  lut[2][8][4] = 1;
  lut[3][8][4] = 1;
  lut[4][8][4] = 1;
  lut[5][8][4] = 1;
  lut[6][8][4] = 1;
  lut[0][8][5] = 1;
  lut[1][8][5] = 1;
  lut[2][8][5] = 1;
  lut[3][8][5] = 1;
  lut[4][8][5] = 1;
  lut[5][8][5] = 1;
  lut[0][8][6] = 1;
  lut[1][8][6] = 1;
  lut[2][8][6] = 1;
  lut[3][8][6] = 1;
  lut[5][8][6] = 1;
  lut[0][8][7] = 1;
  lut[1][8][7] = 1;
  lut[2][8][7] = 1;
  lut[3][8][7] = 1;
  lut[5][8][7] = 1;
  lut[6][8][7] = 1;
  lut[0][8][8] = 1;
  lut[1][8][8] = 1;
  lut[2][8][8] = 1;
  lut[3][8][8] = 1;
  lut[6][8][8] = 1;
  lut[0][8][9] = 1;
  lut[1][8][9] = 1;
  lut[2][8][9] = 1;
  lut[3][8][9] = 1;
  lut[0][8][10] = 1;
  lut[3][8][10] = 1;
  lut[0][8][11] = 1;
  lut[3][8][11] = 1;
  lut[6][8][11] = 1;
  lut[0][9][0] = 1;
  lut[4][9][0] = 1;
  lut[6][9][0] = 1;
  lut[0][9][1] = 1;
  lut[4][9][1] = 1;
  lut[0][9][2] = 1;
  lut[1][9][2] = 1;
  lut[2][9][2] = 1;
  lut[4][9][2] = 1;
  lut[0][9][3] = 1;
  lut[1][9][3] = 1;
  lut[2][9][3] = 1;
  lut[4][9][3] = 1;
  lut[6][9][3] = 1;
  lut[0][9][4] = 1;
  lut[1][9][4] = 1;
  lut[2][9][4] = 1;
  lut[4][9][4] = 1;
  lut[5][9][4] = 1;
  lut[6][9][4] = 1;
  lut[0][9][5] = 1;
  lut[1][9][5] = 1;
  lut[2][9][5] = 1;
  lut[4][9][5] = 1;
  lut[5][9][5] = 1;
  lut[0][9][6] = 1;
  lut[1][9][6] = 1;
  lut[2][9][6] = 1;
  lut[5][9][6] = 1;
  lut[0][9][7] = 1;
  lut[1][9][7] = 1;
  lut[2][9][7] = 1;
  lut[5][9][7] = 1;
  lut[6][9][7] = 1;
  lut[0][9][8] = 1;
  lut[1][9][8] = 1;
  lut[2][9][8] = 1;
  lut[6][9][8] = 1;
  lut[0][9][9] = 1;
  lut[1][9][9] = 1;
  lut[2][9][9] = 1;
  lut[0][9][10] = 1;
  lut[0][9][11] = 1;
  lut[6][9][11] = 1;
  lut[0][10][0] = 1;
  lut[4][10][0] = 1;
  lut[6][10][0] = 1;
  lut[0][10][1] = 1;
  lut[4][10][1] = 1;
  lut[0][10][2] = 1;
  lut[2][10][2] = 1;
  lut[4][10][2] = 1;
  lut[0][10][3] = 1;
  lut[2][10][3] = 1;
  lut[4][10][3] = 1;
  lut[6][10][3] = 1;
  lut[0][10][4] = 1;
  lut[2][10][4] = 1;
  lut[4][10][4] = 1;
  lut[5][10][4] = 1;
  lut[6][10][4] = 1;
  lut[0][10][5] = 1;
  lut[2][10][5] = 1;
  lut[4][10][5] = 1;
  lut[5][10][5] = 1;
  lut[0][10][6] = 1;
  lut[2][10][6] = 1;
  lut[5][10][6] = 1;
  lut[0][10][7] = 1;
  lut[2][10][7] = 1;
  lut[5][10][7] = 1;
  lut[6][10][7] = 1;
  lut[0][10][8] = 1;
  lut[2][10][8] = 1;
  lut[6][10][8] = 1;
  lut[0][10][9] = 1;
  lut[2][10][9] = 1;
  lut[0][10][10] = 1;
  lut[0][10][11] = 1;
  lut[6][10][11] = 1;
  lut[0][11][0] = 1;
  lut[4][11][0] = 1;
  lut[6][11][0] = 1;
  lut[0][11][1] = 1;
  lut[2][11][1] = 1;
  lut[3][11][1] = 1;
  lut[4][11][1] = 1;
  lut[0][11][2] = 1;
  lut[2][11][2] = 1;
  lut[3][11][2] = 1;
  lut[4][11][2] = 1;
  lut[0][11][3] = 1;
  lut[2][11][3] = 1;
  lut[3][11][3] = 1;
  lut[4][11][3] = 1;
  lut[6][11][3] = 1;
  lut[0][11][4] = 1;
  lut[2][11][4] = 1;
  lut[3][11][4] = 1;
  lut[4][11][4] = 1;
  lut[5][11][4] = 1;
  lut[6][11][4] = 1;
  lut[0][11][5] = 1;
  lut[2][11][5] = 1;
  lut[3][11][5] = 1;
  lut[4][11][5] = 1;
  lut[5][11][5] = 1;
  lut[0][11][6] = 1;
  lut[2][11][6] = 1;
  lut[3][11][6] = 1;
  lut[5][11][6] = 1;
  lut[0][11][7] = 1;
  lut[2][11][7] = 1;
  lut[3][11][7] = 1;
  lut[5][11][7] = 1;
  lut[6][11][7] = 1;
  lut[0][11][8] = 1;
  lut[2][11][8] = 1;
  lut[3][11][8] = 1;
  lut[6][11][8] = 1;
  lut[0][11][9] = 1;
  lut[2][11][9] = 1;
  lut[3][11][9] = 1;
  lut[0][11][10] = 1;
  lut[2][11][10] = 1;
  lut[3][11][10] = 1;
  lut[0][11][11] = 1;
  lut[6][11][11] = 1;

  return lut;

}

/*
// gray coded qam
void ofdmi_make_qam(std::vector<gr_complex> &constellation, unsigned char bits)
{
  int num_sym = static_cast<int>(pow(2, bits)), len_bits = (bits-2)/2;
  int a, b, bits_i[len_bits], bits_q[len_bits], coeff = 1, re, im;
  std::vector<gr_complex> c(static_cast<size_t>(num_sym));

  assert(bits == 4 || bits == 6 || bits == 8);

  for(int sym = 0; sym < num_sym; ++sym) {
    a = (sym >> (bits-1)) & 0x01;
    b = (sym >> (bits-2)) & 0x01;
    for(int j = 2; j < bits; j+=2) {
      bits_i[j/2-1] = (sym >> (bits-1-j)) & 0x01;
      bits_q[j/2-1] = (sym >> (bits-2-j)) & 0x01;
    }

    int s1 = 0, s2 = 0;
    for(int i = 0; i < len_bits; ++i) {
      int r1 = 0, r2 = 0;
      for(int j = 0; j < len_bits - i; ++j) {
        r1 = abs(bits_i[j] - r1);
        r2 = abs(bits_q[j] - r2);
      }
      s1 += r1 * static_cast<int>(pow(2, i+1));
      s2 += r2 * static_cast<int>(pow(2, i+1));
    }
    re = (2*a-1)*(s1+1);
    im = (2*b-1)*(s2+1);

    coeff = std::max(coeff, std::max(re, im));
    c[sym] = gr_complex(re, im);
  }

  for(int sym = 0; sym < num_sym; ++sym) {
    c[sym] /= coeff;
  }

  constellation = c;
}

*/

void ofdmi_generic_decision(const std::vector<gr_complex> &constellation,
    const gr_complex &symbol, char* out, int &bits)
{
  assert(constellation.size() > 1);
  assert(constellation.size() <= 256);

  // Find constellation point that minimizes Euclidean distance to
  // the input symbol
  float min_distance = norm(constellation[0] - symbol), distance;
  unsigned int decoded = 0;
  for(unsigned int i  = 1; i < constellation.size(); ++i) {
    distance = norm(constellation[i] - symbol);
    if(distance < min_distance) {
      min_distance = distance;
      decoded = i;
    }
  }
  for(int bit = bits-1; bit >= 0; --bit){
    *out++ = (decoded >> bit) & 1;
  }
}

// assert for all decision function: out preset with zero

void ofdmi_bpsk_decision(const std::vector<gr_complex> &dummy,
    const gr_complex &symbol, char* out, int &bits)
{
  if(symbol.real() < 0.0)
    out[0] = 1;
}

void ofdmi_qpsk_decision(const std::vector<gr_complex> &dummy,
    const gr_complex &symbol, char* out, int &bits)
{
  if(symbol.real() > 0.0){
    if(symbol.imag() < 0.0)
      out[0] = 1;
  }else{
    out[1] = 1;
    if(symbol.imag() > 0.0)
      out[0] = 1;
  }
}

void ofdmi_16qam_decision(const std::vector<gr_complex> &dummy,
    const gr_complex &symbol, char* out, int &bits)
{
  const float level_0 = 0.6325;

  const float i = symbol.real();
  const float q = symbol.imag();

  if(i > 0.0){
    out[0] = 1;
    if((i-level_0) < 0.0)
      out[1] = 1;
  }else{
    if((i+level_0) > 0.0)
      out[1] = 1;
  }

  if(q < 0.0){
    out[2] = 1;
    if((q+level_0) > 0.0)
      out[3] = 1;
  }else{
    if((q-level_0) < 0.0)
      out[3] = 1;
  }
}

void ofdmi_64qam_decision(const std::vector<gr_complex> &dummy,
    const gr_complex &symbol, char* out, int &bits)
{
  const float level = 0.3086;
  const float level2 = level*2.0;
  const float level3 = level*3.0;

  const float i = symbol.real();
  const float q = -symbol.imag();

  if(i < 0.0){
    if((level2+i)>0.0){
      out[1] = 1;
      if((-level-i)>0.0)
        out[2] = 1;
    }else{
      if((i+level3)>0.0)
        out[2] = 1;
    }
  }else{
    out[0] = 1;
    if((level2-i)>0.0){
      out[1] = 1;
      if((i-level)>0.0)
        out[2] = 1;
    }else{
      if((-i+level3)>0.0)
        out[2] = 1;
    }
  }

  if(q < 0.0){
    if((level2+q)>0.0){
      out[4] = 1;
      if((-level-q)>0.0)
        out[5] = 1;
    }else{
      if((q+level3)>0.0)
        out[5] = 1;
    }
  }else{
    out[3] = 1;
    if((level2-q)>0.0){
      out[4] = 1;
      if((q-level)>0.0)
        out[5] = 1;
    }else{
      if((-q+level3)>0.0)
        out[5] = 1;
    }
  }
}


std::vector< std::vector< std::vector< char > > >
ofdmi_generate_32qam_lut()
{
  std::vector< std::vector< std::vector< char > > > lut;

  lut.resize( 5 );
  for( unsigned int i = 0; i < lut.size(); ++i )
  {
    lut[i].resize( 6 );
    for( unsigned int j = 0; j < lut[i].size(); ++j )
    {
      lut[i][j].resize( 6, 0 );
    }
  }

  lut[3][0][0] = 1;
  lut[2][0][1] = 1;
  lut[3][0][1] = 1;
  lut[2][0][2] = 1;
  lut[3][0][2] = 1;
  lut[4][0][2] = 1;
  lut[2][0][3] = 1;
  lut[4][0][3] = 1;
  lut[2][0][4] = 1;
  lut[3][1][0] = 1;
  lut[1][1][1] = 1;
  lut[2][1][1] = 1;
  lut[3][1][1] = 1;
  lut[1][1][2] = 1;
  lut[2][1][2] = 1;
  lut[3][1][2] = 1;
  lut[4][1][2] = 1;
  lut[1][1][3] = 1;
  lut[2][1][3] = 1;
  lut[4][1][3] = 1;
  lut[1][1][4] = 1;
  lut[2][1][4] = 1;
  lut[3][2][0] = 1;
  lut[4][2][0] = 1;
  lut[1][2][1] = 1;
  lut[3][2][1] = 1;
  lut[1][2][2] = 1;
  lut[3][2][2] = 1;
  lut[4][2][2] = 1;
  lut[1][2][3] = 1;
  lut[4][2][3] = 1;
  lut[1][2][4] = 1;
  lut[4][2][5] = 1;
  lut[0][3][0] = 1;
  lut[3][3][0] = 1;
  lut[4][3][0] = 1;
  lut[0][3][1] = 1;
  lut[1][3][1] = 1;
  lut[3][3][1] = 1;
  lut[0][3][2] = 1;
  lut[1][3][2] = 1;
  lut[3][3][2] = 1;
  lut[4][3][2] = 1;
  lut[0][3][3] = 1;
  lut[1][3][3] = 1;
  lut[4][3][3] = 1;
  lut[0][3][4] = 1;
  lut[1][3][4] = 1;
  lut[0][3][5] = 1;
  lut[4][3][5] = 1;
  lut[0][4][0] = 1;
  lut[3][4][0] = 1;
  lut[0][4][1] = 1;
  lut[1][4][1] = 1;
  lut[2][4][1] = 1;
  lut[3][4][1] = 1;
  lut[0][4][2] = 1;
  lut[1][4][2] = 1;
  lut[2][4][2] = 1;
  lut[3][4][2] = 1;
  lut[4][4][2] = 1;
  lut[0][4][3] = 1;
  lut[1][4][3] = 1;
  lut[2][4][3] = 1;
  lut[4][4][3] = 1;
  lut[0][4][4] = 1;
  lut[1][4][4] = 1;
  lut[2][4][4] = 1;
  lut[0][4][5] = 1;
  lut[0][5][0] = 1;
  lut[3][5][0] = 1;
  lut[0][5][1] = 1;
  lut[2][5][1] = 1;
  lut[3][5][1] = 1;
  lut[0][5][2] = 1;
  lut[2][5][2] = 1;
  lut[3][5][2] = 1;
  lut[4][5][2] = 1;
  lut[0][5][3] = 1;
  lut[2][5][3] = 1;
  lut[4][5][3] = 1;
  lut[0][5][4] = 1;
  lut[2][5][4] = 1;
  lut[0][5][5] = 1;

  return lut;
}

