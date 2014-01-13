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
#include "stc_decoder_rx0_impl.h"

#include <iostream>

#define DEBUG 0

namespace gr {
  namespace ofdm {

    stc_decoder_rx0::sptr
    stc_decoder_rx0::make(int vlen)
    {
      return gnuradio::get_initial_sptr
        (new stc_decoder_rx0_impl(vlen));
    }

    /*
     * The private constructor
     */
    stc_decoder_rx0_impl::stc_decoder_rx0_impl(int vlen)
      : gr::sync_block("stc_decoder_rx0",

              gr::io_signature::make(0, 0, 0),
              gr::io_signature::make( 1, 1, sizeof( gr_complex ) * vlen ))
    	, d_vlen( vlen )
    {
        std::vector<int> in_sig(6);
        in_sig[0]= sizeof( gr_complex ) * vlen;            // ofdm_blcoks
        in_sig[1]=sizeof( gr_complex ) * vlen;           // ofdm_blcoks2
        in_sig[2]= sizeof( gr_complex ) * vlen;            // h0
        in_sig[3]=sizeof( gr_complex ) * vlen;            // h1
        in_sig[4]=sizeof( gr_complex ) * vlen;            // h2
        in_sig[5]=sizeof( gr_complex ) * vlen ;          // h3
        set_input_signature(io_signature::makev(6,6,in_sig));



    	  assert( ( vlen % 2 ) == 0 ); // alignment 16 byte
    }

    /*
     * Our virtual destructor.
     */
    stc_decoder_rx0_impl::~stc_decoder_rx0_impl()
    {
    }

    int
    stc_decoder_rx0_impl::work(int noutput_items,
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
    			out[j] = std::conj( h0[j] ) * ofdm_blocks[j] + std::conj( h2[j] ) * ofdm_blocks2[j];
    		} else {
    			out[j-1] += h1[j] * std::conj( ofdm_blocks[j] ) + h3[j] * std::conj( ofdm_blocks2[j] );
    			out[j] = 0 ;
    		}
    	  }

    	  return noutput_items;
    }

  } /* namespace ofdm */
} /* namespace gr */

