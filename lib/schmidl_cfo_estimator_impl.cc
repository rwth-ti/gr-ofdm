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
#include "schmidl_cfo_estimator_impl.h"

#include <gnuradio/math.h>

#include <iostream>
#include <algorithm>
#include <string.h>

namespace gr {
  namespace ofdm {

    schmidl_cfo_estimator::sptr
    schmidl_cfo_estimator::make(const int fft_length, const int carriers, const int estimation_range, const std::vector<gr_complex> &differential_pn_seq)
    {
      return gnuradio::get_initial_sptr
        (new schmidl_cfo_estimator_impl(fft_length, carriers, estimation_range, differential_pn_seq));
    }

    /*
     * The private constructor
     */
    schmidl_cfo_estimator_impl::schmidl_cfo_estimator_impl(const int fft_length, const int carriers, const int estimation_range, const std::vector<gr_complex> &differential_pn_seq)
      : gr::sync_block("schmidl_cfo_estimator",
              gr::io_signature::make(2, 2, sizeof(gr_complex) * fft_length),
              gr::io_signature::make(1, 1, sizeof(float) * (estimation_range*2+1)))
    	, d_differential_pn_seq(differential_pn_seq), d_fft_length(fft_length), d_carriers(carriers)
    	, d_left_padding(static_cast<int>(ceil((d_fft_length - d_carriers) / 2.0)))
    	, d_estimation_range(estimation_range)
    {
    	  //assert(d_estimation_range <= d_left_padding);
    }

    /*
     * Our virtual destructor.
     */
    schmidl_cfo_estimator_impl::~schmidl_cfo_estimator_impl()
    {
    }

    int
    schmidl_cfo_estimator_impl::work(int noutput_items,
			  gr_vector_const_void_star &input_items,
			  gr_vector_void_star &output_items)
    {
    	const gr_complex *c_1 = static_cast<const gr_complex*>(input_items[0]);
    	  const gr_complex *c_2 = static_cast<const gr_complex*>(input_items[1]);
    	  float *metric = static_cast<float*>(output_items[0]);

    	  assert(noutput_items > 0);

    	  const int metric_vlen = d_estimation_range*2+1;
    	  memset(metric, 0, sizeof(float) * metric_vlen * noutput_items);
    	  metric += d_estimation_range;

    	  // input stream 1 holds the preamble 1 in freq. domain, stream 2 holds preamble 2.
    	  // we calculate a metric that will show up a maximum at the correct frequency
    	  // shift index.
    	  for(int symbols = 0; symbols < noutput_items; ++symbols,
    	      metric += metric_vlen, c_1 += d_fft_length, c_2 += d_fft_length) {

    	    // norm factor: 2 * sum(norm(x_2) ^ 2
    	    float denom = 0.0;
    	    for(int i = d_left_padding; i < d_carriers + d_left_padding; i += 2) {
    	      denom += std::norm(c_2[i]);
    	    }
    	    denom = 2 * denom*denom;

    	    #define CYCLIC(x) (x+d_fft_length)%d_fft_length

    	    // rotate vectors cyclically
    	    for(int freq_shift = 0; freq_shift <= d_estimation_range; freq_shift+=2) {
    	      // shift by freq_shift
    	      // nominator = norm(sum(conj(x_1) * x_2 * diff_seq))
    	      gr_complex acc(0.0,0.0);
    	      for(int i = d_left_padding+freq_shift, j = 0; j < d_carriers; i+=2, j+=2) {
    	        acc += conj(c_1[CYCLIC(i)])*c_2[CYCLIC(i)]*d_differential_pn_seq[j];
    	      }
    	      metric[freq_shift] = std::norm(acc) / denom;

    	      if(freq_shift > 0) {
    	        // shift by -freq_shift
    	        gr_complex acc(0.0,0.0);
    	        for(int i = d_left_padding-freq_shift, j = 0; j < d_carriers; i+=2, j+=2) {
    	          acc += conj(c_1[CYCLIC(i)])*c_2[CYCLIC(i)]*d_differential_pn_seq[j];
    	        }
    	        metric[-freq_shift] = std::norm(acc) / denom;
    	      }
    	    }
    	  }
    	  return noutput_items;
    }
	#undef CYCLIC

  } /* namespace ofdm */
} /* namespace gr */

