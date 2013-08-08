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
#include "sinr_estimator_02_impl.h"

#include <string.h>
#include <iostream>

#define DEBUG 0

namespace gr {
  namespace ofdm {

    sinr_estimator_02::sptr
    sinr_estimator_02::make(int vlen, int skip)
    {
      return gnuradio::get_initial_sptr
        (new sinr_estimator_02_impl(vlen, skip));
    }

    /*
     * The private constructor
     */
    sinr_estimator_02_impl::sinr_estimator_02_impl(int vlen, int skip)
      : gr::sync_block("sinr_estimator_02",
              gr::io_signature::make(2, 2, sizeof(gr_complex) * vlen),
              gr::io_signature::make2(2, 2,
            	        sizeof( float )* vlen, sizeof( float )))
    	, d_vlen( vlen )
    	, d_skip( skip )
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
    sinr_estimator_02_impl::~sinr_estimator_02_impl()
    {
    }

    int
    sinr_estimator_02_impl::work(int noutput_items,
			  gr_vector_const_void_star &input_items,
			  gr_vector_void_star &output_items)
    {
    	  const gr_complex *in = static_cast< const gr_complex* >( input_items[0] );
    	  const gr_complex *in1 = static_cast< const gr_complex* >( input_items[1] );
    	  float *out = static_cast< float* >( output_items[0] );
    	  float *out1 = static_cast< float* >( output_items[1] );


    	  for( int j = 0; j < noutput_items; ++j)
    	  {

    		//float null_0=0;
    		//float null_1=0;
    		float estim = 0.0;
    		float estim_av_snr = 0.0;
    		//float square = 0.0;

    	    for( int i = 0; i < d_vlen ; ++i )
    	    {


    	    	if ( i % d_skip != 0 )
    	    	{
    	    		/*null_0 = in[i].real()*in[i].real() + in[i].imag()*in[i].imag();
    	    		null_1 = in1[i].real()*in1[i].real() + in1[i].imag()*in1[i].imag();
    	    		estim = null_1/null_0 - 1;
    	    		*out = static_cast<float>(estim);
    	    		out += 1;*/

    	    		d_taps[i] = 0.01*(in[i].real()*in[i].real() + in[i].imag()*in[i].imag()) + 0.99*d_taps[i];
    	    		d_taps1[i] = 0.01*(in1[i].real()*in1[i].real() + in1[i].imag()*in1[i].imag()) + 0.99*d_taps1[i];
    	    		estim = d_taps1[i]/d_taps[i] - 1;

    	    		if ( i % d_skip == 1  )
    	    		        {
    	    		        	if (i == 1)
    	    		        	{
    	    		        		*out = (estim);
    	    		        		*(out+1) = (estim);
    	    		        		out += 2;
    	    		        		estim_av_snr += 2*estim;
    	    		        	}
    	    		        	else
    	    		        	{
    	    		        		*out = ((estim + *(out-1))/2.0);
    	    		        		*(out+1) = (estim);
    	    		        		out += 2;
    	    		        		estim_av_snr += 2*estim;
    	    		        	}

    	    		        }
    	    		else
    	    		{
    	    		*out = (estim);
    	    		out += 1;
    	    		estim_av_snr += estim;
    	    		}
    	    	}
    		}

    	    /*estim =(1./d_skip)*((d_skip-1)*sum_load/sum_null-1);
    	    estim_noise = sum_null/d_skip*(d_skip-1);
    	    out[j] = static_cast<float>(estim);
    	    out1[j] = static_cast<float>(estim_noise);*/

    	    out1[j] = static_cast<float>(estim_av_snr/d_vlen);

    	  }
    	  return noutput_items;
    }

  } /* namespace ofdm */
} /* namespace gr */

