/* -*- c++ -*- */
/* 
 * Copyright 2015 <+YOU OR YOUR COMPANY+>.
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

#ifndef INCLUDED_OFDM_FBMC_ASYMMETRICAL_VECTOR_MASK_VCVC_IMPL_H
#define INCLUDED_OFDM_FBMC_ASYMMETRICAL_VECTOR_MASK_VCVC_IMPL_H

#include <ofdm/fbmc_asymmetrical_vector_mask_vcvc.h>

namespace gr {
  namespace ofdm {

    class fbmc_asymmetrical_vector_mask_vcvc_impl : public fbmc_asymmetrical_vector_mask_vcvc
    {
     private:
      // Nothing to declare in this block.
      int d_M;
      int d_start;
      int d_end;
      int d_num_carriers;

     public:
      fbmc_asymmetrical_vector_mask_vcvc_impl(int M, int start, int end);
      ~fbmc_asymmetrical_vector_mask_vcvc_impl();

      // Where all the action really happens
      int work(int noutput_items,
	       gr_vector_const_void_star &input_items,
	       gr_vector_void_star &output_items);
    };

  } // namespace ofdm
} // namespace gr

#endif /* INCLUDED_OFDM_FBMC_ASYMMETRICAL_VECTOR_MASK_VCVC_IMPL_H */

