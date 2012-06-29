#ifdef HAVE_CONFIG_H
#include "config.h"
#endif

#include <gr_sync_block.h>
#include <ofdm_ber_measurement.h>
#include <gr_io_signature.h>

#include <iostream>

#define DEBUG 0

ofdm_ber_measurement_sptr ofdm_make_ber_measurement (
    unsigned long long sliding_window_length)
{
  try {
    return ofdm_ber_measurement_sptr (new ofdm_ber_measurement (
        sliding_window_length));
  } catch ( ... ) {
    std::cerr << "Caught exception when creating ofdm.ber_measurement("
              << sliding_window_length << ")" << std::endl;
    throw;
  }
}

ofdm_ber_measurement::ofdm_ber_measurement (
    unsigned long long sliding_window_length)
  : gr_sync_block ("ber_measurement",
                   gr_make_io_signature (2, 2, sizeof(char)),
                   gr_make_io_signature (1, 1, sizeof(float))),
    d_sliding_window_length(sliding_window_length),
    d_bits_in_win(sliding_window_length), d_errs_in_win(0)
{
  set_history(sliding_window_length+1);
}

int ofdm_ber_measurement::work (int noutput_items,
    gr_vector_const_void_star &input_items,
    gr_vector_void_star &output_items)
{
  const char *dat = static_cast<const char*>(input_items[0])+d_sliding_window_length;
  const char *dat_prev = static_cast<const char*>(input_items[0]);
  const char *ref = static_cast<const char*>(input_items[1])+d_sliding_window_length;
  const char *ref_prev = static_cast<const char*>(input_items[1]);

  float *out = static_cast<float*>(output_items[0]);
  
  if(DEBUG)
    std::cout << "[bermst " << unique_id() << "] entered, state "
              << "nout=" << noutput_items << " d_bits_in_win=" << d_bits_in_win
              << " d_errs_in_win=" << d_errs_in_win
              << std::endl;

  for( int i = 0; 
       i < noutput_items;
       ++i, ++dat, ++dat_prev, ++ref, ++ref_prev, ++out )
  {
    
    // erst rausfallen lassen
    if( *dat_prev < 2 ){
      --d_bits_in_win;
      if(*dat_prev != *ref_prev)
        --d_errs_in_win;
    }

    if( *dat < 2 ){
      ++d_bits_in_win;
      if(*dat != *ref)
        ++d_errs_in_win;
    }

    *out = get_ber();
    
  }

  return noutput_items;
}
