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
#include "mm_frequency_estimator_impl.h"


#include <cmath>
#include <iostream>

#define DEBUG_ESTIMATOR 1

static const double two_pi = 6.2831853071795862;

namespace gr {
  namespace ofdm {

    mm_frequency_estimator::sptr
    mm_frequency_estimator::make(int vlen, int identical_parts)
    {
      return gnuradio::get_initial_sptr
        (new mm_frequency_estimator_impl(vlen, identical_parts));
    }

    /*
     * The private constructor
     */
    mm_frequency_estimator_impl::mm_frequency_estimator_impl(int vlen, int identical_parts)
      : gr::sync_block("mm_frequency_estimator",
              gr::io_signature::make(1, 1, sizeof(gr_complex)*vlen),
              gr::io_signature::make(1, 1, sizeof(float)))
    	, d_vlen(vlen)
    	, d_L(identical_parts)
    	, d_M(vlen/identical_parts)
    	, d_weights(identical_parts/2, 0.0)
    {
    	assert(d_M*d_L == vlen);

    	  float L = identical_parts;
    	  float H = L/2;

    	  for(int m = 1; m <= L/2; ++m){
    	    float mf = (float)m;
    	    float w = 3 * ((L-mf)*(L-mf+1)-H*(L-H))/(H*(4*(H*H)-6*L*H+3*(L*L)-1));
    	    d_weights[m-1] = w;


    	    if(DEBUG_ESTIMATOR)
    	      std::cout << "[mm] " << m << ":" << w << std::endl;
    	  }
    }

    /*
     * Our virtual destructor.
     */
    mm_frequency_estimator_impl::~mm_frequency_estimator_impl()
    {
    }

    int
    mm_frequency_estimator_impl::work(int noutput_items,
			  gr_vector_const_void_star &input_items,
			  gr_vector_void_star &output_items)
    {
    	const gr_complex *in = static_cast<const gr_complex*>(input_items[0]);
    	  float *out = static_cast<float*>(output_items[0]);

    	  int H = d_L/2;

    	  std::vector<gr_complexd> R(H+1, gr_complexd(1.0,0.0));
    	  for(int i = 0; i < noutput_items; ++i, in += d_vlen){

    	    // compute correlations between identical parts
    	    for(int m = 1; m <= H; ++m){

    	      gr_complexd acc(0.0,0.0);
    	      const int shift = m*d_M;

    	      for(int k = shift; k < d_vlen; ++k){
    	        acc += in[k]*std::conj(in[k-shift]);
    	      }

    	      R[m] = acc;
    	    }

    	    // estimate the frequency offset
    	    double est = 0.0;
    	    for(int m = 1; m <= H; ++m){
    	      gr_complexd t = R[m] * std::conj(R[m-1]);
    	      double phase_diff = std::atan2(t.imag(),t.real());
    	      est += d_weights[m-1] * phase_diff; // (argR[m] - argR[m-1]);
    	    }

    	    est = d_L / two_pi * est;

    	    out[i] = static_cast<float>(est);

    	  }

    	  return noutput_items;
    }

  } /* namespace ofdm */
} /* namespace gr */

