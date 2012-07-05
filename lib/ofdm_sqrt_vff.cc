#ifdef HAVE_CONFIG_H
#include "config.h"
#endif

#include <gr_sync_block.h>
#include <ofdm_sqrt_vff.h>
#include <gr_io_signature.h>

#include <cmath>

ofdm_sqrt_vff_sptr ofdm_make_sqrt_vff (int vlen)
{
	return ofdm_sqrt_vff_sptr (new ofdm_sqrt_vff (vlen));
}

ofdm_sqrt_vff::ofdm_sqrt_vff (int vlen)
	: gr_sync_block ("sqrt_vff",
     gr_make_io_signature (1, 1, sizeof(float)*vlen),
     gr_make_io_signature (1, 1, sizeof(float)*vlen)),
    d_vlen(vlen)
{
}

int ofdm_sqrt_vff::work (
  int noutput_items,	
	gr_vector_const_void_star &input_items,
	gr_vector_void_star &output_items)
{
	const float *in = static_cast<const float*>(input_items[0]);
	float *out = static_cast<float*>(output_items[0]);
  
  for(int i = 0; i < noutput_items*d_vlen; ++i){
    out[i] = std::sqrt(in[i]);
  }
  
  return noutput_items;
}
