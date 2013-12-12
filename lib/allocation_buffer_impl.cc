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
#include "allocation_buffer_impl.h"

namespace gr {
  namespace ofdm {

    allocation_buffer::sptr
    allocation_buffer::make(int subcarriers)
    {
      return gnuradio::get_initial_sptr
        (new allocation_buffer_impl(subcarriers));
    }

    /*
     * The private constructor
     */
    allocation_buffer_impl::allocation_buffer_impl(int subcarriers)
      : gr::sync_block("allocation_buffer",
              gr::io_signature::make(1, 1, sizeof(short)),
              gr::io_signature::make(4, 4, sizeof(int),
                                           sizeof(char)*subcarriers,
                                           sizeof(char)*subcarriers,
                                           sizeof(float)*subcarriers))

    {
    
    }

    /*
     * Our virtual destructor.
     */
    allocation_buffer_impl::~allocation_buffer_impl()
    {
    }

    int
    allocation_buffer_impl::work(int noutput_items,
                                 gr_vector_const_void_star &input_items,
                                 gr_vector_void_star &output_items)
    {
        const short *in = (const short *) input_items[0];
        int *out = (int *) output_items[0];
        char *out = (char *) output_items[1];
        char *out = (char *) output_items[2];
        float *out = (float *) output_items[3];


        // Tell runtime system how many output items we produced.
        return noutput_items;
    }

  } /* namespace ofdm */
} /* namespace gr */

