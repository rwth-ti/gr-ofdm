/* -*- c++ -*- */
/* 
 * Copyright 2014 Institute for Theoretical Information Technology,
 *                RWTH Aachen University
 *                www.ti.rwth-aachen.de
 * 
 * This is free software; you can redistribute it and/or modify
 * it under the terms of the GNU General Public License as published by
 * the Free Software Foundation; either version 3, or (at your option)
 * any later version.
 * 
 * This software is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 * GNU General Public License for more details.
 * 
 * You should have received a copy of the GNU General Public License
 * along with this software; see the file COPYING.  If not, write to
 * the Free Software Foundation, Inc., 51 Franklin Street,
 * Boston, MA 02110-1301, USA.
 */

#ifdef HAVE_CONFIG_H
#include "config.h"
#endif

#include <gnuradio/io_signature.h>
#include "stream_controlled_mux_b_impl.h"

#include <iostream>

#include <string.h>

namespace gr {
  namespace ofdm {

    stream_controlled_mux_b::sptr
    stream_controlled_mux_b::make()
    {
      return gnuradio::get_initial_sptr
        (new stream_controlled_mux_b_impl());
    }

    /*
     * The private constructor
     */
    stream_controlled_mux_b_impl::stream_controlled_mux_b_impl()
      : gr::block("stream_controlled_mux_b",
              gr::io_signature::make2(2, -1, sizeof(char), sizeof(char)),
              gr::io_signature::make(1, 1, sizeof(char)))
    	, d_next_input(0)
    {}

    /*
     * Our virtual destructor.
     */
    stream_controlled_mux_b_impl::~stream_controlled_mux_b_impl()
    {
    }

    void
    stream_controlled_mux_b_impl::forecast (int noutput_items, gr_vector_int &ninput_items_required)
    {
        /* <+forecast+> e.g. ninput_items_required[0] = noutput_items */
    	  ninput_items_required[0] = noutput_items;

    	  for(int i = 1; i < ninput_items_required.size(); ++i)
    	    ninput_items_required[i] = 0;

    	  if(d_next_input > 0){
    	    assert(d_next_input < ninput_items_required.size());
    	    ninput_items_required[d_next_input] = 1;
    	  }
    }

    int
    stream_controlled_mux_b_impl::noutput_forecast( gr_vector_int &ninput_items,
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

    int
    stream_controlled_mux_b_impl::general_work (int noutput_items,
                       gr_vector_int &ninput_items,
                       gr_vector_const_void_star &input_items,
                       gr_vector_void_star &output_items)
    {
    	  const char *mux = static_cast<const char*>(input_items[0]);
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

  } /* namespace ofdm */
} /* namespace gr */

