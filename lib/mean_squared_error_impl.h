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

#ifndef INCLUDED_OFDM_MEAN_SQUARED_ERROR_IMPL_H
#define INCLUDED_OFDM_MEAN_SQUARED_ERROR_IMPL_H

#include <ofdm/mean_squared_error.h>

namespace gr {
  namespace ofdm {

    class mean_squared_error_impl : public mean_squared_error
    {
     private:
      int  		 d_vlen;
	  unsigned long  d_window;
	  bool  	 d_reset;
	  double  	 d_norm_factor;
	  unsigned long  d_cnt;
	  double	 d_acc;

     public:
      mean_squared_error_impl(int vlen, unsigned long window, bool reset, double norm_factor);
      ~mean_squared_error_impl();

      // Where all the action really happens
      void forecast (int noutput_items, gr_vector_int &ninput_items_required);

      int general_work(int noutput_items,
		       gr_vector_int &ninput_items,
		       gr_vector_const_void_star &input_items,
		       gr_vector_void_star &output_items);
      void reset() { d_acc = 0.0; d_cnt = d_window; }
    };

  } // namespace ofdm
} // namespace gr

#endif /* INCLUDED_OFDM_MEAN_SQUARED_ERROR_IMPL_H */

