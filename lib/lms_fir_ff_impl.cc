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
#include "lms_fir_ff_impl.h"

namespace gr {
  namespace ofdm {

    lms_fir_ff::sptr
    lms_fir_ff::make(int len, float mu)
    {
      return gnuradio::get_initial_sptr
        (new lms_fir_ff_impl(len, mu));
    }

    /*
     * The private constructor
     */
    lms_fir_ff_impl::lms_fir_ff_impl(int len, float mu)
      : gr::sync_block("lms_fir_ff",
              gr::io_signature::make(1, 1, sizeof(float)),
              gr::io_signature::make(1, 1, sizeof(float)))
    	, d_len(len)
    	, d_mu(mu)
    {
    	  set_history(len);

    	  d_taps.reset(new float[len]);
    	  for(int i = 0; i < len; ++i){
    	    d_taps[i] = 1.0/len;
    	  }
    }

    /*
     * Our virtual destructor.
     */
    lms_fir_ff_impl::~lms_fir_ff_impl()
    {
    }

    int
    lms_fir_ff_impl::work(int noutput_items,
			  gr_vector_const_void_star &input_items,
			  gr_vector_void_star &output_items)
    {
    	  const float *in = static_cast<const float*>(input_items[0]);
    	  float *out = static_cast<float*>(output_items[0]);

    	  for(int i = 0; i < noutput_items; ++i){
    	    // FIR filter
    	    float x = d_taps[0] * in[i];
    	    for(int j = 1; j < d_len; ++j){
    	      x += d_taps[j] * in[i+j];
    	    }
    	    out[i] = x;

    	    // adaptive fir part
    	    float e = d_mu*(in[i] - x);
    	    for(int j = 0; j < d_len; ++j){
    	      d_taps[j] += e*in[i+j];
    	    }
    	  }

    	  return noutput_items;
    }

  } /* namespace ofdm */
} /* namespace gr */

