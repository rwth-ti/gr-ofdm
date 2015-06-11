/* -*- c++ -*- */
/* 
 * Copyright 2014 <+YOU OR YOUR COMPANY+>.
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
#include "fbmc_asymmetrical_vector_padding_vcvc_impl.h"

 #include <gnuradio/math.h>

#include <string.h>


#include <vector>
#include <iostream>

#define DEBUG(x)

namespace gr {
  namespace ofdm {

	fbmc_asymmetrical_vector_padding_vcvc::sptr
	fbmc_asymmetrical_vector_padding_vcvc::make(int start, int end, int vlen, int padding_left)
	{
	  return gnuradio::get_initial_sptr
		(new fbmc_asymmetrical_vector_padding_vcvc_impl(start, end, vlen, padding_left));
	}

	/*
	 * The private constructor
	 */
	fbmc_asymmetrical_vector_padding_vcvc_impl::fbmc_asymmetrical_vector_padding_vcvc_impl(int start, int end, int vlen, int padding_left)
	  : gr::sync_block("fbmc_asymmetrical_vector_padding_vcvc",
			  gr::io_signature::make(1, 1, sizeof(gr_complex)*(end-start+1)),
			  gr::io_signature::make(1, 1, sizeof(gr_complex)* vlen)),
	  d_start(start),
	  d_end(end),
	  d_vlen(vlen),
	  d_padding_left(padding_left),
	  d_padding_right(0),
	  d_carriers(end-start+1)
	{
		if(d_padding_left < 0) {
    		d_padding_left = d_start; // we can use the start index b/c indices start from 0.
    		d_padding_right = d_vlen-(d_end+1);
    	}
    	assert(d_end >= d_start);
    	assert(vlen >= d_end);
	}

	/*
	 * Our virtual destructor.
	 */
	fbmc_asymmetrical_vector_padding_vcvc_impl::~fbmc_asymmetrical_vector_padding_vcvc_impl()
	{
	}

	int
	fbmc_asymmetrical_vector_padding_vcvc_impl::work(int noutput_items,
			  gr_vector_const_void_star &input_items,
			  gr_vector_void_star &output_items)
	{
		DEBUG(std::cout << "padding input: " <<  noutput_items << std::endl;)

		const gr_complex *in = static_cast<const gr_complex*>(input_items[0]);
		gr_complex *out = static_cast<gr_complex*>(output_items[0]);

		/* fill unused carriers in first ofdm symbol */
		gr_complex complex_zero(0,0);
		int i;
		for(i = 0; i < d_padding_left; ++i) {
			out[i] = complex_zero;
		}
		for(i= d_end; i < d_vlen; ++i) {
			out[i] = complex_zero;
		}

		gr_complex *shifted_out = out + d_padding_left;
		memcpy(shifted_out , in, d_carriers * sizeof(gr_complex));
		shifted_out += d_vlen;
		in+= d_carriers;

		/* copy that shape to every ofdm symbol */
		for(i = 1; i < noutput_items; ++i, shifted_out += d_vlen, in+= d_carriers) {
			memcpy(out + i*d_vlen, out, d_vlen * sizeof(gr_complex));
			memcpy(shifted_out , in, d_carriers * sizeof(gr_complex));
		}

		return noutput_items;
	}

  } /* namespace ofdm */
} /* namespace gr */

