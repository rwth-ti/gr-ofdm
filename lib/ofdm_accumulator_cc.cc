#ifdef HAVE_CONFIG_H
#include "config.h"
#endif

#include <gr_sync_block.h>
#include <gr_io_signature.h>
#include <ofdm_accumulator_cc.h>

ofdm_accumulator_cc_sptr ofdm_make_accumulator_cc()
{
  return ofdm_accumulator_cc_sptr(new ofdm_accumulator_cc());
}

ofdm_accumulator_cc::ofdm_accumulator_cc()
  : gr_sync_block("accumulator_cc",
           gr_make_io_signature (1, 1, sizeof(gr_complex)),
           gr_make_io_signature (1, 1, sizeof(gr_complex))),
    d_accum( 0.0, 0.0 )
{
}

int ofdm_accumulator_cc::work(
    int noutput_items,
    gr_vector_const_void_star &input_items,
    gr_vector_void_star &output_items)
{
  const gr_complex *in = static_cast<const gr_complex*>(input_items[0]);
  gr_complex *out = static_cast<gr_complex*>(output_items[0]);

  gr_complex acc = d_accum;

  for(int i = 0; i < noutput_items; ++i){
    acc += in[i];
    out[i] = acc;
  }

  d_accum = acc;

  return noutput_items;
}
