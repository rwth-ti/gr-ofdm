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
#include "allocation_buffer_impl.h"

namespace gr {
  namespace ofdm {

    allocation_buffer::sptr
    allocation_buffer::make(int subcarriers, int data_symbols, char *address, bool coding)
    {
      return gnuradio::get_initial_sptr
        (new allocation_buffer_impl(subcarriers, data_symbols, address, coding));
    }

    /*
     * The private constructor
     */
    allocation_buffer_impl::allocation_buffer_impl(int subcarriers, int data_symbols, char *address, bool coding)
        : gr::sync_block("allocation_buffer",
                         gr::io_signature::make(1, 1, sizeof(short)),
                         gr::io_signature::make(0, 0, 0))
    	,d_bitcount_out(2000)
        ,d_subcarriers(subcarriers)
    	, d_data_symbols(data_symbols)
    	, d_allocation_buffer(256) //TODO: id size hardcoded
		,d_coding( coding )
		,d_bitspermode( {1,2,3,4,6,8,9,10,12})
    {
        std::vector<int> out_sig(3);
        out_sig[0] = sizeof(int);                               // bitcount
        out_sig[1] = sizeof(uint8_t)*subcarriers;                  // bitloading
        out_sig[2] = sizeof(float)*subcarriers;            // power
        set_output_signature(io_signature::makev(3,3,out_sig));

        // generate an initial allocation with id -1
        std::vector<uint8_t> bitloading_vec;
        std::vector<float> power_vec;
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

                // Convert to string needed by the deserialize_str method
//                std::string msg_str;
//                msg_str.append((char *)msg.data(), msg.size());
//                // deserialize
//                pmt::pmt_t pmt_tuple = pmt::deserialize_str(msg_str);
//                pmt::pmt_t pmt_id = pmt::tuple_ref(pmt_tuple,0);
//                pmt::pmt_t pmt_bitloading = pmt::tuple_ref(pmt_tuple,1);
//                pmt::pmt_t pmt_power = pmt::tuple_ref(pmt_tuple,2);
//                // copy message into allocation struct and find id to put into buffer
//                d_allocation_struct rcvd_alloc;
//                rcvd_alloc.id = (short)pmt::to_long(pmt_id);
//                rcvd_alloc.bitloading = pmt::u8vector_elements(pmt_bitloading);
//                rcvd_alloc.power = pmt::c32vector_elements(pmt_power);
//                d_allocation_buffer[rcvd_alloc.id] = rcvd_alloc;

                // copy message into allocation struct and find id to put into buffer
                d_allocation_struct rcvd_alloc;
                rcvd_alloc.id = *(uint8_t*)msg.data();
                rcvd_alloc.bitloading.assign((uint8_t*)msg.data()
                                                              +sizeof(rcvd_alloc.id),
                                                              (uint8_t*)msg.data()
                                                              +sizeof(rcvd_alloc.id)
                                                              +d_subcarriers*sizeof(rcvd_alloc.bitloading[0]));
                rcvd_alloc.power.assign((float*)((uint8_t*)msg.data()
                                                             +sizeof(rcvd_alloc.id)
                                                             +d_subcarriers*sizeof(rcvd_alloc.bitloading[0])),
                                                             (float*)((uint8_t*)msg.data()
                                                             +sizeof(rcvd_alloc.id)
                                                             +d_subcarriers*sizeof(rcvd_alloc.bitloading[0])
                                                             +d_subcarriers*sizeof(rcvd_alloc.power[0])));
                d_allocation_buffer[rcvd_alloc.id] = rcvd_alloc;

            } else {
                msg_received = false;
            }
        }
    }

    void
    allocation_buffer_impl::set_allocation(std::vector<uint8_t> bitloading,
                                        std::vector<float> power)
    {
        // clear and write bitloading output vector
        d_bitloading_out = bitloading;

        // clear and write power output vector
        d_power_out = power;

        int sum_of_elems = 0;
        if (d_coding)
        {
        	for(std::vector<uint8_t>::iterator j=bitloading.begin();j!=bitloading.end();++j)
        		sum_of_elems += d_bitspermode[*j-1];
        	d_bitcount_out = sum_of_elems*d_data_symbols/2;
        }
        else
        {
        	for(std::vector<uint8_t>::iterator j=bitloading.begin();j!=bitloading.end();++j)
        		sum_of_elems += *j;
        	d_bitcount_out = sum_of_elems*d_data_symbols;
        }
    }


    int
    allocation_buffer_impl::work(int noutput_items,
                                 gr_vector_const_void_star &input_items,
                                 gr_vector_void_star &output_items)

    {
        const short *in_id = (const short *) input_items[0];
        int *out_bitcount = (int *) output_items[0];
        uint8_t *out_bitloading = (uint8_t *) output_items[1];
        float *out_power = (float *) output_items[2];

        for(int i=0; i < noutput_items; i++)
        {
            // Receive allocation from Tx
            recv_allocation();

            // set new allocation
            set_allocation(d_allocation_buffer[*in_id].bitloading,d_allocation_buffer[*in_id].power);
            // output
            out_bitcount[i] = d_bitcount_out; 
            //FIXME: probably dirty hack
            // output vector for data (bpsk is used for id)
            memcpy(&out_bitloading[i*d_subcarriers], &d_bitloading_out[0], sizeof(uint8_t)*d_subcarriers);
            // output 1 vector for id and the rest for data
            memcpy(&out_power[i*d_subcarriers], &d_power_out[0], sizeof(float)*d_subcarriers);
        }
        return noutput_items;
    }

  } /* namespace ofdm */
} /* namespace gr */

