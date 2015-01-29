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

#ifndef INCLUDED_OFDM_FBMC_ASYMMETRICAL_VECTOR_PADDING_VCVC_IMPL_H
#define INCLUDED_OFDM_FBMC_ASYMMETRICAL_VECTOR_PADDING_VCVC_IMPL_H

#include <ofdm/fbmc_asymmetrical_vector_padding_vcvc.h>

#include <vector>
#include <boost/shared_array.hpp>

namespace gr {
  namespace ofdm {

	class fbmc_asymmetrical_vector_padding_vcvc_impl : public fbmc_asymmetrical_vector_padding_vcvc
	{
	 private:
	  // Nothing to declare in this block.
	  int d_start, d_end, d_vlen, d_padding_left,d_padding_right,d_carriers;

	 public:
	  fbmc_asymmetrical_vector_padding_vcvc_impl(int start, int end, int vlen, int padding_left);
	  ~fbmc_asymmetrical_vector_padding_vcvc_impl();

	  // Where all the action really happens
	  int work(int noutput_items,
		   gr_vector_const_void_star &input_items,
		   gr_vector_void_star &output_items);
	};

  } // namespace ofdm
} // namespace gr

#endif /* INCLUDED_OFDM_FBMC_ASYMMETRICAL_VECTOR_PADDING_VCVC_IMPL_H */

