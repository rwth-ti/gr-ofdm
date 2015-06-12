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

#ifndef INCLUDED_OFDM_ALLOCATION_SRC_IMPL_H
#define INCLUDED_OFDM_ALLOCATION_SRC_IMPL_H

#include <ofdm/allocation_src.h>
#include <gnuradio/thread/thread.h>
#include <zmq.hpp>
#include <stdint.h>
#include <fstream>

#include <ctime>

namespace gr {
    namespace ofdm {

        class allocation_src_impl : public allocation_src
        {
            private:
                struct d_allocation_struct {
                    uint8_t id;
                    std::vector<uint8_t> bitloading;
                    std::vector<float> power;
                };
                struct d_feedback_information_struct {
                    std::vector<float> snr;
                    short id;
                };

                // local copy of allocation
                d_allocation_struct d_allocation;
                // output vectors have a different format, see set_allocation()
                d_allocation_struct d_allocation_out;
                int d_bitcount_out;
                int d_subcarriers;
                int d_data_symbols;
                bool d_coding;
                int d_modulbitcount_out;
                int d_bitspermode[9];
                int d_modulbitspermode[9];
                gr::thread::mutex d_mutex;

                d_feedback_information_struct d_feedback_information;
                enum d_allocation_scheme_enum {CM, RA, MA};
                d_allocation_scheme_enum d_allocation_scheme;
                int d_power_limit;
                int d_data_rate;
                float d_gap;
                std::map<float, float> d_gap_map;
                void init_gap_map();
                gr_complex d_amplitude_out;
                float d_amplitude_abs;
                std::vector<float> d_amplitude;

                zmq::context_t  *d_context;
                zmq::socket_t   *d_socket;

                zmq::context_t  *d_context_feedback;
                zmq::socket_t   *d_socket_feedback;

                void calculate_bitloading_MA();
                void calculate_bitloading_RA();

            public:
                allocation_src_impl(int subcarriers, int data_symbols, bool coding, char *address, char *fb_address);
                ~allocation_src_impl();

                void send_allocation();
                void recv_snr();
                void calculate_bitloading();

                void set_allocation_scheme(int allocation_scheme);
                void set_power_limit(int power_limit);
                void set_data_rate(int data_rate);
                void set_gap(float gap);


                void set_allocation(std::vector<uint8_t> bitloading,
                        std::vector<float> power);

                // Where all the action really happens
                int general_work(int noutput_items,
                        gr_vector_int &ninput_items,
                        gr_vector_const_void_star &input_items,
                        gr_vector_void_star &output_items);
        };

    } // namespace ofdm
} // namespace gr

#endif /* INCLUDED_OFDM_ALLOCATION_SRC_IMPL_H */

