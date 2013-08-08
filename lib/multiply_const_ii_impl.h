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

#ifndef INCLUDED_OFDM_MULTIPLY_CONST_II_IMPL_H
#define INCLUDED_OFDM_MULTIPLY_CONST_II_IMPL_H

#include <ofdm/multiply_const_ii.h>

namespace gr {
  namespace ofdm {

    class multiply_const_ii_impl : public multiply_const_ii
    {
     private:
    	float	d_k;		// the constant

     public:
      multiply_const_ii_impl(float k);
      ~multiply_const_ii_impl();

      // Where all the action really happens
      int work(int noutput_items,
	       gr_vector_const_void_star &input_items,
	       gr_vector_void_star &output_items);

      float k () const  { return d_k; }
      void set_k (float k) { d_k = k; }
    };

  } // namespace ofdm
} // namespace gr

#endif /* INCLUDED_OFDM_MULTIPLY_CONST_II_IMPL_H */

