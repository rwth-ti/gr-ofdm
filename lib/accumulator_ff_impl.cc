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
#include "accumulator_ff_impl.h"

namespace gr {
  namespace ofdm {

    accumulator_ff::sptr
    accumulator_ff::make()
    {
      return gnuradio::get_initial_sptr
        (new accumulator_ff_impl());
    }

    /*
     * The private constructor
     */
    accumulator_ff_impl::accumulator_ff_impl()
      : gr::sync_block("accumulator_ff",
              gr::io_signature::make(1, 1, sizeof(float)),
              gr::io_signature::make(1, 1, sizeof(float)))
    ,d_accum( 0.0 )
    {}

    /*
     * Our virtual destructor.
     */
    accumulator_ff_impl::~accumulator_ff_impl()
    {
    }

    int
    accumulator_ff_impl::work(int noutput_items,
			  gr_vector_const_void_star &input_items,
			  gr_vector_void_star &output_items)
    {
    	const float *in = static_cast<const float*>(input_items[0]);
    	float *out = static_cast<float*>(output_items[0]);

    	float acc = d_accum;

	  	for(int i = 0; i < noutput_items; ++i){
		acc += in[i];
		out[i] = acc;
	}
	  	d_accum = acc;
        // Tell runtime system how many output items we produced.
        return noutput_items;
    }

  } /* namespace ofdm */
} /* namespace gr */

