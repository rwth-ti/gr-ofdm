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
#include "stc_decoder_rx1_impl.h"

#include <iostream>

#define DEBUG 0

namespace gr {
  namespace ofdm {

    stc_decoder_rx1::sptr
    stc_decoder_rx1::make(int vlen)
    {
      return gnuradio::get_initial_sptr
        (new stc_decoder_rx1_impl(vlen));
    }

    /*
     * The private constructor
     */
    stc_decoder_rx1_impl::stc_decoder_rx1_impl(int vlen)
      : gr::sync_block("stc_decoder_rx1",
              gr::io_signature::make6(
            	        6, 6,
            	        sizeof( gr_complex ) * vlen,            // ofdm_blcoks
            	        sizeof( gr_complex ) * vlen,            // ofdm_blcoks2
            	        sizeof( gr_complex ) * vlen,            // h0
            	        sizeof( gr_complex ) * vlen,            // h1
            	        sizeof( gr_complex ) * vlen,            // h2
            	        sizeof( gr_complex ) * vlen ),          // h3
              gr::io_signature::make(1, 1, sizeof( gr_complex ) * vlen))
    	, d_vlen( vlen )
    {
    	  assert( ( vlen % 2 ) == 0 ); // alignment 16 byte
    }

    /*
     * Our virtual destructor.
     */
    stc_decoder_rx1_impl::~stc_decoder_rx1_impl()
    {
    }

    int
    stc_decoder_rx1_impl::work(int noutput_items,
			  gr_vector_const_void_star &input_items,
			  gr_vector_void_star &output_items)
    {
    	  gr_complex const * ofdm_blocks = static_cast< gr_complex const * >( input_items[0] );
    	  gr_complex const * ofdm_blocks2 = static_cast< gr_complex const * >( input_items[1] );
    	  gr_complex const * h0 = static_cast< gr_complex const * >( input_items[2] );
    	  gr_complex const * h1 = static_cast< gr_complex const * >( input_items[3] );
    	  gr_complex const * h2 = static_cast< gr_complex const * >( input_items[4] );
    	  gr_complex const * h3 = static_cast< gr_complex const * >( input_items[5] );
    	  gr_complex * out = static_cast< gr_complex * >( output_items[0] );

    	  for( int j = 0; j < d_vlen; ++j )
    	  {
    	        if( j % 2 == 0 )
    	        {
    	            out[j] = 0 ;
    	        } else {
    	            out[j] = std::conj( h1[j] ) * ofdm_blocks[j-1] - h0[j] * std::conj( ofdm_blocks[j] ) +std::conj( h3[j] ) * ofdm_blocks2[j-1] - h2[j] * std::conj( ofdm_blocks2[j] );
    	        }
    	  }

    	  return noutput_items;
    }

  } /* namespace ofdm */
} /* namespace gr */

