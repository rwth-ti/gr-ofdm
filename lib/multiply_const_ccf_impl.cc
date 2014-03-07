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
#include "multiply_const_ccf_impl.h"

#include <iostream>

#include "malloc16.h"

#define DEBUG 0



namespace gr {
  namespace ofdm {

    typedef float v4sf __attribute__ ((vector_size(16)));

    multiply_const_ccf::sptr
    multiply_const_ccf::make(float k)
    {
      return gnuradio::get_initial_sptr
        (new multiply_const_ccf_impl(k));
    }

    /*
     * The private constructor
     */
    multiply_const_ccf_impl::multiply_const_ccf_impl(float k)
      : gr::sync_block("multiply_const_ccf",
              gr::io_signature::make(1, 1, sizeof( gr_complex )),
              gr::io_signature::make(1, 1, sizeof( gr_complex ) ))
    , d_cache( static_cast< float * >( malloc16Align( cache_line ) ) )
    {
    	  set_k( k );
    	  set_output_multiple( cache_size / 2 ); // because treat complex as 2 floats
    }

    /*
     * Our virtual destructor.
     */
    multiply_const_ccf_impl::~multiply_const_ccf_impl()
    {
    	  if( d_cache )
    	    free16Align( d_cache );
    }

    void
    multiply_const_ccf_impl ::
    set_k( float k )
    {
      for( size_type i = 0; i < cache_size; ++i )
      {
        d_cache[ i ] = k;
      }
      d_k = k;
    }

    typedef v4sf * v4sf_ptr __attribute__ ((aligned(16)));
    typedef v4sf const * v4sfc_ptr __attribute__ ((aligned(16)));

    int
    multiply_const_ccf_impl::work(int noutput_items,
			  gr_vector_const_void_star &input_items,
			  gr_vector_void_star &output_items)
    {
    	//assert( ( (long)input_items[0] & 15 ) == 0 );
    	  //assert( ( (long)output_items[0] & 15 ) == 0 );

    	  // because treat complex as 2 floats

    	  size_type cnt = 2 * noutput_items; // multiple of cache_size

    	  {
    	    v4sfc_ptr __restrict in  = static_cast< v4sfc_ptr >( input_items[0] );
    	    v4sf_ptr  __restrict out = static_cast< v4sf_ptr >( output_items[0] );
    	    v4sfc_ptr __restrict cache = reinterpret_cast< v4sfc_ptr >( d_cache );

    	    size_type i = 0;

    	    while( cnt >= cache_size )
    	    {
    	      out[ i + 0 ] = in[ i + 0 ] * cache[ 0 ];
    	      out[ i + 1 ] = in[ i + 1 ] * cache[ 1 ];
    	      out[ i + 2 ] = in[ i + 2 ] * cache[ 2 ];
    	      out[ i + 3 ] = in[ i + 3 ] * cache[ 3 ];
    	      out[ i + 4 ] = in[ i + 4 ] * cache[ 4 ];
    	      out[ i + 5 ] = in[ i + 5 ] * cache[ 5 ];
    	      out[ i + 6 ] = in[ i + 6 ] * cache[ 6 ];
    	      out[ i + 7 ] = in[ i + 7 ] * cache[ 7 ];

    	      cnt -= cache_size;
    	      i += 8;
    	    }
    	  }

    	  return noutput_items;
    }

  } /* namespace ofdm */
} /* namespace gr */

