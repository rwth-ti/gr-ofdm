#ifdef HAVE_CONFIG_H
#include "config.h"
#endif

#include <gr_sync_block.h>
#include <ofdm_complex_to_arg.h>
#include <gr_io_signature.h>

#include <cmath>

ofdm_complex_to_arg_sptr ofdm_make_complex_to_arg (unsigned int vlen)
{
  return ofdm_complex_to_arg_sptr (new ofdm_complex_to_arg (vlen));
}

ofdm_complex_to_arg::ofdm_complex_to_arg (unsigned int vlen)
  : gr_sync_block ("complex_to_arg",
      gr_make_io_signature (1, 1, sizeof(gr_complex)*vlen),
      gr_make_io_signature (1, 1, sizeof(float)*vlen)),
    d_vlen(vlen)
{
}

int ofdm_complex_to_arg::work(
  int noutput_items,
  gr_vector_const_void_star &input_items,
  gr_vector_void_star &output_items)
{
  const gr_complex *in = static_cast<const gr_complex*>(input_items[0]);
  float *out = static_cast<float*>(output_items[0]);

  for (int i = 0; i < noutput_items*d_vlen; i++){
    out[i] = std::arg(in[i]);
  }

  return noutput_items;
}
