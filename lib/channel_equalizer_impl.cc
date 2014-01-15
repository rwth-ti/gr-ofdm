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
#include "channel_equalizer_impl.h"

#include <iostream>
#include <algorithm>

#include "malloc16.h"

#define DEBUG 0

namespace gr {
  namespace ofdm {

    channel_equalizer::sptr
    channel_equalizer::make(int vlen)
    {
      return gnuradio::get_initial_sptr
        (new channel_equalizer_impl(vlen));
    }

    /*
     * The private constructor
     */
    channel_equalizer_impl::channel_equalizer_impl(int vlen)
      : gr::block("channel_equalizer",
              gr::io_signature::make3( 3, 3,
            	        sizeof( gr_complex ) * vlen,
            	        sizeof( gr_complex ) * vlen,
            	        sizeof( char ) ),
              gr::io_signature::make(1, 1,
            	        sizeof( gr_complex ) * vlen))
     , d_vlen( vlen )
     , d_need_input( 1 )

     , d_buffer( static_cast< gr_complex * >(
         malloc16Align( sizeof( gr_complex ) * vlen ) ) )
    {
    	assert( ( vlen % 2 ) == 0 ); // alignment 16 byte
    }

    /*
     * Our virtual destructor.
     */
    channel_equalizer_impl::~channel_equalizer_impl()
    {
    	if( d_buffer )
    	    free16Align( d_buffer );
    	    //delete[] d_buffer;
    }

    void
    channel_equalizer_impl::forecast (int noutput_items, gr_vector_int &ninput_items_required)
    {
        /* <+forecast+> e.g. ninput_items_required[0] = noutput_items */
    	ninput_items_required[0] = ninput_items_required[2] = noutput_items;
    	ninput_items_required[1] = d_need_input;
    }

    typedef float __attribute__((vector_size(16))) v4sf;
    typedef float const __attribute__((vector_size(16))) v4sfc;

    int
    channel_equalizer_impl::general_work (int noutput_items,
                       gr_vector_int &ninput_items,
                       gr_vector_const_void_star &input_items,
                       gr_vector_void_star &output_items)
    {
    	  gr_complex const * ofdm_blocks =
    	    static_cast< gr_complex const * >( input_items[0] );

    	  gr_complex const * inv_ctf =
    	    static_cast< gr_complex const * >( input_items[1] );

    	  char const * frame_start = static_cast< char const * >( input_items[2] );

    	  gr_complex * out = static_cast< gr_complex * >( output_items[0] );

    	  int const nin = std::min( ninput_items[0],
    	                  std::min( ninput_items[2], noutput_items ) );
    	  int n_inv_ctf = ninput_items[1];


    	  if( DEBUG )
    	    std::cout << "EQ: nin=" << nin << " nin0=" << ninput_items[0]
    	              << " nin2=" << ninput_items[2] << " n_inv_ctf=" << ninput_items[1]
    	              << " nout=" << noutput_items
    	              << std::endl;

    	  v4sf * vbuf = reinterpret_cast< v4sf * >( d_buffer );
    	  v4sfc * vin = reinterpret_cast< v4sfc * >( ofdm_blocks );
    	  v4sf * vout = reinterpret_cast< v4sf * >( out );

    	  int i = 0;
    	//  for( ; i < nin; ++i, ofdm_blocks += d_vlen, out += d_vlen )
    	  for( ; i < nin; ++i, vin += d_vlen/2, vout += d_vlen/2, ofdm_blocks += d_vlen, out += d_vlen )
    	  {
    	    // if not first frame start, advance inv_ctf ptr if enough input available
    	    if( frame_start[i] != 0 )
    	    {
    	      if( n_inv_ctf == 0 )
    	      {
    	        d_need_input = 1;
    	        break;
    	      }


    	      std::copy( inv_ctf, inv_ctf + d_vlen, d_buffer );
    	      --n_inv_ctf;
    	      inv_ctf += d_vlen;

    	      d_need_input = 0;

    	    } // if frame-start[i] != 0


    	    // HACK!!!!!!!!!!!!!!!!!!!!!!!!!!!
    	    // leave first preamble intact, Milans SNR estimator requires this

    	#if 0
    	    if( frame_start[i] != 0 )
    	    {
    	//      std::copy( ofdm_blocks, ofdm_blocks + d_vlen, out );

    	      for( int j = 0; j < d_vlen/2; ++j )
    	      {
    	        v4sf x = vin[ j ];
    	        vout[ j ] = x;
    	      }
    	    }
    	    else
    	#endif
    	    {
    	      for( int j = 0; j < d_vlen/2; ++j )
    	      {
    	        v4sf x0 = __builtin_ia32_movsldup( vin[ j ] );
    	        v4sf x1 = vbuf[ j ];
    	        x0 *= x1;

    	        x1 = __builtin_ia32_shufps( x1, x1, 0xB1 );
    	        v4sf x2 = __builtin_ia32_movshdup( vin[ j ] );
    	        x2 *= x1;

    	        x0 = __builtin_ia32_addsubps( x0, x2 );
    	        vout[ j ] = x0;
    	      }
    	//      // Equalization
    	//      for( int j = 0; j < d_vlen; ++j )
    	//        out[j] = ofdm_blocks[j] * d_buffer[j];
    	    }

    	  } // for-loop over input

    	  if( i > 0 )
    	  {
    	    consume( 0, i );
    	    consume( 2, i );
    	  }

    	  int const tmp = ninput_items[1] - n_inv_ctf;
    	  if( tmp > 0 )
    	    consume( 1, tmp );

    	  if( DEBUG )
    	    std::cout << "EQ: leave, consume i=" << i << " and "
    	              << (ninput_items[1]-n_inv_ctf) << ", produce " << i
    	              << std::endl;

    	  return i;
    }

  } /* namespace ofdm */
} /* namespace gr */

