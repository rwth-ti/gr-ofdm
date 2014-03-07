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
#include "vector_sum_vcc_impl.h"

namespace gr {
  namespace ofdm {

    vector_sum_vcc::sptr
    vector_sum_vcc::make(int vlen)
    {
      return gnuradio::get_initial_sptr
        (new vector_sum_vcc_impl(vlen));
    }

    /*
     * The private constructor
     */
    vector_sum_vcc_impl::vector_sum_vcc_impl(int vlen)
      : gr::sync_block("vector_sum_vcc",
              gr::io_signature::make(1, 1, sizeof(gr_complex)*vlen),
              gr::io_signature::make(1, 1, sizeof(gr_complex)))
    	, d_vlen(vlen)
    {}

    /*
     * Our virtual destructor.
     */
    vector_sum_vcc_impl::~vector_sum_vcc_impl()
    {
    }

    int
    vector_sum_vcc_impl::work(int noutput_items,
			  gr_vector_const_void_star &input_items,
			  gr_vector_void_star &output_items)
    {
    	  const gr_complex *in = static_cast<const gr_complex*>(input_items[0]);
    	  gr_complex *out = static_cast<gr_complex*>(output_items[0]);

    	  for(int i = 0; i < noutput_items; ++i) {
    	    gr_complex sum(0.0,0.0);
    	    for(int x = 0; x < d_vlen; ++x) {
    	      sum += *(in++);
    	    }
    	    *(out++) = sum;
    	  }

    	  return noutput_items;
    }

  } /* namespace ofdm */
} /* namespace gr */

