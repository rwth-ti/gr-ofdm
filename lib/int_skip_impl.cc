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
#include "int_skip_impl.h"

namespace gr {
  namespace ofdm {

    int_skip::sptr
    int_skip::make(int vlen, int skip, int start)
    {
      return gnuradio::get_initial_sptr
        (new int_skip_impl(vlen, skip, start));
    }

    /*
     * The private constructor
     */
    int_skip_impl::int_skip_impl(int vlen, int skip, int start)
      : gr::sync_block("int_skip",
              gr::io_signature::make(1, 1, sizeof(gr_complex) * vlen),
              gr::io_signature::make(1, 1, sizeof(gr_complex)*vlen/skip ))
    	, d_vlen( vlen )
    	, d_skip( skip )
    	, d_start( start )
    {
    	assert( d_vlen > 0 );
    }

    /*
     * Our virtual destructor.
     */
    int_skip_impl::~int_skip_impl()
    {
    }

    int
    int_skip_impl::work(int noutput_items,
			  gr_vector_const_void_star &input_items,
			  gr_vector_void_star &output_items)
    {
    	const gr_complex *in = static_cast< const gr_complex* >( input_items[0] );
    	  gr_complex *out = static_cast< gr_complex* >( output_items[0] );


    	  for( int j = 0; j < noutput_items; ++j)
    	  {

    	    for( int i = 0; i < d_vlen ; ++i )
    	    {


    	    	if ( i % d_skip == 0 )
    	    	{
    	    		*out = in[i+d_start];
    	    		 out += 1;
    	    	}


    		}

    	  }
    	  return noutput_items;
    }

  } /* namespace ofdm */
} /* namespace gr */

