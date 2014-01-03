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
        : gr::block("allocation_buffer",
                         gr::io_signature::make(1, 1, sizeof(short)),
                         gr::io_signature::make(0, 0, 0))
        ,d_subcarriers(subcarriers), d_data_symbols(data_symbols)
    {
        std::vector<int> out_sig(3);
        out_sig[0] = sizeof(int);                               // bitcount
        out_sig[1] = sizeof(char)*subcarriers;                  // bitloading
        out_sig[2] = sizeof(gr_complex)*subcarriers;            // power
        set_output_signature(io_signature::makev(3,3,out_sig));

        // generate an initial allocation with id -1
        d_allocation.id = -1;
        std::vector<char> bitloading_vec;
        std::vector<gr_complex> power_vec;
        // default data modulation scheme is BPSK
        for(int i=0;i<subcarriers;i++)
        {
            bitloading_vec.push_back(1);
        }
        // init power allocation vector
        for(int i=0;i<subcarriers;i++)
        {
            power_vec.push_back(1);
        }
        set_allocation(bitloading_vec,power_vec);
    }

    /*
     * Our virtual destructor.
     */
    allocation_buffer_impl::~allocation_buffer_impl()
    {
    }

    void
    allocation_buffer_impl::set_allocation(std::vector<char> bitloading,
                                        std::vector<gr_complex> power)
    {
        // push back 0s for ID symbol to ignore in demodulator
        // NOTE: this is different in tx allocation_src!
        for(int i=0;i<d_subcarriers;i++)
        {
            d_allocation.bitloading.push_back(0);
        }
        // insert data symbol modulation at the end ONCE
        d_allocation.bitloading.insert(d_allocation.bitloading.end(), bitloading.begin(), bitloading.end());

        // push back ID symbol power
        for(int i=0;i<d_subcarriers;i++)
        {
            d_allocation.power.push_back(1);
        }
        // insert data symbol power at the end TIMES data_symbols
        for(int i=0;i<d_data_symbols;i++)
        {
            d_allocation.power.insert(d_allocation.power.end(), power.begin(), power.end());
        }

        int sum_of_elems = 0;
        for(std::vector<char>::iterator j=bitloading.begin();j!=bitloading.end();++j)
            sum_of_elems += *j;
        d_bitcount = sum_of_elems*d_data_symbols;
    }

    int
    allocation_buffer_impl::general_work(int noutput_items,
                                         gr_vector_int &ninput_items,
                                         gr_vector_const_void_star &input_items,
                                         gr_vector_void_star &output_items)

    {
        const short *in_id = (const short *) input_items[0];
        int *out_bitcount = (int *) output_items[0];
        char *out_bitloading = (char *) output_items[1];
        gr_complex *out_power = (gr_complex *) output_items[2];

        // find allocation data for incoming id
        // std::vector<d_allocation_struct>::iterator it;
        // it = std::find(d_allocation_buffer.begin(), d_allocation_buffer.end(),
        //                  boost::bind(&d_allocation_struct::id, _1) == *in_id);
        //if (it != d_allocation_buffer->back()) {
        //    // set allocation
        //    set_allocation(it->bitloading, it->power);
        //}

        *out_bitcount = d_bitcount;
        //FIXME: probably dirty hack
        // output 2 vectors for id and data
        memcpy(out_bitloading, &d_allocation.bitloading[0], sizeof(char)*2*d_subcarriers);
        // output 1 vector for id and the rest for data
        memcpy(out_power, &d_allocation.power[0], sizeof(gr_complex)*(1+d_data_symbols)*d_subcarriers);

        produce(0,1);
        produce(1,2);
        produce(2,1+d_data_symbols);

        // Tell runtime system how many output items we produced.
        return WORK_CALLED_PRODUCE;
    }

  } /* namespace ofdm */
} /* namespace gr */

