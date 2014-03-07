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

#ifndef INCLUDED_OFDM_STREAM_CONTROLLED_MUX_IMPL_H
#define INCLUDED_OFDM_STREAM_CONTROLLED_MUX_IMPL_H

#include <ofdm/stream_controlled_mux.h>

/*!
 * \brief Input stream controls multiplexing
 *
 * For each item on input 1, one item from a selected input is multiplexed
 * in the output. Items in 1 should be in range (0, number of mux_ports-1).
 */

namespace gr {
  namespace ofdm {

    class stream_controlled_mux_impl : public stream_controlled_mux
    {
     private:
        int d_streamsize;
        unsigned int d_next_input;

     public:
      stream_controlled_mux_impl(int streamsize);
      ~stream_controlled_mux_impl();

      // Where all the action really happens
      void forecast (int noutput_items, gr_vector_int &ninput_items_required);

      int general_work(int noutput_items,
		       gr_vector_int &ninput_items,
		       gr_vector_const_void_star &input_items,
		       gr_vector_void_star &output_items);

      virtual int noutput_forecast( gr_vector_int &ninput_items,
          int available_space, int max_items_avail,
          std::vector<bool> &input_done );
    };

  } // namespace ofdm
} // namespace gr

#endif /* INCLUDED_OFDM_STREAM_CONTROLLED_MUX_IMPL_H */

