#ifdef HAVE_CONFIG_H
#include "config.h"
#endif

#include <gr_sync_block.h>
#include <gr_io_signature.h>
#include <ofdm_vector_sum_vcc.h>

ofdm_vector_sum_vcc_sptr ofdm_make_vector_sum_vcc(int vlen)
{
  return ofdm_vector_sum_vcc_sptr(new ofdm_vector_sum_vcc(vlen));
}

ofdm_vector_sum_vcc::ofdm_vector_sum_vcc(int vlen)
  : gr_sync_block("vector_sum_vcc",
           gr_make_io_signature (1, 1, sizeof(gr_complex)*vlen),
           gr_make_io_signature (1, 1, sizeof(gr_complex))),
  d_vlen(vlen)
{
}

int ofdm_vector_sum_vcc::work(
    int noutput_items,
    gr_vector_const_void_star &input_items,
    gr_vector_void_star &output_items)
{
  const gr_complex *in = static_cast<const gr_complex*>(input_items[0]);
  gr_complex *out = static_cast<gr_complex*>(output_items[0]);

  for(int i = 0; i < noutput_items; ++i) {
    gr_complex sum(0.0,0.0);
    for(int x = 0; x < d_vlen; ++x) {
      sum += *(in++);
    }
    *(out++) = sum;
  }

  return noutput_items;
}
