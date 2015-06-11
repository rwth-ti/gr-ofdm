/* -*- c++ -*- */
/* 
 * Copyright 2014 <+YOU OR YOUR COMPANY+>.
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

#ifndef INCLUDED_OFDM_MIDAMBLE_INSERT_IMPL_H
#define INCLUDED_OFDM_MIDAMBLE_INSERT_IMPL_H

#include <ofdm/midamble_insert.h>

namespace gr {
  namespace ofdm {

    class midamble_insert_impl : public midamble_insert
    {
     private:
      int  d_vlen;
  	  int  d_frame_len;
	  typedef unsigned int size_type;

	  //cache_ptr d_frame_head;
	  size_type d_head_size;
	  size_type d_data_size;

	  void update();

     public:
      midamble_insert_impl(int vlen, int frame_len);
      ~midamble_insert_impl();

      // Where all the action really happens
      void forecast (int noutput_items, gr_vector_int &ninput_items_required);

      int general_work(int noutput_items,
		       gr_vector_int &ninput_items,
		       gr_vector_const_void_star &input_items,
		       gr_vector_void_star &output_items);
    };

  } // namespace ofdm
} // namespace gr

#endif /* INCLUDED_OFDM_MIDAMBLE_INSERT_IMPL_H */

