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
#include "gate_ff_impl.h"

#include <cstdlib>

namespace gr {
  namespace ofdm {

    gate_ff::sptr
    gate_ff::make()
    {
      return gnuradio::get_initial_sptr
        (new gate_ff_impl());
    }

    /*
     * The private constructor
     */
    gate_ff_impl::gate_ff_impl()
      : gr::sync_block("gate_ff",
              gr::io_signature::make2(1, -1, sizeof(char), sizeof(float)),
              gr::io_signature::make2(1, -1, sizeof(char), sizeof(float)))
    {}

    /*
     * Our virtual destructor.
     */
    gate_ff_impl::~gate_ff_impl()
    {
    }

    int
    gate_ff_impl::work(int noutput_items,
			  gr_vector_const_void_star &input_items,
			  gr_vector_void_star &output_items)
    {
    	const char *in = static_cast<const char*>(input_items[0]);

    		assert(input_items.size() == output_items.size());

    		int j = 0;
    		for(int i = 0; i < noutput_items; ++i) {
    			if(in[i] == 1) {
    				(static_cast<char*>(output_items[0]))[j] = in[i];
    				for(std::size_t s = 1; s < output_items.size(); ++s) {
    					(static_cast<float*>(output_items[s]))[j] = (static_cast<const float*>(input_items[s]))[i];
    				}
    				++j;
    			}
    		}

    		consume_each(noutput_items - j);
    		return j;
    }

  } /* namespace ofdm */
} /* namespace gr */

