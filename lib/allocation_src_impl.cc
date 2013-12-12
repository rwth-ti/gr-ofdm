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
#include "allocation_src_impl.h"

namespace gr {
  namespace ofdm {

    allocation_src::sptr
    allocation_src::make(int subcarriers)
    {
      return gnuradio::get_initial_sptr
        (new allocation_src_impl(subcarriers));
    }

    /*
     * The private constructor
     */
    allocation_src_impl::allocation_src_impl(int subcarriers)
      : gr::sync_block("allocation_src",
              gr::io_signature::make(0, 0, 0),
              gr::io_signature::make(5, 5, sizeof(short),
                                           sizeof(int),
                                           sizeof(char)*subcarriers,
                                           sizeof(char)*subcarriers,
                                           sizeof(float)*subcarriers))
    {
        d_subcarrier_allocation.id = 0;
        d_subcarrier_allocation.mask = 0;
        d_subcarrier_allocation.bitloading = 0;
        d_subcarrier_allocation.power = 0;
    }

    /*
     * Our virtual destructor.
     */
    allocation_src_impl::~allocation_src_impl()
    {
    }

    int
    allocation_src_impl::work(int noutput_items,
                              gr_vector_const_void_star &input_items,
                              gr_vector_void_star &output_items)
    {
        short *out = (short *) output_items[0];
        int *out = (int *) output_items[1];
        char *out = (char *) output_items[2];
        char *out = (char *) output_items[3];
        float *out = (float *) output_items[4];


        // Tell runtime system how many output items we produced.
        return noutput_items;
    }

  } /* namespace ofdm */
} /* namespace gr */

