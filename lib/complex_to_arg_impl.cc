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
#include "complex_to_arg_impl.h"

namespace gr {
  namespace ofdm {

    complex_to_arg::sptr
    complex_to_arg::make(unsigned int vlen)
    {
      return gnuradio::get_initial_sptr
        (new complex_to_arg_impl(vlen));
    }

    /*
     * The private constructor
     */
    complex_to_arg_impl::complex_to_arg_impl(unsigned int vlen)
      : gr::sync_block("complex_to_arg",
              gr::io_signature::make(1, 1, sizeof(gr_complex)*vlen),
              gr::io_signature::make(1, 1, sizeof(float)*vlen))
		, d_vlen(vlen)
    {}

    /*
     * Our virtual destructor.
     */
    complex_to_arg_impl::~complex_to_arg_impl()
    {
    }

    int
    complex_to_arg_impl::work(int noutput_items,
			  gr_vector_const_void_star &input_items,
			  gr_vector_void_star &output_items)
    {
	  const gr_complex *in = static_cast<const gr_complex*>(input_items[0]);
	  float *out = static_cast<float*>(output_items[0]);

	  for (int i = 0; i < noutput_items*d_vlen; i++){
		out[i] = std::arg(in[i]);
	  }

	  return noutput_items;
    }

  } /* namespace ofdm */
} /* namespace gr */

