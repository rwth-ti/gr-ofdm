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
#include "autocorrelator_stage1_impl.h"
#include <iostream>

namespace gr {
  namespace ofdm {

    autocorrelator_stage1::sptr
    autocorrelator_stage1::make(int lag)
    {
      return gnuradio::get_initial_sptr
        (new autocorrelator_stage1_impl(lag));
    }

    /*
     * The private constructor
     */
    autocorrelator_stage1_impl::autocorrelator_stage1_impl(int lag)
      : gr::sync_block("autocorrelator_stage1",
              gr::io_signature::make(1, 1, sizeof( gr_complex )),
              gr::io_signature::make2(2, 2, sizeof( gr_complex ), sizeof( float )))
    , d_lag( lag )
     , d_delay( lag )
    {
    	  set_history( d_delay + 1 );
    	  set_output_multiple( 4 ); // due to vectorization
    }

    /*
     * Our virtual destructor.
     */
    autocorrelator_stage1_impl::~autocorrelator_stage1_impl()
    {
    }

    typedef float v4sf __attribute__ ((vector_size (16)));

    typedef union
    {
      v4sf vec;
      unsigned int v[4];
    }
    v4sf_i __attribute__((aligned(16)));

    int
    autocorrelator_stage1_impl::work(int noutput_items,
			  gr_vector_const_void_star &input_items,
			  gr_vector_void_star &output_items)
    {
    	v4sf const * __restrict in_del =
    	    static_cast< v4sf const * >( input_items[0] );
    	  v4sf const * __restrict in = in_del + d_delay / 2;

    	  v4sf * __restrict p = static_cast< v4sf * >( output_items[0] );
    	  v4sf * __restrict r = static_cast< v4sf * >( output_items[1] );

    	  // use this constant to flip the sign bit of the imaginary part
    	  // with a simple XOR instruction
    	  v4sf_i _xsign = { { 0 } };
    	  _xsign.v[1] = 0x80000000;
    	  _xsign.v[3] = 0x80000000;
    	  v4sf const xsign = _xsign.vec;

    	  unsigned int const nout = noutput_items;

    	  // complex multiplication
    	  // p[i] = std::conj( in_del[i] ) * in[i]
    	  // squared magnitude:
    	  // r[i] = in[i].real()**2 + in[i].imag()**2

    	  // processing 4 complex values per iteration

    	  for( unsigned int i = 0;
    	       i < nout;
    	       i+=4, in+=2, in_del+=2, p+=2, ++r )
    	  {
    	    v4sf const in0 = *in;
    	    v4sf const in1 = *(in+1);
    	    v4sf const in_del0 = *in_del;
    	    v4sf const in_del1 = *(in_del+1);

    	    v4sf x0 = __builtin_ia32_movsldup( in0 );
    	    v4sf x1 = __builtin_ia32_xorps( in_del0, xsign ); // conjugate
    	    x0 *=  x1;

    	    x1 = __builtin_ia32_shufps( x1, x1, 0xB1 );
    	    v4sf x2 = __builtin_ia32_movshdup( in0 );
    	    x2 *= x1;

    	    x0 = __builtin_ia32_addsubps( x0, x2 );
    	    p[0] = x0;


    	    x0 = __builtin_ia32_movsldup( in1 );
    	    x1 = __builtin_ia32_xorps( in_del1, xsign ); // conjugate
    	    x0 *= x1;

    	    x1 = __builtin_ia32_shufps( x1, x1, 0xB1 );
    	    x2 = __builtin_ia32_movshdup( in1 );
    	    x2 *= x1;

    	    x0 = __builtin_ia32_addsubps( x0, x2 );
    	    p[1] = x0;

    	    v4sf const x14 = in0 * in0;
    	    v4sf const x15 = in1 * in1;
    	    r[0] = __builtin_ia32_haddps( x14, x15 );

    	//    movsldup xmm0, [eax]    ; multiplier real (a1, a1, a0, a0)
    	//    movaps xmm1, [ebx]      ; multiplicand (d1, c1, d0, c0)
    	//    mulps xmm0, xmm1        ; temp1 (a1d1, a1c1, a0d0, a0c0)
    	//    shufps xmm1, xmm1, 0xB1 ; shuf multiplicand(c1, d1, c0, d0)
    	//    movshdup xmm2, [eax]    ; multiplier imag (b1, b1, b0, b0)
    	//    mulps xmm2, xmm1        ; temp2 (b1c1, b1d1, b0c0, b0d0)
    	//    addsubps xmm0, xmm2     ; b1c1+a1d1, a1c1-b1d1, a0d0+b0c0, a0c0-b0d0
    	//    movaps [edx], xmm0      ; store the results (y1,x1,y0,x0)


    	  } // for-loop

        // Tell runtime system how many output items we produced.
        return noutput_items;
    }

  } /* namespace ofdm */
} /* namespace gr */

