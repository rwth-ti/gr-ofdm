#ifdef HAVE_CONFIG_H
#include "config.h"
#endif

#include <gr_sync_block.h>
#include <gr_io_signature.h>
#include <ofdm_get_zeros.h>

ofdm_get_zeros_sptr ofdm_make_get_zeros(int ll)
{
  return ofdm_get_zeros_sptr(new ofdm_get_zeros(ll));
}

ofdm_get_zeros::ofdm_get_zeros(int ll)
  : gr_sync_block("get_zeros",
           gr_make_io_signature (1, 1, sizeof(gr_complex)),
           gr_make_io_signature (1, 1, sizeof(gr_complex))),
  d_ll(ll)
{
}

int ofdm_get_zeros::work(
    int noutput_items,
    gr_vector_const_void_star &input_items,
    gr_vector_void_star &output_items)
{
  const gr_complex *in = static_cast<const gr_complex*>(input_items[0]);
  gr_complex *out = static_cast<gr_complex*>(output_items[0]);

  int i_max = noutput_items/(d_ll-1);
  for(int i = 0; i < i_max; ++i, out += (d_ll-1)){
	  in+=1;

     for(int j = 0; j < d_ll; ++j){
       out[j] = in[j];
     }

   }

  return i_max*(d_ll-1);
  //return noutput_items;

}
