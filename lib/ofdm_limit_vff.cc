#ifdef HAVE_CONFIG_H
#include "config.h"
#endif

#include <gr_sync_block.h>
#include <gr_io_signature.h>
#include <ofdm_limit_vff.h>

#include <gr_math.h>

//include <math.h>
#include <cmath>


ofdm_limit_vff_sptr ofdm_make_limit_vff(int vlen, float up_limit, float lo_limit)
{
  return ofdm_limit_vff_sptr(new ofdm_limit_vff(vlen, up_limit, lo_limit));
}

ofdm_limit_vff::ofdm_limit_vff(int vlen, float up_limit, float lo_limit)
  : gr_sync_block("limit_vff",
           gr_make_io_signature (1, 1, sizeof(float)*vlen),
           gr_make_io_signature (1, 1, sizeof(float)*vlen)),
  d_up_limit(up_limit), d_lo_limit(lo_limit), d_vlen(vlen)
{
}

int ofdm_limit_vff::work(
    int noutput_items,
    gr_vector_const_void_star &input_items,
    gr_vector_void_star &output_items)
{
  const float *in = static_cast<const float*>(input_items[0]);
  float *out = static_cast<float*>(output_items[0]);

  for(int i = 0; i < noutput_items*d_vlen; ++i){
    if(std::isnan(in[i])){
      out[i] = 0.0;
    }else if(in[i] > d_up_limit){
      out[i] = d_up_limit;
    }else if(in[i] < d_lo_limit){
      out[i] = -d_lo_limit;
    }else{
      out[i] = in[i];
    }
  }

  return noutput_items;
}
