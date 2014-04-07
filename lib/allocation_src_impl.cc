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
#include "allocation_src_impl.h"
#include <iostream>
#include <pmt/pmt.h>

namespace gr {
  namespace ofdm {

    allocation_src::sptr
    allocation_src::make(int subcarriers, int data_symbols, char *address)
    {
      return gnuradio::get_initial_sptr
        (new allocation_src_impl(subcarriers, data_symbols, address));
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
    allocation_src_impl::allocation_src_impl(int subcarriers, int data_symbols, char *address)
        : gr::block("allocation_src",
                         gr::io_signature::make(0, 0, 0),
                         gr::io_signature::make(0, 0, 0))
        ,d_subcarriers(subcarriers), d_data_symbols(data_symbols)
    {
        std::vector<int> out_sig(4);
        out_sig[0] = sizeof(short);                             // id
        out_sig[1] = sizeof(int);                               // bitcount
        out_sig[2] = sizeof(uint8_t)*subcarriers;                  // bitloading
        out_sig[3] = sizeof(gr_complex)*subcarriers;            // power
        set_output_signature(io_signature::makev(4,4,out_sig));


        std::vector<uint8_t> bitloading_vec;
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
        // generate allocation and allocation_out structures
        d_allocation.id = 0;
        d_allocation_out.id = 0;
        set_allocation(bitloading_vec,power_vec);

        d_context = new zmq::context_t(1);
        d_socket = new zmq::socket_t(*d_context, ZMQ_PUB);
        d_socket->bind(address);
        std::cout << "allocation_src on " << address << std::endl;

        //set_output_multiple((1+d_data_symbols));
        //set_output_multiple((1+d_data_symbols)*d_subcarriers);
        //set_min_output_buffer (3, 2*sizeof(gr_complex)*(1+d_data_symbols)*d_subcarriers);
        //set_max_output_buffer (3, 2*sizeof(gr_complex)*(1+d_data_symbols)*d_subcarriers);
        set_min_noutput_items((1+d_data_symbols));
        //set_max_noutput_items((1+d_data_symbols)*d_subcarriers);
    }

    /*
     * Our virtual destructor.
     */
    allocation_src_impl::~allocation_src_impl()
    {
        delete(d_socket);
        delete(d_context);
    }

    void
    allocation_src_impl::send_allocation()
    {
        // use pmt to serialize allocation struct (this is VERY slow)
//        pmt::pmt_t pmt_id, pmt_bitloading, pmt_power;
//        pmt_id = pmt::from_long(d_allocation.id);
//        pmt_bitloading = pmt::init_u8vector(d_allocation.bitloading.size(),d_allocation.bitloading);
//        pmt_power = pmt::init_c32vector(d_allocation.power.size(),d_allocation.power);
//        pmt::pmt_t pmt_tuple;
//        pmt_tuple = pmt::make_tuple();
//        pmt_tuple = pmt::make_tuple(pmt_id, pmt_bitloading, pmt_power);
//        std::string msg_str = pmt::serialize_str(pmt_tuple);
//
//        // copy to zmq message and send
//        zmq::message_t msg(msg_str.size()+1);
//        memcpy(msg.data(), (void *)msg_str.c_str(), msg_str.size()+1);

        // just write datagram to message with raw copying (much faster)
        zmq::message_t msg(sizeof(d_allocation.id)
                           + d_subcarriers*sizeof(d_allocation.bitloading[0])
                           + d_subcarriers*sizeof(d_allocation.power[0]));
        memcpy(msg.data(), &d_allocation.id, sizeof(d_allocation.id));
        memcpy((uint8_t*)msg.data()+sizeof(d_allocation.id),
                                 &d_allocation.bitloading[0],
                                 d_subcarriers*sizeof(d_allocation.bitloading[0]));
        memcpy((uint8_t*)msg.data()+sizeof(d_allocation.id)+d_subcarriers*sizeof(d_allocation.bitloading[0]),
                                 &d_allocation.power[0],
                                 d_subcarriers*sizeof(d_allocation.power[0]));
        d_socket->send(msg, ZMQ_NOBLOCK);
    }

    void
    allocation_src_impl::set_allocation(std::vector<uint8_t> bitloading,
                                        std::vector<gr_complex> power)
    {
        gr::thread::scoped_lock guard(d_mutex);
        d_allocation.bitloading = bitloading;
        d_allocation.power = power;

        // clear and write bitloading output vector
        d_allocation_out.bitloading.clear();
        // push back ID symbol modulation
        for(int i=0;i<d_subcarriers;i++)
        {
            d_allocation_out.bitloading.push_back(1);
        }
        // insert data symbol modulation at the end ONCE
        d_allocation_out.bitloading.insert(d_allocation_out.bitloading.end(), bitloading.begin(), bitloading.end());

        // clear and write power output vector
        d_allocation_out.power.clear();
        // push back ID symbol power
        for(int i=0;i<d_subcarriers;i++)
        {
            d_allocation_out.power.push_back(1);
        }
        // insert data symbol power at the end TIMES data_symbols
        for(int i=0;i<d_data_symbols;i++)
        {
            d_allocation_out.power.insert(d_allocation_out.power.end(), power.begin(), power.end());
        }

        int sum_of_elems = 0;
        for(std::vector<uint8_t>::iterator j=bitloading.begin();j!=bitloading.end();++j)
            sum_of_elems += *j;
        d_bitcount_out = sum_of_elems*d_data_symbols;
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
        uint8_t *out_bitloading = (uint8_t *) output_items[2];
        gr_complex *out_power = (gr_complex *) output_items[3];

        if (noutput_items < (1+d_data_symbols)) {
            return 0;
        } else {
            for (int i = 0; i < (noutput_items / ((1+d_data_symbols))); i++) {
                // send the allocation to Rx
                send_allocation();

                // now generate outputs
                out_id[i] = d_allocation_out.id;
                out_bitcount[i] = d_bitcount_out;
                //FIXME: probably dirty hack
                // output 2 vectors for id and data
                int bl_idx = i*2*d_subcarriers;
                memcpy(&out_bitloading[bl_idx], &d_allocation_out.bitloading[0], sizeof(uint8_t)*2*d_subcarriers);
                // output 1 vector for id and the rest for data
                int p_idx = i*(1+d_data_symbols)*d_subcarriers;
                memcpy(&out_power[p_idx], &d_allocation_out.power[0], sizeof(gr_complex)*(1+d_data_symbols)*d_subcarriers);

                //increase frame id, [0..255]
                d_allocation.id++;
                if (d_allocation.id > 255) {
                    d_allocation.id = 0;
                }
                d_allocation_out.id = d_allocation.id;

                // Tell runtime system how many output items we produced.
                produce(0,1);
                produce(1,1);
                produce(2,2);
                produce(3,1+d_data_symbols);
            }
            return WORK_CALLED_PRODUCE;
        }
    }
  } /* namespace ofdm */
} /* namespace gr */

