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
              gr::io_signature::make(0, 0, 0))
        ,d_subcarriers(subcarriers)
    {
        std::vector<int> out_sig(5);
        out_sig[0] = sizeof(short);
        out_sig[1] = sizeof(int);
        out_sig[2] = sizeof(char)*subcarriers;
        out_sig[3] = sizeof(char)*subcarriers;
        out_sig[4] = sizeof(float)*subcarriers;
        set_output_signature(io_signature::makev(5,5,out_sig));

        d_allocation.id = 0;
        // default BPSK
        d_allocation.bitcount = subcarriers;
        for(int i=0;i<subcarriers;i++)
        {
            d_allocation.mask.push_back(1);
            d_allocation.bitloading.push_back(1);
            d_allocation.power.push_back(1);
        }
    }

    /*
     * Our virtual destructor.
     */
    allocation_src_impl::~allocation_src_impl()
    {
    }

    void
    allocation_src_impl::set_allocation(std::vector<char> mask,
                                        std::vector<char> bitloading,
                                        std::vector<float> power)
    {
        gr::thread::scoped_lock guard(d_mutex);
        d_allocation.mask = mask;
        d_allocation.bitloading = bitloading;
        d_allocation.power = power;
    }



    int
    allocation_src_impl::work(int noutput_items,
                              gr_vector_const_void_star &input_items,
                              gr_vector_void_star &output_items)
    {
        gr::thread::scoped_lock guard(d_mutex);

        short *out_id = (short *) output_items[0];
        int *out_bitcount = (int *) output_items[1];
        char *out_mask = (char *) output_items[2];
        char *out_bitloading = (char *) output_items[3];
        float *out_power = (float *) output_items[4];

        *out_id = d_allocation.id;
        d_allocation.id++;
        *out_bitcount = d_allocation.bitcount;
        memcpy(out_mask, &d_allocation.mask, sizeof(char)*d_subcarriers);
        memcpy(out_mask, &d_allocation.bitloading, sizeof(char)*d_subcarriers);
        memcpy(out_mask, &d_allocation.power, sizeof(float)*d_subcarriers);

        // Tell runtime system how many output items we produced.
        return noutput_items;
    }

  } /* namespace ofdm */
} /* namespace gr */

