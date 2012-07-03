#ifdef HAVE_CONFIG_H
#include "config.h"
#endif

#include <gr_sync_block.h>
#include <ofdm_normalize_vcc.h>
#include <gr_io_signature.h>

#include <cmath>

ofdm_normalize_vcc_sptr ofdm_make_normalize_vcc (int vlen, float norm_power)
{
  return ofdm_normalize_vcc_sptr (new ofdm_normalize_vcc (vlen, norm_power));
}

ofdm_normalize_vcc::ofdm_normalize_vcc (int vlen, float norm_power)
  : gr_sync_block ("normalize_vcc",
           gr_make_io_signature (1, 1, sizeof(gr_complex)*vlen),
           gr_make_io_signature (1, 1, sizeof(gr_complex)*vlen)),
    d_norm_power(norm_power), d_vlen(vlen)
{
}

int ofdm_normalize_vcc::work (int noutput_items,
    gr_vector_const_void_star &input_items,
    gr_vector_void_star &output_items)
{
  const gr_complex *in = static_cast<const gr_complex*>(input_items[0]);
  gr_complex *out = static_cast<gr_complex*>(output_items[0]);

  for(int i = 0; i < noutput_items; ++i){
    float power = 0.0;
    for(int j = 0; j < d_vlen; ++j){
      const float __x = in[i*d_vlen+j].real();
      const float __y = in[i*d_vlen+j].imag();
      power += __x * __x + __y * __y;
    }

    float amp = std::sqrt(d_norm_power/power);
    for(int j = 0; j < d_vlen; ++j){
      out[i*d_vlen+j] = in[i*d_vlen+j]*amp;
    }
  }

  return noutput_items;
}
