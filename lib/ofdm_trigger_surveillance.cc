#ifdef HAVE_CONFIG_H
#include "config.h"
#endif

#include <gr_sync_block.h>
#include <ofdm_trigger_surveillance.h>
#include <gr_io_signature.h>

#include <iostream>
#include <cmath>

ofdm_trigger_surveillance_sptr ofdm_make_trigger_surveillance (int ideal_distance, int max_shift)
{
  return ofdm_trigger_surveillance_sptr (new ofdm_trigger_surveillance (ideal_distance, max_shift));
}

ofdm_trigger_surveillance::ofdm_trigger_surveillance (int ideal_distance, int max_shift)
  : gr_sync_block ("trigger_surveillance",
           gr_make_io_signature (1, 1, sizeof(char)),
           gr_make_io_signature (0, 0, 0)),
  d_ideal_distance(ideal_distance), d_max_shift(max_shift), d_dist(0),
  d_lost(0), d_first(true)
{
}

int ofdm_trigger_surveillance::work (int noutput_items,
    gr_vector_const_void_star &input_items,
    gr_vector_void_star &output_items)
{
  const char *in = static_cast<const char*>(input_items[0]);

  for(int i = 0; i < noutput_items; ++i, ++d_dist){
    if(in[i] != 1){
      if(!d_first){
        if(d_dist <= d_ideal_distance+d_max_shift){
          continue;
        }else{
          ++d_lost;
          d_dist = d_dist-d_ideal_distance;
          //std::cout << "Missed one trigger point" << std::endl;
          std::cout << "X"; // << std::flush;
        }
      }
    }else{
      if(d_first){
        d_first = false;
      } else {
        long long x = d_dist-d_ideal_distance;
        if(std::abs(x) > static_cast<long long>(d_max_shift)){
          ++d_lost;
          //std::cout << "Shifted trigger, shift of " << x << std::endl;
          std::cout << "S"; // << std::flush;
        }
      }

      d_dist = 0;
    }
  }

  return noutput_items;
}
