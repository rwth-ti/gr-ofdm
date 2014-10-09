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
#include "vector_padding_dc_null_impl.h"

#include <gnuradio/math.h>
#include <string.h>

#include <vector>
#include <iostream>

#define DEBUG(x)

namespace gr {
  namespace ofdm {

    vector_padding_dc_null::sptr
    vector_padding_dc_null::make(int carriers, int vlen, int dc_zeros, int padding_left)
    {
      return gnuradio::get_initial_sptr
        (new vector_padding_dc_null_impl(carriers, vlen, dc_zeros, padding_left));
    }

    /*
     * The private constructor
     */
    vector_padding_dc_null_impl::vector_padding_dc_null_impl(int carriers, int vlen, int dc_zeros, int padding_left)
      : gr::sync_block("vector_padding_dc_null",
              gr::io_signature::make(1, 1, sizeof(gr_complex) * carriers),
              gr::io_signature::make(1, 1, sizeof(gr_complex) * vlen))
	, d_carriers(carriers)
	, d_vlen(vlen)
    , d_dc_zeros(dc_zeros)
	, d_padding_left(padding_left)
    {
    	if(d_padding_left < 0) {
    		d_padding_left = static_cast<int>(ceil((d_vlen - d_carriers) / 2.0)-(d_dc_zeros/2.0));
    	}
    	assert(vlen >= d_padding_left + carriers);
    }

    /*
     * Our virtual destructor.
     */
    vector_padding_dc_null_impl::~vector_padding_dc_null_impl()
    {
    }

    int
    vector_padding_dc_null_impl::work(int noutput_items,
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

		for(i += d_carriers/2; i < d_vlen/2 + d_dc_zeros/2; ++i) {
				out[i] = complex_zero;
			}

		for(i+= d_carriers/2; i < d_vlen; ++i) {
			out[i] = complex_zero;
		}

		gr_complex *shifted_out1 = out + d_padding_left;
		memcpy(shifted_out1 , in, (d_carriers/2) * sizeof(gr_complex));
		shifted_out1 += d_vlen;
		in+= d_carriers/2;

		gr_complex *shifted_out2 = out + d_vlen/2 + d_dc_zeros/2;
		memcpy(shifted_out2 , in, (d_carriers/2) * sizeof(gr_complex));
		shifted_out2 += d_vlen;
		in+= d_carriers/2;

		/* copy that shape to every ofdm symbol */
		for(i = 1; i < noutput_items; ++i, shifted_out1 += d_vlen, shifted_out2 += d_vlen,in+= d_carriers) {
			memcpy(out + i*d_vlen, out, d_vlen * sizeof(gr_complex));
			memcpy(shifted_out1 , in, (d_carriers/2) * sizeof(gr_complex));
			memcpy(shifted_out2 , in+ d_carriers/2, (d_carriers/2) * sizeof(gr_complex));
		}

        return noutput_items;
    }

  } /* namespace ofdm */
} /* namespace gr */

