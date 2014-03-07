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
#include "sqrt_vff_impl.h"

#include <cmath>

namespace gr {
  namespace ofdm {

    sqrt_vff::sptr
    sqrt_vff::make(int vlen)
    {
      return gnuradio::get_initial_sptr
        (new sqrt_vff_impl(vlen));
    }

    /*
     * The private constructor
     */
    sqrt_vff_impl::sqrt_vff_impl(int vlen)
      : gr::sync_block("sqrt_vff",
              gr::io_signature::make(1, 1, sizeof(float)*vlen),
              gr::io_signature::make(1, 1, sizeof(float)*vlen))
    	, d_vlen(vlen)
    {}

    /*
     * Our virtual destructor.
     */
    sqrt_vff_impl::~sqrt_vff_impl()
    {
    }

    int
    sqrt_vff_impl::work(int noutput_items,
			  gr_vector_const_void_star &input_items,
			  gr_vector_void_star &output_items)
    {
    	const float *in = static_cast<const float*>(input_items[0]);
    	float *out = static_cast<float*>(output_items[0]);

        for(int i = 0; i < noutput_items*d_vlen; ++i)
        {
        out[i] = std::sqrt(in[i]);
        }

        return noutput_items;
    }

  } /* namespace ofdm */
} /* namespace gr */

