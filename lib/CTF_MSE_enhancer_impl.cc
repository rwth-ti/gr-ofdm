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
#include "CTF_MSE_enhancer_impl.h"


#include "malloc16.h"

#include <iostream>
#include <algorithm>

#define DEBUG 0

namespace gr {
  namespace ofdm {

    CTF_MSE_enhancer::sptr
    CTF_MSE_enhancer::make(int vlen, int cir_len)
    {
      return gnuradio::get_initial_sptr
        (new CTF_MSE_enhancer_impl(vlen, cir_len));
    }

    /*
     * The private constructor
     */
    CTF_MSE_enhancer_impl::CTF_MSE_enhancer_impl(int vlen, int cir_len)
      : gr::sync_block("CTF_MSE_enhancer",
              gr::io_signature::make( 1, 1, sizeof( gr_complex ) * vlen),
              gr::io_signature::make( 1, 1, sizeof( gr_complex ) * vlen ))
     , d_vlen( vlen )
     , d_cir_len( cir_len )

     , d_fd_filter( static_cast< gr_complex * >(
         malloc16Align( ( d_vlen/2 + 1 ) * sizeof( gr_complex ) ) ) )
    {
    	  assert( cir_len > 0 );
    	  assert( ( d_vlen % 4 ) == 0 );

    	  boost::shared_ptr< gr::fft::fft_complex> invfft(
    	    new gr::fft::fft_complex( vlen, false ) );

    	  boost::shared_ptr< gr::fft::fft_complex > fwdfft(
    	    new gr::fft::fft_complex( vlen, true, 1 ) );
    	  //trying to fix the fft_complex problem

    	//  fwdfft->d_inbuf = invfft->get_outbuf();
    	//  fwdfft->d_outbuf = invfft->get_inbuf();

    	  boost::shared_ptr< gr::fft::fft_real_fwd > fwdrfft(
    	      new gr::fft::fft_real_fwd ( vlen ) );

    	  boost::shared_ptr< gr::fft::fft_real_rev > invrfft(
    	      new gr::fft::fft_real_rev ( vlen, 1 ) );

    	  d_invfft = invfft;
    	  d_fwdfft = fwdfft;
    	  d_fwdrfft = fwdrfft;
    	  d_invrfft = invrfft;

    	  buf1 = invfft->get_inbuf();
    	  buf2 = invfft->get_outbuf();
    	  buf3 = fwdrfft->get_inbuf();
    	  buf4 = fwdrfft->get_outbuf();

    	  assert( fwdrfft->inbuf_length() == d_vlen );
    	  assert( fwdrfft->outbuf_length() == (d_vlen/2+1) );

    	  set_fd_filter();
    }

    /*
     * Our virtual destructor.
     */
    CTF_MSE_enhancer_impl::~CTF_MSE_enhancer_impl()
    {
    	  if( d_fd_filter )
    	    free16Align( static_cast< void * >( d_fd_filter ) );
    }

    void
    CTF_MSE_enhancer_impl ::
    set_fd_filter()
    {
      // Correlation with rect-func of width d_cir_len
      // conjugate transfer function -> mirror rect

      std::fill( buf3, buf3 + d_vlen, 0.0 );

      for( int i = 0; i < d_cir_len; ++i )
        buf3[i] = 1.0;


      d_fwdrfft->execute();

      for( int i = 0; i < d_vlen/2+1; ++i )
      {
        d_fd_filter[i] = std::conj( buf4[i] );
      }
    }

    typedef float __attribute__((vector_size(16))) v4sf;

    int
    CTF_MSE_enhancer_impl::work(int noutput_items,
			  gr_vector_const_void_star &input_items,
			  gr_vector_void_star &output_items)
    {
    	gr_complex const * in = static_cast< gr_complex const * >( input_items[0] );
    	  gr_complex * out = static_cast< gr_complex * >( output_items[0] );

    	  v4sf * vfbuf2 = reinterpret_cast< v4sf * >( buf2 );
    	  v4sf * vfbuf3 = reinterpret_cast< v4sf * >( buf3 );
    	  v4sf * vfbuf4 = reinterpret_cast< v4sf * >( buf4 );
    	  v4sf * vffilt = reinterpret_cast< v4sf * >( d_fd_filter );

    	  for( int i = 0; i < noutput_items; ++i, in += d_vlen, out += d_vlen )
    	  {
    	    // CTF -> CIR
    	    std::copy( in, in + d_vlen, buf1 );
    	    d_invfft->execute();


    	    // | CIR | ^ 2
    	    for( int j = 0; j < d_vlen/4; ++j )
    	    {
    	      v4sf const & x = vfbuf2[ 2*j ];
    	      v4sf const & y = vfbuf2[ 2*j + 1 ];
    	      v4sf x2 = x * x;
    	      v4sf y2 = y * y;
    	      x2 = __builtin_ia32_haddps( x2, y2 );
    	      vfbuf3[ j ] = x2;
    	    }

    	    // SSE3 is wonderful! It speeds up complex math significantly.


    	    // cyclic convolution with rect of size cir_len
    	    // FFT -> mult -> IFFT
    	    d_fwdrfft->execute();

    	//    for( int j = 0; j < d_vlen/2+1; ++j )
    	//      buf4[j] = buf4[j] * d_fd_filter[j];

    	    for( int j = 0; j < d_vlen/4; ++j )
    	    {
    	      v4sf x0 = __builtin_ia32_movsldup( vfbuf4[ j ] );
    	      v4sf x1 = vffilt[ j ];
    	      x0 *= x1;

    	      x1 = __builtin_ia32_shufps( x1, x1, 0xB1 );
    	      v4sf x2 = __builtin_ia32_movshdup( vfbuf4[ j ] );
    	      x2 *= x1;

    	      x0 = __builtin_ia32_addsubps( x0, x2 );
    	      vfbuf4[ j ] = x0;

    	    } // for-loop, element-wise complex multiplication

    	    buf4[ d_vlen/2 ] = buf4[ d_vlen/2 ] * d_fd_filter[ d_vlen/2 ];


    	    //some fix by pranav
    	    std::copy( buf4, buf4 + d_vlen/2 + 1, d_invrfft->get_inbuf() );

    	    d_invrfft->execute();

    	    //part 2 of fix
    	    std::copy( d_invrfft->get_outbuf(), d_invrfft->get_outbuf() + d_vlen, buf3 );

    	    // find position where maximum energy in rect-window
    	    short ind = 0;
    	    float val = buf3[ 0 ];
    	    for( int j = 1; j < d_vlen; ++j )
    	    {
    	      if( buf3[ j ] > val )
    	      {
    	        val = buf3[ j ];
    	        ind = j;
    	      }
    	    } // for-loop

    	    if( DEBUG )
    	      std::cout << "CTF_MSE_enhancer: ind=" << ind << std::endl;


    	    // set samples that do not belong to CIR to zero

    	    float const norm_const = 1. / static_cast< float >( d_vlen );

    	    if( ( ind + d_cir_len ) < d_vlen )
    	    {
    	      if( ind > 0 )
    	        std::fill( buf2, buf2 + ind, gr_complex( 0.0, 0.0 ) );

    	      std::fill( buf2 + ind + d_cir_len, buf2 + d_vlen,
    	        gr_complex( 0.0, 0.0 ) );

    	      for( int j = 0; j < d_cir_len; ++j )
    	        buf2[ ind + j ] *= norm_const;
    	    }
    	    else if( ( ind + d_cir_len ) == d_vlen )
    	    {
    	      std::fill( buf2, buf2 + ind, gr_complex( 0.0, 0.0 ) );

    	      for( int j = 0; j < d_cir_len; ++j )
    	        buf2[ ind + j ] *= norm_const;
    	    }
    	    else
    	    {
    	      short const ind2 = ( ind + d_cir_len ) - d_vlen;
    	      std::fill( buf2 + ind2, buf2 + ind, gr_complex( 0.0, 0.0 ) );

    	      for( int j = 0; j < ind2; ++j )
    	        buf2[ j ] *= norm_const;
    	      for( int j = ind; j < d_vlen; ++j )
    	        buf2[ j ] *= norm_const;

    	    }


    	    //some fix by pranav
    	    std::copy( buf2, buf2 + d_vlen, d_fwdfft->get_inbuf() );

    	    // CIR -> CTF
    	    d_fwdfft->execute();

    	    //2nd fix
    	    std::copy( d_fwdfft->get_outbuf(), d_fwdfft->get_outbuf() + d_vlen, buf1 );
    	    std::copy( buf1, buf1 + d_vlen, out );

    	  } // for-loop over noutput_items

    	  if( DEBUG )
    	    std::cout << "MSE: leave, nout=" << noutput_items << std::endl;

    	  return noutput_items;
    }

  } /* namespace ofdm */
} /* namespace gr */

