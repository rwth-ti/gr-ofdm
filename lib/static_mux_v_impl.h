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

#ifndef INCLUDED_OFDM_STATIC_MUX_V_IMPL_H
#define INCLUDED_OFDM_STATIC_MUX_V_IMPL_H

#include <ofdm/static_mux_v.h>

namespace gr {
  namespace ofdm {

    class static_mux_v_impl : public static_mux_v
    {
     private:
        int                 d_streamsize;
        std::vector<int>    d_mux_ctrl;
        int                 d_mpos;
        int                 d_msize;

     public:
      static_mux_v_impl(int streamsize, const std::vector<int> &mux_ctrl);
      ~static_mux_v_impl();

      // Where all the action really happens
      void forecast (int noutput_items, gr_vector_int &ninput_items_required);

      int general_work(int noutput_items,
		       gr_vector_int &ninput_items,
		       gr_vector_const_void_star &input_items,
		       gr_vector_void_star &output_items);

      virtual bool check_topology( int ninputs, int noutputs );
      void reset() { d_mpos = 0; }

      virtual int noutput_forecast( gr_vector_int &ninput_items,
          int available_space, int max_items_avail,
          std::vector<bool> &input_done );
    };

  } // namespace ofdm
} // namespace gr

#endif /* INCLUDED_OFDM_STATIC_MUX_V_IMPL_H */

