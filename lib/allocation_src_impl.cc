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
#include <iostream>

namespace gr {
  namespace ofdm {

    allocation_src::sptr
    allocation_src::make(int subcarriers, int data_symbols)
    {
      return gnuradio::get_initial_sptr
        (new allocation_src_impl(subcarriers, data_symbols));
    }

    /*
     * The private constructor
     *
     * Description of output format:
     *
     * id: 0..255
     * bitcount: number of payload bits in a frame
     * bitloading: vector containing 2 vectors with bitloading for 1.: id and 2.: data
     * power: vector containing power allocation vectors for id symbol and every data symbol
     *
     */
    allocation_src_impl::allocation_src_impl(int subcarriers, int data_symbols)
        : gr::block("allocation_src",
                         gr::io_signature::make(0, 0, 0),
                         gr::io_signature::make(0, 0, 0))
        ,d_subcarriers(subcarriers), d_data_symbols(data_symbols)
    {
        std::vector<int> out_sig(4);
        out_sig[0] = sizeof(short);                             // id
        out_sig[1] = sizeof(int);                               // bitcount
        out_sig[2] = sizeof(char)*subcarriers;                  // bitloading
        out_sig[3] = sizeof(gr_complex)*subcarriers;            // power
        set_output_signature(io_signature::makev(4,4,out_sig));

        d_allocation.id = 0;
        d_bitcount = data_symbols*subcarriers;
        // default modulation scheme is BPSK
        for(int i=0;i<2*subcarriers;i++)
        {
            d_allocation.bitloading.push_back(1);
        }
        // init power allocation vector for id and all data symbols
        for(int i=0;i<(data_symbols+1)*subcarriers;i++)
        {
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
    allocation_src_impl::set_allocation(std::vector<char> bitloading,
                                        std::vector<gr_complex> power)
    {
        gr::thread::scoped_lock guard(d_mutex);
        d_allocation.bitloading = bitloading;
        d_allocation.power = power;
        int sum_of_elems = 0;
        for(std::vector<char>::iterator j=d_allocation.bitloading.begin();j!=d_allocation.bitloading.end();++j)
            sum_of_elems += *j;
        d_bitcount = sum_of_elems;
    }


    int
    allocation_src_impl::general_work(int noutput_items,
                                      gr_vector_int &ninput_items,
                                      gr_vector_const_void_star &input_items,
                                      gr_vector_void_star &output_items)

    {
        gr::thread::scoped_lock guard(d_mutex);

        short *out_id = (short *) output_items[0];
        int *out_bitcount = (int *) output_items[1];
        char *out_bitloading = (char *) output_items[2];
        gr_complex *out_power = (gr_complex *) output_items[3];

        *out_id = d_allocation.id;
        *out_bitcount = d_bitcount;
        memcpy(out_bitloading, &d_allocation.bitloading[0], sizeof(char)*2*d_subcarriers);
        memcpy(out_power, &d_allocation.power[0], sizeof(gr_complex)*10*d_subcarriers);

        d_allocation.id++;
        if (d_allocation.id > 255) {
            d_allocation.id = 0;
        }
        produce(0,1);
        produce(1,1);
        produce(2,2);
        produce(3,10);

        // Tell runtime system how many output items we produced.
        return WORK_CALLED_PRODUCE;
    }

  } /* namespace ofdm */
} /* namespace gr */

