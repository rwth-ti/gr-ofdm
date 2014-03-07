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
#include "multiply_const_vcc_impl.h"

#include "malloc16.h"

#include <iostream>
#include <algorithm>

#define DEBUG 0

namespace gr {
  namespace ofdm {

    multiply_const_vcc::sptr
    multiply_const_vcc::make(std::vector< gr_complex > const &k)
    {
      return gnuradio::get_initial_sptr
        (new multiply_const_vcc_impl(k));
    }

    /*
     * The private constructor
     */
    multiply_const_vcc_impl::multiply_const_vcc_impl(std::vector< gr_complex > const &k)
      : gr::sync_block("multiply_const_vcc",
              gr::io_signature::make(1, 1, sizeof( gr_complex ) * k.size()),
              gr::io_signature::make(1, 1, sizeof( gr_complex ) * k.size()))
    , d_vlen( k.size() )
    , d_buffer( static_cast< gr_complex * >(
        malloc16Align( sizeof( gr_complex ) * k.size() ) ) )
    {
    	assert( ( d_vlen % 2 ) == 0 ); // 16 byte alignment
    	std::copy( k.begin(), k.end(), d_buffer );
    }

    /*
     * Our virtual destructor.
     */
    multiply_const_vcc_impl::~multiply_const_vcc_impl()
    {
    	  if( d_buffer )
    	    free16Align( d_buffer );
    }

    typedef float __attribute__((vector_size(16))) v4sf;
    typedef float const __attribute__((vector_size(16))) v4sfc;

    int
    multiply_const_vcc_impl::work(int noutput_items,
			  gr_vector_const_void_star &input_items,
			  gr_vector_void_star &output_items)
    {
    	  v4sfc const * in = static_cast< v4sfc * >( input_items[0] );
    	  v4sf * out = static_cast< v4sf * >( output_items[0] );

    	  v4sf * buf = reinterpret_cast< v4sf * >( d_buffer );

    	  for( int i = 0; i < noutput_items; ++i, in += d_vlen/2, out += d_vlen/2 )
    	  {
    	    for( int j = 0; j < d_vlen/2; ++j )
    	    {
    	      v4sf x0 = __builtin_ia32_movsldup( buf[ j ] );
    	      v4sf x1 = in[ j ];
    	      x0 *= x1;

    	      x1 = __builtin_ia32_shufps( x1, x1, 0xB1 );
    	      v4sf x2 = __builtin_ia32_movshdup( buf[ j ] );
    	      x2 *= x1;

    	      x0 = __builtin_ia32_addsubps( x0, x2 );
    	      out[ j ] = x0;

    	    } // element-wise complex multiplication with d_buffer

    	  } // for-loop over input

    	  return noutput_items;
    }

  } /* namespace ofdm */
} /* namespace gr */

