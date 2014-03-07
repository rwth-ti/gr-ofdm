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
#include "static_mux_v_impl.h"

#include <cstring>

#include <iostream>
#include <algorithm>

#define DEBUG 0

namespace gr {
  namespace ofdm {

    static_mux_v::sptr
    static_mux_v::make(int streamsize, const std::vector<int> &mux_ctrl)
    {
      return gnuradio::get_initial_sptr
        (new static_mux_v_impl(streamsize, mux_ctrl));
    }

    /*
     * The private constructor
     */
    static_mux_v_impl::static_mux_v_impl(int streamsize, const std::vector<int> &mux_ctrl)
      : gr::block("static_mux_v",
              gr::io_signature::make(1, -1, streamsize),
              gr::io_signature::make(1,  1, streamsize ))
    	, d_streamsize( streamsize )
    	, d_mux_ctrl( mux_ctrl )
    	, d_mpos( 0 )
    	, d_msize( mux_ctrl.size() )
    {
    	  assert( d_msize > 0 );

    	  if(DEBUG)
    	    std::cout << "[static mux " << unique_id() << "] msize=" << d_msize
    	              << std::endl;

    	  assert( *std::max_element( mux_ctrl.begin(), mux_ctrl.end() ) >= 0 );
    }

    /*
     * Our virtual destructor.
     */
    static_mux_v_impl::~static_mux_v_impl()
    {
    }

    void
    static_mux_v_impl::forecast (int noutput_items, gr_vector_int &ninput_items_required)
    {
        /* <+forecast+> e.g. ninput_items_required[0] = noutput_items */
    	  for(int i = 0; i < ninput_items_required.size(); ++i)
    	    ninput_items_required[i] = 0;

    	  int nout = noutput_items;
    	  int i = d_mpos;
    	  while( nout > 0 )
    	  {
    	    const int pos = d_mux_ctrl[i];
    	    if( pos >= 0 )
    	    {
    	      ++ninput_items_required[pos]; --nout;
    	    }
    	    i = (i+1) % d_msize;
    	  }

    	  // TODO more precise hint
    }

    int
    static_mux_v_impl::noutput_forecast( gr_vector_int &ninput_items,
        int available_space, int max_items_avail, std::vector<bool> &input_done )
    {

      int next_input = d_mux_ctrl[d_mpos];

      if( next_input >= 0 ){
        assert( next_input < ninput_items.size() );

        if( ninput_items[next_input] == 0 && input_done[next_input] ){
          return -1;
        }

        if( ninput_items[next_input] == 0 ){
          return 0;
        }
      }


      return available_space;

    }

    int
    static_mux_v_impl::general_work (int noutput_items,
                       gr_vector_int &ninput_items,
                       gr_vector_const_void_star &input_items,
                       gr_vector_void_star &output_items)
    {
    	if(DEBUG)
    	    std::cout << "[static mux " << unique_id() << "] entered, state is "
    	              << "streams=" << input_items.size()
    	              << " nout=" << noutput_items;


    	  char *out = static_cast<char*>(output_items[0]);

    	  gr_vector_int nin( ninput_items );

    	  const char *in[input_items.size()];
    	  for( gr_vector_const_void_star::size_type i = 0;
    	       i < input_items.size();
    	       ++i )
    	  {
    	    in[i] = static_cast<const char*>(input_items[i]);

    	    if(DEBUG)
    	      std::cout << " nin[" << i << "]=" << nin[i];
    	  } // for-loop


    	  if(DEBUG)
    	    std::cout << std::endl;

    	  int mpos = d_mpos;
    	  int produced = 0;

    	  while( produced < noutput_items )
    	  {
    	    const int next_input = d_mux_ctrl[mpos];

    	    if( DEBUG )
    	      std::cout << "next_input = " << next_input << std::endl;

    	    if( next_input >= 0 )
    	    {
    	      if( nin[next_input] == 0 )
    	      {
    	        if(DEBUG)
    	          std::cout << "Break, nin[" << next_input << "]=0" << std::endl;
    	        break;
    	      }

    	      memcpy(out, in[next_input], d_streamsize);

    	      out += d_streamsize;
    	      in[next_input] += d_streamsize;

    	      --nin[next_input];
    	      ++produced;

    	    } // if( next_input >= 0 )

    	    ++mpos;
    	    mpos %= d_msize;

    	  } // while-loop


    	  for( int j = 0; j < ninput_items.size(); ++j )
    	  {
    	    if( nin[j] != ninput_items[j] )
    	    {
    	      consume( j, ninput_items[j] - nin[j] );
    	    }
    	  }

    	  d_mpos = mpos;

    	  if(DEBUG){

    	    std::cout << "[static mux] leave process, d_mpos=" << d_mpos
    	              << " produce " << produced << " items";

    	    for( unsigned int k = 0; k < nin.size(); ++k ){
    	      std::cout << " nin[" << k << "]=" << nin[k];
    	    }

    	    std::cout << std::endl;

    	  } // DEBUG


    	  return produced;
    }

    bool
    static_mux_v_impl::check_topology( int ninputs, int noutputs )
    {
      if(DEBUG)
        std::cout << "[static mux " << unique_id() << "] check_topology"
                  << " ninputs=" << ninputs << " noutputs=" << noutputs
                  << std::endl;

      for( int i = 0; i < d_mux_ctrl.size(); ++i ){
        if( d_mux_ctrl[i] < -1 || d_mux_ctrl[i] >= ninputs ){

          if(DEBUG)
            std::cout << "[static mux " << unique_id() << "] check topology failed"
                      << std::endl;

          return false;
        }
      }
      return true;
    }

  } /* namespace ofdm */
} /* namespace gr */

