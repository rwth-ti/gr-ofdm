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
#include "fbmc_postprocess_CTF_estimate_impl.h"

#include <iostream>

#define DEBUG 0

namespace gr {
  namespace ofdm {

    fbmc_postprocess_CTF_estimate::sptr
    fbmc_postprocess_CTF_estimate::make(int vlen)
    {
      return gnuradio::get_initial_sptr
        (new fbmc_postprocess_CTF_estimate_impl(vlen));
    }

    /*
     * The private constructor
     */
    fbmc_postprocess_CTF_estimate_impl::fbmc_postprocess_CTF_estimate_impl(int vlen)
      : gr::sync_block("fbmc_postprocess_CTF_estimate",
              gr::io_signature::make(1, 1, sizeof( gr_complex ) * vlen),
              gr::io_signature::make(1, 1,
            	        sizeof( float ) * vlen))
    	, d_vlen( vlen )
    {
    	  assert( ( vlen % 2 ) == 0 ); // alignment requirement
    }

    /*
     * Our virtual destructor.
     */
    fbmc_postprocess_CTF_estimate_impl::~fbmc_postprocess_CTF_estimate_impl()
    {
    }

    int
    fbmc_postprocess_CTF_estimate_impl::work(int noutput_items,
			  gr_vector_const_void_star &input_items,
			  gr_vector_void_star &output_items)
    {
    	  gr_complex const * in = static_cast< gr_complex const * >( input_items[0] );
    	  //float * snr_est = static_cast< float * >( output_items[0] );
    	  float * disp_ctf = static_cast< float * >( output_items[0] );


    	  for( int i = 0; i < noutput_items;
    	       ++i, in += d_vlen, disp_ctf += d_vlen )
    	  {
    	    float acc = 0.0;
    	    gr_complex const one( 1.0, 0.0 );

    	    float sum_real = 0;
    	    float sum_imag = 0;
    	    float estim = 0.0;
    	    float square_real = 0.0;
    	    float square_imag = 0.0;

    	    // TODO: good candidate for vectorization
    	    for( int j = 0; j < d_vlen; ++j )
    	    {

    	      gr_complex const val = in[j];

    	      float const & __x = val.real();
    	      float const & __y = val.imag();

    	      square_real = __x*__x;
    	      square_imag = __y*__y;

    	      sum_real+=square_real;
    	      sum_imag+=square_imag;


    	      float const t = square_real + square_imag;

    	      disp_ctf[j] = t;
    	      acc += t;

    	      // best example for strength reduction: 2x speedup
//inv_ctf[j] = std::conj( in[j] ) / t;
    	//      inv_ctf[j] = one / in[j]; // = conj(in[j])/|in[j]|^2
    	//                                // |in[j]|^2 = t
    	    }

    	    //estim =(2.128/2.37)*(sum_real/sum_imag-1);
    	    //snr_est[i] = static_cast<float>(estim);

    	    float const f = static_cast< float >( d_vlen ) / acc;
    	    for( int j = 0; j < d_vlen; ++j )
    	    {
    	      disp_ctf[j] *= f;
    	    }

    	  } // for-loop over input

    	  if( DEBUG )
    	    std::cout << "POST: leave, nout=" << noutput_items << std::endl;


    	  return noutput_items;
    }

  } /* namespace ofdm */
} /* namespace gr */

