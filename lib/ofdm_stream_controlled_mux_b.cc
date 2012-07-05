#ifdef HAVE_CONFIG_H
#include "config.h"
#endif

#include <gr_block.h>
#include <gr_io_signature.h>
#include <ofdm_stream_controlled_mux_b.h>

#include <iostream>

#include <string.h>

ofdm_stream_controlled_mux_b_sptr ofdm_make_stream_controlled_mux_b()
{
  return ofdm_stream_controlled_mux_b_sptr(new ofdm_stream_controlled_mux_b());
}


void ofdm_stream_controlled_mux_b::forecast(int noutput_items, gr_vector_int &ninput_items_required)
{
  ninput_items_required[0] = noutput_items;

  for(int i = 1; i < ninput_items_required.size(); ++i)
    ninput_items_required[i] = 0;

  if(d_next_input > 0){
    assert(d_next_input < ninput_items_required.size());
    ninput_items_required[d_next_input] = 1;
  }
}


ofdm_stream_controlled_mux_b::ofdm_stream_controlled_mux_b()
  : gr_block("stream_controlled_mux_b",
           gr_make_io_signature2(2, -1, sizeof(unsigned short), sizeof(char)),
           gr_make_io_signature (1, 1, sizeof(char))),
  d_next_input(0)
{
}

int ofdm_stream_controlled_mux_b::general_work(
    int noutput_items,
    gr_vector_int &ninput_items,
    gr_vector_const_void_star &input_items,
    gr_vector_void_star &output_items)
{
  const unsigned short *mux = static_cast<const unsigned short*>(input_items[0]);
  char *out = static_cast<char*>(output_items[0]);

  const char* in[input_items.size()];
  gr_vector_int nin(ninput_items);
  for(gr_vector_const_void_star::size_type i = 1; i < input_items.size(); ++i){
    in[i] = static_cast<const char*>(input_items[i]);
  }


  d_next_input = 0;

  int i;

  for(i = 0; i < noutput_items; ++i){

    const int next_input = mux[i]+1;

    if(next_input >= input_items.size()){
      std::cerr << "input mux selection out of range" << std::endl;
      return -1;
    }

    if(nin[next_input] > 0){
      out[i] = *in[next_input];

      ++in[next_input];
      --nin[next_input];

    } else {

      d_next_input = next_input;
      break;

    } // nin[next_input] > 0

  } // for-loop

  for( unsigned k = 1; k < ninput_items.size(); ++k ){
    consume( k, ninput_items[k] - nin[k] );
  }

  consume( 0, i );

  return i;
}


int
ofdm_stream_controlled_mux_b::noutput_forecast( gr_vector_int &ninput_items,
    int available_space, int max_items_avail, std::vector<bool> &input_done )
{

  if( ninput_items[0] == 0 && input_done[0] ){
    return -1;
  }

  if( d_next_input > 0 ){
    assert( d_next_input < ninput_items.size() );

    if( ninput_items[d_next_input] == 0 && input_done[d_next_input] ){
      return -1;
    }

    if( ninput_items[d_next_input] == 0 ){
      return 0;
    }
  }

  int n_min = std::min( available_space, ninput_items[0] );

  return n_min;

}

