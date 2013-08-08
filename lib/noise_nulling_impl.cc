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
#include "noise_nulling_impl.h"

#include <string.h>
#include <iostream>

#define DEBUG 0


namespace gr {
  namespace ofdm {

    noise_nulling::sptr
    noise_nulling::make(int vlen, int keep)
    {
      return gnuradio::get_initial_sptr
        (new noise_nulling_impl(vlen, keep));
    }

    /*
     * The private constructor
     */
    noise_nulling_impl::noise_nulling_impl(int vlen, int keep)
      : gr::sync_block("noise_nulling",
              gr::io_signature::make(1, 1, sizeof(gr_complex) * vlen),
              gr::io_signature::make(1, 1, sizeof(gr_complex) * vlen))
    	, d_vlen( vlen )
    	, d_keep( keep )
    {
    	assert( d_vlen > 0 );
    }

    /*
     * Our virtual destructor.
     */
    noise_nulling_impl::~noise_nulling_impl()
    {
    }

    int
    noise_nulling_impl::work(int noutput_items,
			  gr_vector_const_void_star &input_items,
			  gr_vector_void_star &output_items)
    {
    	  const gr_complex *in = static_cast< const gr_complex* >( input_items[0] );
    	  gr_complex *out = static_cast< gr_complex* >( output_items[0] );


    	  for( int j = 0; j < noutput_items; ++j)
    	  {

    	    for( int i = 0; i < d_vlen ; ++i )
    	    {

    	    	if ( i < d_keep+1)
    	    	{
    	    		out[i] = in[i];
    	    		out += 1;
    	    	}
    	    	else
    	    	{
    	    		out[i] = 0.0;
    	    		out += 1;
    	    	}

    		}


    	  }
    	  return noutput_items;
    }

  } /* namespace ofdm */
} /* namespace gr */

