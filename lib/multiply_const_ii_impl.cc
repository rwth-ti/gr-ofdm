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
#include "multiply_const_ii_impl.h"

namespace gr {
  namespace ofdm {

    multiply_const_ii::sptr
    multiply_const_ii::make(float k)
    {
      return gnuradio::get_initial_sptr
        (new multiply_const_ii_impl(k));
    }

    /*
     * The private constructor
     */
    multiply_const_ii_impl::multiply_const_ii_impl(float k)
      : gr::sync_block("multiply_const_ii",
              gr::io_signature::make(1, 1, sizeof (int)),
              gr::io_signature::make(1, 1, sizeof (int)))
    	, d_k (k)
    {}

    /*
     * Our virtual destructor.
     */
    multiply_const_ii_impl::~multiply_const_ii_impl()
    {
    }

    int
    multiply_const_ii_impl::work(int noutput_items,
			  gr_vector_const_void_star &input_items,
			  gr_vector_void_star &output_items)
    {
    	  int *iptr = (int *) input_items[0];
    	  int *optr = (int *) output_items[0];

    	  int	size = noutput_items;

    	  while (size >= 8){
    	    *optr++ = (float)*iptr++ * d_k;
    	    *optr++ = (float)*iptr++ * d_k;
    	    *optr++ = (float)*iptr++ * d_k;
    	    *optr++ = (float)*iptr++ * d_k;
    	    *optr++ = (float)*iptr++ * d_k;
    	    *optr++ = (float)*iptr++ * d_k;
    	    *optr++ = (float)*iptr++ * d_k;
    	    *optr++ = (float)*iptr++ * d_k;
    	    size -= 8;
    	  }

    	  while (size-- > 0)
    	    *optr++ = (float)*iptr++ * d_k;

    	  return noutput_items;
    }

  } /* namespace ofdm */
} /* namespace gr */

