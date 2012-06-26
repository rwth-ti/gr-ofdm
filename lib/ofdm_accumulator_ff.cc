#ifdef HAVE_CONFIG_H
#include "config.h"
#endif

#include <gr_sync_block.h>
#include <gr_io_signature.h>
#include <ofdm_accumulator_ff.h>

ofdm_accumulator_ff_sptr ofdm_make_accumulator_ff()
{
  return ofdm_accumulator_ff_sptr(new ofdm_accumulator_ff());
}

ofdm_accumulator_ff::ofdm_accumulator_ff()

  : gr_sync_block("accumulator_ff",
           gr_make_io_signature (1, 1, sizeof(float)),
           gr_make_io_signature (1, 1, sizeof(float))),
           
    d_accum( 0.0 )
    
{
}

int ofdm_accumulator_ff::work(
    int noutput_items,
    gr_vector_const_void_star &input_items,
    gr_vector_void_star &output_items)
{
  const float *in = static_cast<const float*>(input_items[0]);
  float *out = static_cast<float*>(output_items[0]);
  
  float acc = d_accum;
  
  for(int i = 0; i < noutput_items; ++i){
    acc += in[i];
    out[i] = acc;
  }
  
  d_accum = acc;
  
  return noutput_items;
}
