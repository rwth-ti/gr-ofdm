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
#include "interp_cir_set_noncir_to_zero_impl.h"

#include <iostream>
#include <algorithm>

#define DEBUG 0

namespace gr {
  namespace ofdm {

    interp_cir_set_noncir_to_zero::sptr
    interp_cir_set_noncir_to_zero::make(int vlen, int window)
    {
      return gnuradio::get_initial_sptr
        (new interp_cir_set_noncir_to_zero_impl(vlen, window));
    }

    /*
     * The private constructor
     */
    interp_cir_set_noncir_to_zero_impl::interp_cir_set_noncir_to_zero_impl(int vlen, int window)
      : gr::sync_block("interp_cir_set_noncir_to_zero",
              gr::io_signature::make2(
            	        2, 2,
            	        sizeof( gr_complex ) * vlen,
            	        sizeof( short ) ),
              gr::io_signature::make(1, 1, sizeof( gr_complex ) * vlen))
    	, d_vlen( vlen )
    	, d_window( window )
    {}

    /*
     * Our virtual destructor.
     */
    interp_cir_set_noncir_to_zero_impl::~interp_cir_set_noncir_to_zero_impl()
    {
    }

    int
    interp_cir_set_noncir_to_zero_impl::work(int noutput_items,
			  gr_vector_const_void_star &input_items,
			  gr_vector_void_star &output_items)
    {
    	gr_complex const * in = static_cast< gr_complex const * >( input_items[0] );
    	  short const * in_1 = static_cast< short const * >( input_items[1] );
    	  gr_complex * out = static_cast< gr_complex * >( output_items[0] );

    	  // only copy d_window items from in to out vectors
    	  // where start of window within in vector is given by in_1

    	  std::fill_n( out, d_vlen * noutput_items, gr_complex( 0, 0 ) );

    	  for( int i = 0; i < noutput_items; ++i )
    	  {

    	    int pos = in_1[ i ];

    	    for( int x = 0; x < d_window; ++x )
    	    {
    	      out[ pos ] = in[ pos ];

    	      ++pos;

    	      if( pos >= d_vlen )
    	      {
    	        pos = 0;
    	      }

    	    } // for

    	    in += d_vlen;
    	    out += d_vlen;

    	  } // for

    	  return noutput_items;
    }

  } /* namespace ofdm */
} /* namespace gr */

