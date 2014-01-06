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

#ifndef INCLUDED_OFDM_ALLOCATION_BUFFER_IMPL_H
#define INCLUDED_OFDM_ALLOCATION_BUFFER_IMPL_H

#include <ofdm/allocation_buffer.h>
#include <boost/circular_buffer.hpp>
#include "zmq.hpp"

namespace gr {
    namespace ofdm {

        class allocation_buffer_impl : public allocation_buffer
        {
            private:
                struct d_allocation_struct {
                    short id;
                    std::vector<char> bitloading;
                    std::vector<gr_complex> power;
                };
                std::vector<d_allocation_struct> d_allocation_buffer;
                std::vector<char> d_bitloading_out;
                std::vector<gr_complex> d_power_out;
                int d_bitcount_out;
                int d_subcarriers;
                int d_data_symbols;

                zmq::context_t  *d_context;
                zmq::socket_t   *d_socket;

            public:
                allocation_buffer_impl(int subcarriers, int data_symbols, char *address);
                ~allocation_buffer_impl();

                void recv_allocation();

                void set_allocation(std::vector<char> bitloading,
                                    std::vector<gr_complex> power);

                // Where all the action really happens
                int general_work(int noutput_items,
                                 gr_vector_int &ninput_items,
                                 gr_vector_const_void_star &input_items,
                                 gr_vector_void_star &output_items);
        };

    } // namespace ofdm
} // namespace gr

#endif /* INCLUDED_OFDM_ALLOCATION_BUFFER_IMPL_H */

