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
#include "channel_equalizer_mimo_3_impl.h"

#include <iostream>
#include <algorithm>

#include "malloc16.h"

#define DEBUG 0

namespace gr {
  namespace ofdm {

    channel_equalizer_mimo_3::sptr
    channel_equalizer_mimo_3::make(int vlen)
    {
      return gnuradio::get_initial_sptr
        (new channel_equalizer_mimo_3_impl(vlen));
    }

    /*
     * The private constructor
     */
    channel_equalizer_mimo_3_impl::channel_equalizer_mimo_3_impl(int vlen)
      : gr::block("channel_equalizer_mimo_3",

              gr::io_signature::make(0, 0, 0),
              gr::io_signature::make(1, 1,
            	        sizeof( gr_complex ) * vlen))
    , d_vlen( vlen )
      , d_need_input_h0( 1 )
      , d_need_input_h1( 1 )
      , d_need_input_h2( 1 )
      , d_need_input_h3( 1 )

      , d_buffer_h0( static_cast< gr_complex * >( malloc16Align( sizeof( gr_complex ) * vlen ) ) )
      , d_buffer_h1( static_cast< gr_complex * >( malloc16Align( sizeof( gr_complex ) * vlen ) ) )
      , d_buffer_h2( static_cast< gr_complex * >( malloc16Align( sizeof( gr_complex ) * vlen ) ) )
      , d_buffer_h3( static_cast< gr_complex * >( malloc16Align( sizeof( gr_complex ) * vlen ) ) )
    {
        std::vector<int> in_sig(8);
        in_sig[0] = sizeof( gr_complex ) * vlen;    // ofdm_blocks
        in_sig[1] =sizeof( gr_complex ) * vlen;    // ofdm_blocks2
        in_sig[2] =sizeof( gr_complex ) * vlen/2;    // h0
        in_sig[3] =sizeof( gr_complex ) * vlen/2;    // h1
        in_sig[4] =sizeof( gr_complex ) * vlen/2;    // h2
        in_sig[5] =sizeof( gr_complex ) * vlen/2;    // h3
        in_sig[6] =sizeof( char );                 // frame_start
        in_sig[7] =sizeof( char );
        set_input_signature(io_signature::makev(8,8,in_sig));


    	assert( ( vlen % 2 ) == 0 ); // alignment 16 byte
    }

    /*
     * Our virtual destructor.
     */
    channel_equalizer_mimo_3_impl::~channel_equalizer_mimo_3_impl()
    {
      if( d_buffer_h0 )
		free16Align( d_buffer_h0 );
	  if( d_buffer_h1 )
		free16Align( d_buffer_h1 );
	  if( d_buffer_h2 )
		free16Align( d_buffer_h2 );
	  if( d_buffer_h3 )
		free16Align( d_buffer_h3 );
    }

    void
    channel_equalizer_mimo_3_impl::forecast (int noutput_items, gr_vector_int &ninput_items_required)
    {
        /* <+forecast+> e.g. ninput_items_required[0] = noutput_items */
      ninput_items_required[0] = ninput_items_required[6] = ninput_items_required[1] = ninput_items_required[7] = noutput_items;
	  ninput_items_required[2] = d_need_input_h0;
	  ninput_items_required[3] = d_need_input_h1;
	  ninput_items_required[4] = d_need_input_h2;
	  ninput_items_required[5] = d_need_input_h3;
    }

    int
    channel_equalizer_mimo_3_impl::general_work (int noutput_items,
                       gr_vector_int &ninput_items,
                       gr_vector_const_void_star &input_items,
                       gr_vector_void_star &output_items)
    {
    	  gr_complex const * ofdm_blocks = static_cast< gr_complex const * >( input_items[0] );
    	  gr_complex const * ofdm_blocks2 = static_cast< gr_complex const * >( input_items[1] );

    	  gr_complex const * ctf_0 = static_cast< gr_complex const * >( input_items[2] );
    	  gr_complex const * ctf_1 = static_cast< gr_complex const * >( input_items[3] );
    	  gr_complex const * ctf_2 = static_cast< gr_complex const * >( input_items[4] );
    	  gr_complex const * ctf_3 = static_cast< gr_complex const * >( input_items[5] );

    	  char const * frame_start = static_cast< char const * >( input_items[6] );
    	  char const * frame_start2 = static_cast< char const * >( input_items[7] );

    	  gr_complex * out = static_cast< gr_complex * >( output_items[0] );

    	  int const nin = std::min( ninput_items[0],
    	                   std::min( ninput_items[1],
    	                   std::min( ninput_items[6],
    	                   std::min( ninput_items[7], noutput_items ) ) ) );
    	   int n_ctf_0 = ninput_items[2];
    	   int n_ctf_1 = ninput_items[3];
    	   int n_ctf_2 = ninput_items[4];
    	   int n_ctf_3 = ninput_items[5];;

    	  if( DEBUG )
    	    std::cout << "EQ: nin=" << nin << " nin0=" << ninput_items[0]
    	              << " nin2=" << ninput_items[3]
    	              << " n_ctf_0=" << ninput_items[1] << " n_ctf_1=" << ninput_items[2]
    	              << " nout=" << noutput_items
    	              << std::endl;

    	  int i = 0;

    	//  for( ; i < nin; ++i, ofdm_blocks += d_vlen, out += d_vlen )
    	  for( ; i < nin; ++i, ofdm_blocks += d_vlen, ofdm_blocks2 += d_vlen, out += d_vlen )
    	  {
    		//gr_complex norm = 0.5;
    		gr_complex norm_c = 1 / sqrt(2);
    		gr_complex norm = 2.0;
    		//gr_complex norm_c = sqrt(2);

    	    // if not first frame start, advance ctf_0 ptr if enough input available

    		if ( frame_start[i] != frame_start2[i] )
    		    {
    		        std::cout << " X ";
    		    }


    	    if( frame_start[i] != 0 )
    	    {
    	      if( n_ctf_0 == 0 )
    	      {
    	        d_need_input_h0 = 1;
    	        if( DEBUG )
    	            std::cout << "d_need_input_h0" << std::endl;
    	        break;
    	      }
    		  if( n_ctf_1 == 0 )
    	      {
    	        d_need_input_h1 = 1;
    	        if( DEBUG )
    	        	std::cout << "d_need_input_h1" << std::endl;
    	        break;
    	      }

    	      std::copy( ctf_0, ctf_0 + d_vlen/2, d_buffer_h0 );
    		  std::copy( ctf_1, ctf_1 + d_vlen/2, d_buffer_h1 );

    	      --n_ctf_0;
    	      ctf_0 += d_vlen/2;
    		  --n_ctf_1;
    	      ctf_1 += d_vlen/2;

    	      d_need_input_h0 = 0;
    		  d_need_input_h1 = 0;
    	    }
    	    if( frame_start2[i] != 0 )
    	    {

    	      if( n_ctf_2 == 0 )
    	      {
    	        d_need_input_h2 = 1;
    	        if( DEBUG )
    	            std::cout << "d_need_input_h2" << std::endl;
    	        break;
    	      }
    	      if( n_ctf_3 == 0 )
    	      {
    	        d_need_input_h3 = 1;
    	        if( DEBUG )
    	            std::cout << "d_need_input_h3" << std::endl;
    	        break;
    	      }

    	      std::copy( ctf_2, ctf_2 + d_vlen/2, d_buffer_h2 );
    	      std::copy( ctf_3, ctf_3 + d_vlen/2, d_buffer_h3 );

    	      --n_ctf_2;
    	      ctf_2 += d_vlen/2;
    	      --n_ctf_3;
    	      ctf_3 += d_vlen/2;

    	      d_need_input_h2 = 0;
    	      d_need_input_h3 = 0;
    	    }
    	    {

    	     // Equalization
    	     for( int k = 0; k < d_vlen; k++ )
    		 {
    	    	 int l = k / 2;

    	    	 if ( frame_start[i] == 1 )
    	    	 {
    	    		 if ( k % 2 == 0 )
    	    		 {
    	    			 out[k] = ofdm_blocks[k] *  std::conj( d_buffer_h0[l] ) * norm / ( std::abs(d_buffer_h0[l]) * std::abs(d_buffer_h0[l]) );
    	    		 } else {
    	    			 out[k] = ofdm_blocks[k] * std::conj( d_buffer_h1[l] ) * norm / ( std::abs(d_buffer_h1[l]) * std::abs(d_buffer_h1[l]) );
    	    		 }

    	    	// if pilot
    	    	 } else if ( k == 24 || k == 44 || k == 64 || k == 84 || k == 124 || k == 144 || k == 164 || k == 184 )
    	    	 {
    	    		 out[k] = (ofdm_blocks[k] * std::conj( d_buffer_h0[l] )+ ofdm_blocks2[k] * std::conj( d_buffer_h2[l] )) * norm / ( std::abs(d_buffer_h0[l]) * std::abs(d_buffer_h0[l]) + std::abs(d_buffer_h2[l]) * std::abs(d_buffer_h2[l]) );

    	    	// if pair part of pilot
    	    	 } else if ( k == 25 || k == 45 || k == 65 || k == 85 || k == 125 || k == 145 || k == 165 || k == 185 )
    	    	 {
    	    		 out[k] = ( - std::conj( ofdm_blocks[k] ) * d_buffer_h0[l] - std::conj( ofdm_blocks2[k] ) * d_buffer_h2[l] ) * norm_c / ( std::abs(d_buffer_h0[l]) * std::abs(d_buffer_h0[l]) + std::abs(d_buffer_h2[l]) * std::abs(d_buffer_h2[l]));

    	    	 } else {
    	    		 if ( k % 2 == 0 )
    	    		 {
    	    			 out[k] = ( ( ofdm_blocks[k] * std::conj( d_buffer_h0[l] ) + std::conj( ofdm_blocks[k+1] ) * d_buffer_h1[l] )  + ( ofdm_blocks2[k] * std::conj( d_buffer_h2[l] ) + std::conj( ofdm_blocks2[k+1] ) * d_buffer_h3[l] ) ) / ( std::abs(d_buffer_h0[l]) * std::abs(d_buffer_h0[l]) + std::abs(d_buffer_h1[l]) * std::abs(d_buffer_h1[l]) + std::abs(d_buffer_h3[l]) * std::abs(d_buffer_h3[l])+ std::abs(d_buffer_h2[l]) * std::abs(d_buffer_h2[l]));
    	    		 } else {
    	    			 out[k] = ( ofdm_blocks[k-1] * std::conj( d_buffer_h1[l] ) - std::conj( ofdm_blocks[k] ) * d_buffer_h0[l] + ofdm_blocks2[k-1] * std::conj( d_buffer_h3[l] ) - std::conj( ofdm_blocks2[k] ) * d_buffer_h2[l] )  / (  std::abs(d_buffer_h0[l]) * std::abs(d_buffer_h0[l]) + std::abs(d_buffer_h1[l]) * std::abs(d_buffer_h1[l]) + std::abs(d_buffer_h3[l]) * std::abs(d_buffer_h3[l])+ std::abs(d_buffer_h2[l]) * std::abs(d_buffer_h2[l]));
    	    		 }
    	    	 }
    		 }
    	    }

    	  } // for-loop over input

    	  if( i > 0 )
    	  {
    		consume( 0, i );
    	    consume( 1, i );
    	    consume( 6, i );
    	    consume( 7, i );
    	  }

    	  int const tmp_0 = ninput_items[2] - n_ctf_0;
    	  if( tmp_0 > 0 )
    	    consume( 2, tmp_0 );
    	  int const tmp_1 = ninput_items[3] - n_ctf_1;
    	  if( tmp_1 > 0 )
    	    consume( 3, tmp_1 );
    	  int const tmp_2 = ninput_items[4] - n_ctf_2;
    	  if( tmp_2 > 0 )
    	    consume( 4, tmp_2 );
    	  int const tmp_3 = ninput_items[5] - n_ctf_3;
    	  if( tmp_3 > 0 )
    	    consume( 5, tmp_3 );

    	  if( DEBUG )
    		    std::cout << "EQ: leave, consume i=" << i << " and "
    		              << (ninput_items[2]-n_ctf_0) << ", produce " << i
    		              << (ninput_items[3]-n_ctf_1) << ", produce " << i
    		              << (ninput_items[4]-n_ctf_2) << ", produce " << i
    		              << (ninput_items[5]-n_ctf_3) << ", produce " << i
    		              << std::endl;

    	  return i;
    }

  } /* namespace ofdm */
} /* namespace gr */

