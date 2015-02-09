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
#include "channel_equalizer_mimo_12_impl.h"

#include <iostream>
#include <algorithm>
#include "malloc16.h"

#define DEBUG 0

namespace gr {
  namespace ofdm {

    channel_equalizer_mimo_12::sptr
    channel_equalizer_mimo_12::make(int vlen)
    {
      return gnuradio::get_initial_sptr
        (new channel_equalizer_mimo_12_impl(vlen));
    }

    /*
     * The private constructor
     */
    channel_equalizer_mimo_12_impl::channel_equalizer_mimo_12_impl(int vlen)
      : gr::block("channel_equalizer_mimo_12",
              gr::io_signature::make(0, 0, 0),
              gr::io_signature::make( 1, 1,
            	        sizeof( gr_complex ) * vlen))
    , d_vlen( vlen )
    , d_need_input_h0( 1 )
    , d_need_input_h1( 1 )

    , d_buffer_h0( static_cast< gr_complex * >( malloc16Align( sizeof( gr_complex ) * vlen ) ) )
    , d_buffer_h1( static_cast< gr_complex * >( malloc16Align( sizeof( gr_complex ) * vlen ) ) )
    {

         std::vector<int> in_sig(5);
         in_sig[0] = sizeof( gr_complex ) * vlen;    // ofdm_blocks
         in_sig[1] = sizeof( gr_complex ) * vlen;    // ofdm_blocks 1
         in_sig[2] = sizeof( gr_complex ) * vlen;  // h0
         in_sig[3] = sizeof( gr_complex ) * vlen;  // h1
         in_sig[4] = sizeof( char );				 // trigger
         //in_sig[5] = sizeof( char );				 // trigger 1
         set_input_signature(io_signature::makev(5,5,in_sig));


    	 assert( ( vlen % 2 ) == 0 ); // alignment 16 byte
    }

    /*
     * Our virtual destructor.
     */
    channel_equalizer_mimo_12_impl::~channel_equalizer_mimo_12_impl()
    {
    	 if( d_buffer_h0 )
    	    free16Align( d_buffer_h0 );
    	 if( d_buffer_h1 )
    	    free16Align( d_buffer_h1 );
    }

    void
    channel_equalizer_mimo_12_impl::forecast (int noutput_items, gr_vector_int &ninput_items_required)
    {
        /* <+forecast+> e.g. ninput_items_required[0] = noutput_items */
      ninput_items_required[0] = ninput_items_required[1] = ninput_items_required[4] = noutput_items;
	  ninput_items_required[2] = d_need_input_h0;
	  ninput_items_required[3] = d_need_input_h1;
    }

    int
    channel_equalizer_mimo_12_impl::general_work (int noutput_items,
                       gr_vector_int &ninput_items,
                       gr_vector_const_void_star &input_items,
                       gr_vector_void_star &output_items)
    {
    	gr_complex const * ofdm_blocks = static_cast< gr_complex const * >( input_items[0] );
    	gr_complex const * ofdm_blocks_1 = static_cast< gr_complex const * >( input_items[1] );

    	  gr_complex const * ctf_0 = static_cast< gr_complex const * >( input_items[2] );
    	  gr_complex const * ctf_1 = static_cast< gr_complex const * >( input_items[3] );

    	  char const * frame_start = static_cast< char const * >( input_items[4] );
    	  //char const * frame_start_1 = static_cast< char const * >( input_items[5] );

    	  gr_complex * out = static_cast< gr_complex * >( output_items[0] );

    	  int const nin = std::min( ninput_items[0],std::min( ninput_items[1],
    					  std::min( ninput_items[4], noutput_items ) ) ) ;

    	 // int const nin = std::min( ninput_items[0],
    				//	  std::min( ninput_items[4], noutput_items ) )  ;
    	 // int const nin_1 = std::min( ninput_items[1],
    	      			//		  std::min( ninput_items[5], noutput_items ) )  ;
    	  int n_ctf_0 = ninput_items[2];
    	  int n_ctf_1 = ninput_items[3];

    	  if( DEBUG )
    	    std::cout << "EQ: nin=" << nin << " nin0=" << ninput_items[0]
    	              << " nin2=" << ninput_items[4]
    	              << " n_ctf_0=" << ninput_items[2] << " n_ctf_1=" << ninput_items[3]
    	              << " nout=" << noutput_items
    	              << std::endl;

    	  int i = 0;
    	  //gr_complex ijk = 0.5;

    	//  for( ; i < nin; ++i, ofdm_blocks += d_vlen, out += d_vlen )
    	  for( ; i < nin; ++i, ofdm_blocks += d_vlen, ofdm_blocks_1 += d_vlen, out += d_vlen )
    	  {
    		//gr_complex norm = 0.5;
    		//gr_complex norm_c = 1 / sqrt(2);
    		//gr_complex norm = 2.0;
    		//gr_complex norm_c = sqrt(2);

    	    // if not first frame start, advance ctf_0 ptr if enough input available
    	    if( frame_start[i] != 0 )//| frame_start_1[i] != 0 )
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

    	      std::copy( ctf_0, ctf_0 + d_vlen, d_buffer_h0 );
    		  std::copy( ctf_1, ctf_1 + d_vlen, d_buffer_h1 );

    	      --n_ctf_0;
    	      ctf_0 += d_vlen;
    		  --n_ctf_1;
    	      ctf_1 += d_vlen;

    	      d_need_input_h0 = 0;
    		  d_need_input_h1 = 0;
    	    }

/*    	    if( frame_start_1[i] != 0 )
    	    {
//    	      if( n_ctf_0 == 0 )
//    	      {
//    	        d_need_input_h0 = 1;
//    	        if( DEBUG )
//    	            std::cout << "d_need_input_h0" << std::endl;
//    	        break;
//    	      }
    		  if( n_ctf_1 == 0 )
    	      {
    	        d_need_input_h1 = 1;
    	        if( DEBUG )
    	        	std::cout << "d_need_input_h1" << std::endl;
    	        break;
    	      }

//    	      std::copy( ctf_0, ctf_0 + d_vlen, d_buffer_h0 );
    		  std::copy( ctf_1, ctf_1 + d_vlen, d_buffer_h1 );

//    	      --n_ctf_0;
//    	      ctf_0 += d_vlen;
    		  --n_ctf_1;
    	      ctf_1 += d_vlen;

//    	      d_need_input_h0 = 0;
    		  d_need_input_h1 = 0;
    	    }*/


    	     // Equalization
    	     for( int k = 0; k < d_vlen; k++ )
    		 {
    	    out[k] = (ofdm_blocks[k] *  d_buffer_h0[k]  + ofdm_blocks_1[k] *  d_buffer_h1[k])/ ( d_buffer_h0[k] + d_buffer_h1[k]);
    	    //out[k] = (ofdm_blocks[k] + ofdm_blocks_1[k])*ijk;// *  d_buffer_h1[k])/ ( d_buffer_h1[k]);
  	    //out[k] = (ofdm_blocks_1[k]);
//    	    std::cout << "ofdm_blocks=" << k << "=" << ofdm_blocks[k]
//    	        	  << "ofdm_blocks_1=" << k << "=" << ofdm_blocks_1[k]
//    	        	  << "out=" << k << "=" << out[k]
//    	        	  << std::endl;
    		 }

    	  } // for-loop over input

    	  if( i > 0 )
    	  {
    		consume( 0, i );
    		consume( 1, i );
    	    consume( 4, i );
    	    //consume( 5, i );
    	  }

    	  int const tmp_0 = ninput_items[2] - n_ctf_0;
    	  if( tmp_0 > 0 )
    	    consume( 2, tmp_0 );
    	  int const tmp_1 = ninput_items[3] - n_ctf_1;
    	  if( tmp_1 > 0 )
    	    consume( 3, tmp_1 );

    	  if( DEBUG )
    	    std::cout << "EQ: leave, consume i=" << i << " and "
    	              << (ninput_items[1]-n_ctf_0) << ", produce " << i
    	              << (ninput_items[2]-n_ctf_1) << ", produce " << i
    	              << std::endl;

    	  return i;
    }

  } /* namespace ofdm */
} /* namespace gr */

