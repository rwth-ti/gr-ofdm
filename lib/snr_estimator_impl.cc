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
#include "snr_estimator_impl.h"

#include <string.h>
#include <iostream>

#define DEBUG 0

namespace gr {
  namespace ofdm {

    snr_estimator::sptr
    snr_estimator::make(int vlen, int skip)
    {
      return gnuradio::get_initial_sptr
        (new snr_estimator_impl(vlen, skip));
    }

    /*
     * The private constructor
     */
    snr_estimator_impl::snr_estimator_impl(int vlen, int skip)
      : gr::sync_block("snr_estimator",
              gr::io_signature::make(1, 1, sizeof(gr_complex) * vlen),
              gr::io_signature::make(2, 2, sizeof( float )))
    	, d_vlen( vlen )
    	, d_skip( skip )
    {
    	  assert( d_vlen > 0 );
    }

    /*
     * Our virtual destructor.
     */
    snr_estimator_impl::~snr_estimator_impl()
    {
    }

    int
    snr_estimator_impl::work(int noutput_items,
			  gr_vector_const_void_star &input_items,
			  gr_vector_void_star &output_items)
    {
    	  const gr_complex *in = static_cast< const gr_complex* >( input_items[0] );
    	  float *out = static_cast< float* >( output_items[0] );
    	  float *out1 = static_cast< float* >( output_items[1] );


    	  for( int j = 0; j < noutput_items; ++j)
    	  {

    		float sum_load=0;
    		float sum_null=0;
    		float estim = 0.0;
    		float estim_noise = 0.0;
    		float square = 0.0;

    	    for( int i = 0; i < d_vlen ; ++i )
    	    {
    	    	//square = std::abs(in[i]*std::conj(in[i]));
    	    	square = in[i].real()*in[i].real() + in[i].imag()*in[i].imag();

    	    	if ( i % d_skip == 0 )
    	    	{
    	    	   sum_load+=square;
    	    	}
    	    	else
    	    	{
    	           sum_null+=square;
    	    	}

    		}

    	    estim =(1./d_skip)*((d_skip-1)*sum_load/sum_null-1);
    	    estim_noise = sum_null*d_skip/(d_skip-1)/d_vlen;
    	    out[j] = static_cast<float>(estim);
    	    out1[j] = static_cast<float>(estim_noise);

    	  }
    	  return noutput_items;
    }

  } /* namespace ofdm */
} /* namespace gr */

