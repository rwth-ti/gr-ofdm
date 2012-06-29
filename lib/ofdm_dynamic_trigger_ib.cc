#ifdef HAVE_CONFIG_H
#include "config.h"
#endif

#include <gr_block.h>
#include <gr_io_signature.h>
#include <ofdm_dynamic_trigger_ib.h>

#include <cstring>


#include <iostream>
#include <algorithm>

ofdm_dynamic_trigger_ib_sptr ofdm_make_dynamic_trigger_ib(bool first_or_last)
{
  return ofdm_dynamic_trigger_ib_sptr(new ofdm_dynamic_trigger_ib(first_or_last));
}


void ofdm_dynamic_trigger_ib::forecast(int noutput_items, gr_vector_int &ninput_items_required)
{
  ninput_items_required[0] = 1;
}


ofdm_dynamic_trigger_ib::ofdm_dynamic_trigger_ib(bool first_or_last)
  : gr_block("dynamic_trigger_ib",
           gr_make_io_signature (1, 1, sizeof(unsigned int)),
           gr_make_io_signature (1, 1, sizeof(char))),
  d_first_or_last(first_or_last), 
  d_produced(0)
{
}

int ofdm_dynamic_trigger_ib::general_work(
    int noutput_items,
    gr_vector_int &ninput_items,
    gr_vector_const_void_star &input_items,
    gr_vector_void_star &output_items)
{
  const unsigned int *in = static_cast<const unsigned int*>(input_items[0]);
  char *out = static_cast<char*>(output_items[0]);
  
  int ninput = ninput_items[0];
  int noutput = noutput_items;
  
  memset(out,0,noutput_items*sizeof(char));
  
  //std::cout << "[dyn.trig] " << in[0] << std::endl;
  
  while( noutput > 0 && ninput > 0 ) {
    if(in[0] == 0){
      
      std::cerr << "warning: bitcount = 0" << std::endl;
      consume_each(1);
      --ninput;
      ++in;
  
    } else if(in[0] > d_produced){
      
      unsigned int n = std::min(static_cast<unsigned int>(noutput),
          in[0]-d_produced);
      assert(n > 0);
      
      if(d_first_or_last && d_produced == 0){ // first
        out[0] = 1;
      }
      
      d_produced += n;
      
      if(d_produced == in[0]){
        d_produced = 0;
        consume_each(1);
        //std::cout << "[dyn trig] consume, new " << in[0] << std::endl;
        --ninput;
        ++in;
        
        if(!d_first_or_last)
          out[n-1] = 1;
      }
      
      noutput -= n;
      out += n;
      
    } else {
      
      assert(false && "[dyn.trig] failed, in <= d_produced && != 0");
      
    }
  } // while (..)
  
  //std::cout << "[dyn.trig] produce " << noutput_items-noutput << std::endl; 
  
  return noutput_items-noutput;
}


int 
ofdm_dynamic_trigger_ib::noutput_forecast( gr_vector_int &ninput_items, 
    int available_space, int max_items_avail, std::vector<bool> &input_done )
{  
  
  // check if we are done or if we can't produce anything
  // else with at least one input item, we possibly use the whole
  // available output space.
  
  if( ninput_items[0] == 0 && input_done[0] )
    return -1;
  
  if( ninput_items[0] == 0 )
    return 0;
  
  return available_space;
  
}
