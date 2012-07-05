#ifdef HAVE_CONFIG_H
#include "config.h"
#endif

#include <gr_sync_block.h>
#include <gr_io_signature.h>
#include <ofdm_vector_sum_vff.h>

ofdm_vector_sum_vff_sptr ofdm_make_vector_sum_vff(int vlen)
{
  return ofdm_vector_sum_vff_sptr(new ofdm_vector_sum_vff(vlen));
}

ofdm_vector_sum_vff::ofdm_vector_sum_vff(int vlen)
  : gr_sync_block("vector_sum_vff",
           gr_make_io_signature (1, 1, sizeof(float)*vlen),
           gr_make_io_signature (1, 1, sizeof(float))),
  d_vlen(vlen)
{
}

int ofdm_vector_sum_vff::work(
    int noutput_items,
    gr_vector_const_void_star &input_items,
    gr_vector_void_star &output_items)
{
  const float *in = static_cast<const float*>(input_items[0]);
  float *out = static_cast<float*>(output_items[0]);

  for(int i = 0; i < noutput_items; ++i) {
    float sum = 0.0;
    for(int x = 0; x < d_vlen; ++x) {
      sum += *(in++);
    }
    *(out++) = sum;
  }

  return noutput_items;
}
