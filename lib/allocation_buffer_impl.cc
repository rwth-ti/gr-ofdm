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
    allocation_buffer::make(int subcarriers, int data_symbols, char *address)
    {
      return gnuradio::get_initial_sptr
        (new allocation_buffer_impl(subcarriers, data_symbols, address));
    }

    /*
     * The private constructor
     */
    allocation_buffer_impl::allocation_buffer_impl(int subcarriers, int data_symbols, char *address)
        : gr::block("allocation_buffer",
                         gr::io_signature::make(1, 1, sizeof(short)),
                         gr::io_signature::make(0, 0, 0))
        ,d_subcarriers(subcarriers), d_data_symbols(data_symbols), d_allocation_buffer(256) //TODO: id size hardcoded
    {
        std::vector<int> out_sig(3);
        out_sig[0] = sizeof(int);                               // bitcount
        out_sig[1] = sizeof(char)*subcarriers;                  // bitloading
        out_sig[2] = sizeof(gr_complex)*subcarriers;            // power
        set_output_signature(io_signature::makev(3,3,out_sig));

        // generate an initial allocation with id -1
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
        // init allocation buffer TODO: id size hardcoded
        for(int i=0;i<256;i++) {
            d_allocation_buffer[i].id = i;
            d_allocation_buffer[i].bitloading = bitloading_vec;
            d_allocation_buffer[i].power = power_vec;
        }
        set_allocation(bitloading_vec,power_vec);

        d_context = new zmq::context_t(1);
        d_socket = new zmq::socket_t(*d_context, ZMQ_SUB);
        d_socket->connect(address);
        // subscribe to all incoming messages
        d_socket->setsockopt(ZMQ_SUBSCRIBE, "", 0);

        std::cout << "allocation_buffer on " << address << std::endl;
    }

    /*
     * Our virtual destructor.
     */
    allocation_buffer_impl::~allocation_buffer_impl()
    {
        delete(d_socket);
        delete(d_context);
    }

    void
    allocation_buffer_impl::recv_allocation()
    {
        zmq::pollitem_t items[] = { { *d_socket, 0, ZMQ_POLLIN, 0 } };
        bool msg_received = true;
        while(msg_received) {
            // poll with timeout 0
            zmq::poll (&items[0], 1, 0);
            //  If we got a msg, process
            if (items[0].revents & ZMQ_POLLIN) {
                // Receive data
                zmq::message_t msg;
                d_socket->recv(&msg);
                // copy message into allocation struct and find id to put into buffer
                d_allocation_struct rcvd_alloc;
                rcvd_alloc = *(d_allocation_struct *)msg.data();
                d_allocation_buffer[rcvd_alloc.id] = rcvd_alloc;
            } else {
                msg_received = false;
            }
        }
    }

    void
    allocation_buffer_impl::set_allocation(std::vector<char> bitloading,
                                        std::vector<gr_complex> power)
    {
        // clear and write bitloading output vector
        d_bitloading_out.clear();
        // push back 0s for ID symbol to ignore in demodulator
        // NOTE: this is different in tx allocation_src!
        for(int i=0;i<d_subcarriers;i++)
        {
            d_bitloading_out.push_back(0);
        }
        // insert data symbol modulation at the end ONCE
        d_bitloading_out.insert(d_bitloading_out.end(), bitloading.begin(), bitloading.end());

        // clear and write power output vector
        d_power_out.clear();
        // push back ID symbol power
        for(int i=0;i<d_subcarriers;i++)
        {
            d_power_out.push_back(1);
        }
        // insert data symbol power at the end TIMES data_symbols
        for(int i=0;i<d_data_symbols;i++)
        {
            d_power_out.insert(d_power_out.end(), power.begin(), power.end());
        }

        int sum_of_elems = 0;
        for(std::vector<char>::iterator j=bitloading.begin();j!=bitloading.end();++j)
            sum_of_elems += *j;
        d_bitcount_out = sum_of_elems*d_data_symbols;
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


        // Receive allocation from Tx
        recv_allocation();
        // set new allocation
        set_allocation(d_allocation_buffer[*in_id].bitloading,d_allocation_buffer[*in_id].power);
        // output
        *out_bitcount = d_bitcount_out;
        //FIXME: probably dirty hack
        // output 2 vectors for id and data
        memcpy(out_bitloading, &d_bitloading_out[0], sizeof(char)*2*d_subcarriers);
        // output 1 vector for id and the rest for data
        memcpy(out_power, &d_power_out[0], sizeof(gr_complex)*(1+d_data_symbols)*d_subcarriers);

        // Tell runtime system how many output items we produced.
        consume(0,1);
        produce(0,1);
        produce(1,2);
        produce(2,1+d_data_symbols);
        return WORK_CALLED_PRODUCE;
    }

  } /* namespace ofdm */
} /* namespace gr */

