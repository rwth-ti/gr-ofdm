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
#include "sinr_estimator_impl.h"

#include <string.h>
#include <iostream>

#define DEBUG 0

namespace gr {
  namespace ofdm {

    sinr_estimator::sptr
    sinr_estimator::make(int vlen, int skip, int dc_null)
    {
      return gnuradio::get_initial_sptr
        (new sinr_estimator_impl(vlen, skip, dc_null));
    }

    /*
     * The private constructor
     */
    sinr_estimator_impl::sinr_estimator_impl(int vlen, int skip, int dc_null)
      : gr::sync_block("sinr_estimator",
              gr::io_signature::make(2, 2, sizeof(gr_complex) * vlen),
              gr::io_signature::make(1, 1, sizeof( float )*vlen*(skip-1)/ skip))
    	, d_vlen( vlen )
    	, d_skip( skip )
        , d_dc_null (dc_null)
    {
    	  assert( d_vlen > 0 );
    	  d_taps.reset(new float[vlen]);
    	  d_taps1.reset(new float[vlen]);
    	   for(int i = 0; i < vlen; ++i){
    	     d_taps[i] = 1.0;
    	     d_taps1[i] = 1.0;
    	   }

    }

    /*
     * Our virtual destructor.
     */
    sinr_estimator_impl::~sinr_estimator_impl()
    {
    }

    int
    sinr_estimator_impl::work(int noutput_items,
			  gr_vector_const_void_star &input_items,
			  gr_vector_void_star &output_items)
    {
    	  const gr_complex *in = static_cast< const gr_complex* >( input_items[0] );
    	  const gr_complex *in1 = static_cast< const gr_complex* >( input_items[1] );
    	  float *out = static_cast< float* >( output_items[0] );


    	  for( int j = 0; j < noutput_items; ++j)
    	  {

    		//float null_0=0;
    		//float null_1=0;
    		float estim = 0.0;
    		//float square = 0.0;

    	    for( int i = 0; i < d_vlen ; ++i )
    	    {
                if (i< (d_vlen)/2)
                {
                    if ( i % d_skip != 4 + d_dc_null/2 )
                    {
                            d_taps[i] = 0.01*(in[i].real()*in[i].real() + in[i].imag()*in[i].imag()) + 0.99*d_taps[i];
                            d_taps1[i] = 0.01*(in1[i].real()*in1[i].real() + in1[i].imag()*in1[i].imag()) + 0.99*d_taps1[i];
                            estim = d_taps1[i]/d_taps[i] - 1;

                            *out = (estim);
                            out += 1;

                    }
                }
                else
                {
                    if ( i % d_skip != 4 - d_dc_null/2 )
                    {
                            d_taps[i] = 0.01*(in[i].real()*in[i].real() + in[i].imag()*in[i].imag()) + 0.99*d_taps[i];
                            d_taps1[i] = 0.01*(in1[i].real()*in1[i].real() + in1[i].imag()*in1[i].imag()) + 0.99*d_taps1[i];
                            estim = d_taps1[i]/d_taps[i] - 1;

                            *out = (estim);
                            out += 1;

                    }
                }
            }

    	  }

    	  return noutput_items;
    }

  } /* namespace ofdm */
} /* namespace gr */

