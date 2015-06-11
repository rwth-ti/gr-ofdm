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
#include "fbmc_vector_copy_vcvc_impl.h"

namespace gr {
  namespace ofdm {

    fbmc_vector_copy_vcvc::sptr
    fbmc_vector_copy_vcvc::make(unsigned int M, unsigned int interpolation)
    {
      return gnuradio::get_initial_sptr
        (new fbmc_vector_copy_vcvc_impl(M, interpolation));
    }

    /*
     * The private constructor
     */
    fbmc_vector_copy_vcvc_impl::fbmc_vector_copy_vcvc_impl(unsigned int M, unsigned int interpolation)
      : gr::sync_interpolator("fbmc_vector_copy_vcvc",
              gr::io_signature::make(1,1, sizeof(gr_complex)*M),
              gr::io_signature::make(1, 1, sizeof(gr_complex)*M), interpolation),
      d_M(M),
      d_interpolation(interpolation)
    {}

    /*
     * Our virtual destructor.
     */
    fbmc_vector_copy_vcvc_impl::~fbmc_vector_copy_vcvc_impl()
    {
    }

    int
    fbmc_vector_copy_vcvc_impl::work(int noutput_items,
			  gr_vector_const_void_star &input_items,
			  gr_vector_void_star &output_items)
    {
        const gr_complex *in = (const gr_complex *) input_items[0];
        gr_complex *out = (gr_complex *) output_items[0];

        // Do <+signal processing+>
/*        for(unsigned int i=0;i<noutput_items*d_M;i++){
          out[i] = in[int(floor(i/(d_interpolation*d_M))*d_M+(i%d_M))];
        }*/

        //paralelized
        for(unsigned int i=0;i<noutput_items;i++){
        	memcpy(&out[i*d_M], &in[ int(floor(i/(d_interpolation))*d_M)], sizeof(gr_complex)*d_M);
         }

        // Tell runtime system how many output items we produced.
        return noutput_items;
    }

  } /* namespace ofdm */
} /* namespace gr */

