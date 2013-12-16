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
    allocation_buffer::make(int subcarriers, int data_symbols)
    {
      return gnuradio::get_initial_sptr
        (new allocation_buffer_impl(subcarriers, data_symbols));
    }

    /*
     * The private constructor
     */
    allocation_buffer_impl::allocation_buffer_impl(int subcarriers, int data_symbols)
        : gr::sync_block("allocation_buffer",
                         gr::io_signature::make(1, 1, sizeof(short)),
                         gr::io_signature::make(0, 0, 0))
        ,d_subcarriers(subcarriers), d_data_symbols(data_symbols)
    {
        std::vector<int> out_sig(4);
        out_sig[0] = sizeof(int);
        out_sig[1] = sizeof(char)*subcarriers;
        out_sig[2] = sizeof(char)*subcarriers;
        out_sig[3] = sizeof(float)*subcarriers;
        set_output_signature(io_signature::makev(4,4,out_sig));
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
        int *out_bitcount = (int *) output_items[0];
        char *out_bitloading = (char *) output_items[2];
        float *out_power = (float *) output_items[3];


        // Tell runtime system how many output items we produced.
        return noutput_items;
    }

  } /* namespace ofdm */
} /* namespace gr */

