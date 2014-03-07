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
#include "postprocess_CTF_estimate_impl.h"

#include <iostream>

#define DEBUG 0

namespace gr {
  namespace ofdm {

    postprocess_CTF_estimate::sptr
    postprocess_CTF_estimate::make(int vlen)
    {
      return gnuradio::get_initial_sptr
        (new postprocess_CTF_estimate_impl(vlen));
    }

    /*
     * The private constructor
     */
    postprocess_CTF_estimate_impl::postprocess_CTF_estimate_impl(int vlen)
      : gr::sync_block("postprocess_CTF_estimate",
              gr::io_signature::make(1, 1, sizeof( gr_complex ) * vlen),
              gr::io_signature::make2(2, 2,
            	        sizeof( gr_complex ) * vlen,
            	        sizeof( float ) * vlen))
    	, d_vlen( vlen )
    {
    	  assert( ( vlen % 2 ) == 0 ); // alignment requirement
    }

    /*
     * Our virtual destructor.
     */
    postprocess_CTF_estimate_impl::~postprocess_CTF_estimate_impl()
    {
    }

    int
    postprocess_CTF_estimate_impl::work(int noutput_items,
			  gr_vector_const_void_star &input_items,
			  gr_vector_void_star &output_items)
    {
    	  gr_complex const * in = static_cast< gr_complex const * >( input_items[0] );
    	  gr_complex * inv_ctf = static_cast< gr_complex * >( output_items[0] );
    	  float * disp_ctf = static_cast< float * >( output_items[1] );


    	  for( int i = 0; i < noutput_items;
    	       ++i, in += d_vlen, inv_ctf += d_vlen, disp_ctf += d_vlen )
    	  {
    	    float acc = 0.0;
    	    gr_complex const one( 1.0, 0.0 );

    	    // TODO: good candidate for vectorization
    	    for( int j = 0; j < d_vlen; ++j )
    	    {
    	      gr_complex const val = in[j];

    	      float const & __x = val.real();
    	      float const & __y = val.imag();

    	      float const t = __x*__x + __y*__y;

    	      disp_ctf[j] = t;
    	      acc += t;

    	      // best example for strength reduction: 2x speedup
    	      inv_ctf[j] = std::conj( in[j] ) / t;
    	//      inv_ctf[j] = one / in[j]; // = conj(in[j])/|in[j]|^2
    	//                                // |in[j]|^2 = t
    	    }

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

