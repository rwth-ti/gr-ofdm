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

#ifndef INCLUDED_OFDM_ALLOCATION_SRC_IMPL_H
#define INCLUDED_OFDM_ALLOCATION_SRC_IMPL_H

#include <ofdm/allocation_src.h>
#include <gnuradio/thread/thread.h>
#include "zmq.hpp"

namespace gr {
  namespace ofdm {

    class allocation_src_impl : public allocation_src
    {
     private:
         struct d_allocation_struct {
             short id;
             std::vector<char> bitloading;
             std::vector<gr_complex> power;
         };
         d_allocation_struct d_allocation;
         int d_bitcount;
         int d_subcarriers;
         int d_data_symbols;
         gr::thread::mutex d_mutex;

     public:
        allocation_src_impl(int subcarriers, int data_symbols);
        ~allocation_src_impl();

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

#endif /* INCLUDED_OFDM_ALLOCATION_SRC_IMPL_H */

