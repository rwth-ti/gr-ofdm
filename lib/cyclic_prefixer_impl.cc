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
#include "cyclic_prefixer_impl.h"

#include <string.h>

namespace gr {
  namespace ofdm {

    cyclic_prefixer::sptr
    cyclic_prefixer::make(size_t input_size, size_t output_size)
    {
      return gnuradio::get_initial_sptr
        (new cyclic_prefixer_impl(input_size, output_size));
    }

    /*
     * The private constructor
     */
    cyclic_prefixer_impl::cyclic_prefixer_impl(size_t input_size, size_t output_size)
      : gr::sync_interpolator("cyclic_prefixer",
              gr::io_signature::make(1, 1, input_size*sizeof(gr_complex)),
              gr::io_signature::make(1, 1, sizeof(gr_complex)), output_size)
    , d_input_size(input_size)
    , d_output_size(output_size)
    {}

    /*
     * Our virtual destructor.
     */
    cyclic_prefixer_impl::~cyclic_prefixer_impl()
    {
    }

    int
    cyclic_prefixer_impl::work(int noutput_items,
			  gr_vector_const_void_star &input_items,
			  gr_vector_void_star &output_items)
    {
    	const gr_complex *in = static_cast<const gr_complex*>(input_items[0]);
		gr_complex *out = static_cast<gr_complex*>(output_items[0]);
		size_t cp_size = d_output_size - d_input_size;

		int produced = 0;

		while(produced < noutput_items) {
			memcpy(out + cp_size, in, d_input_size * sizeof(gr_complex));
			memcpy(out, in + (d_input_size - cp_size), cp_size * sizeof(gr_complex));
			out += d_output_size;
			in += d_input_size;
			produced += d_output_size;
		}

		return produced;
    }

  } /* namespace ofdm */
} /* namespace gr */

