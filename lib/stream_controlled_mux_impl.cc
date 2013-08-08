/* -*- c++ -*- */
/* 
 * Copyright 2013 <+YOU OR YOUR COMPANY+>.
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
#include "stream_controlled_mux_impl.h"

#include <iostream>

#include <string.h>

namespace gr {
  namespace ofdm {

    stream_controlled_mux::sptr
    stream_controlled_mux::make(int streamsize)
    {
      return gnuradio::get_initial_sptr
        (new stream_controlled_mux_impl(streamsize));
    }

    /*
     * The private constructor
     */
    stream_controlled_mux_impl::stream_controlled_mux_impl(int streamsize)
      : gr::block("stream_controlled_mux",
              gr::io_signature::make2(2, -1, sizeof(unsigned short), streamsize),
              gr::io_signature::make(1, 1, streamsize))
    	, d_streamsize(streamsize)
    	, d_next_input(0)
    {}

    /*
     * Our virtual destructor.
     */
    stream_controlled_mux_impl::~stream_controlled_mux_impl()
    {
    }

    void
    stream_controlled_mux_impl::forecast (int noutput_items, gr_vector_int &ninput_items_required)
    {
      ninput_items_required[0] = noutput_items;

      for(int i = 1; i < ninput_items_required.size(); ++i)
        ninput_items_required[i] = 0;

      if(d_next_input > 0){
        assert(d_next_input < ninput_items_required.size());
        ninput_items_required[d_next_input] = 1;
      }
    }

    int
    stream_controlled_mux_impl::noutput_forecast( gr_vector_int &ninput_items,
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
    stream_controlled_mux_impl::general_work (int noutput_items,
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

    	  assert(ninput_items[0] >= noutput_items);

    	  d_next_input = 0;

    	  unsigned short next_input;
    	  int i;
    	  for(i = 0; i < noutput_items; ++i){
    	    next_input = mux[i]+1;
    	    if(next_input >= input_items.size()){
    	      std::cerr << "input mux selection out of range" << std::endl;
    	      return -1;
    	    }

    	    if(nin[next_input] > 0){
    	      memcpy(out, in[next_input], d_streamsize);

    	      out += d_streamsize;
    	      in[next_input] += d_streamsize;

    	      consume(0, 1);
    	      consume(next_input, 1);

    	      --nin[next_input];
    	    } else {
    	      d_next_input = next_input;
    	      break;
    	    }
    	  }
    	  return i;
    }

  } /* namespace ofdm */
} /* namespace gr */

