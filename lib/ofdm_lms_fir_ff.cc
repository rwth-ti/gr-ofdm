#ifdef HAVE_CONFIG_H
#include "config.h"
#endif

#include <gr_sync_block.h>

#include <ofdm_lms_fir_ff.h>
#include <gr_io_signature.h>

ofdm_lms_fir_ff_sptr ofdm_make_lms_fir_ff (int len, float mu)
{
  return ofdm_lms_fir_ff_sptr (new ofdm_lms_fir_ff (len,mu));
}

ofdm_lms_fir_ff::ofdm_lms_fir_ff (int len, float mu)
  : gr_sync_block ("lms_fir_ff",
           gr_make_io_signature (1, 1, sizeof(float)),
           gr_make_io_signature (1, 1, sizeof(float))),
  d_len(len), d_mu(mu)
{
  set_history(len);

  d_taps.reset(new float[len]);
  for(int i = 0; i < len; ++i){
    d_taps[i] = 1.0/len;
  }
}

int ofdm_lms_fir_ff::work (int noutput_items,
    gr_vector_const_void_star &input_items,
    gr_vector_void_star &output_items)
{
  const float *in = static_cast<const float*>(input_items[0]);
  float *out = static_cast<float*>(output_items[0]);

  for(int i = 0; i < noutput_items; ++i){
    // FIR filter
    float x = d_taps[0] * in[i];
    for(int j = 1; j < d_len; ++j){
      x += d_taps[j] * in[i+j];
    }
    out[i] = x;

    // adaptive fir part
    float e = d_mu*(in[i] - x);
    for(int j = 0; j < d_len; ++j){
      d_taps[j] += e*in[i+j];
    }
  }

  return noutput_items;
}
