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

#ifndef INCLUDED_OFDM_SCHMIDL_CFO_ESTIMATOR_IMPL_H
#define INCLUDED_OFDM_SCHMIDL_CFO_ESTIMATOR_IMPL_H

#include <ofdm/schmidl_cfo_estimator.h>

/*!
  Carrier frequency offset estimator
  This block calculates a metric that will show up a maximum at the point that is an
  estimation for the integer part of the present frequency shift.
  It supposes	to have a special preamble design, where two pn sequences are transmitted
  on the even subchannels. See Schmidl & Cox's paper.

  Input 1 is a a stream of fft'ed preamble 1.
  Input 2 is a a stream of fft'ed preamble 2.

  Output is a vector of size estimation_range * 2 + 1
  Index goes from -estimation_range to +estimation_range
  Maximum at e.g. 80 with range = 100 means: 80 => -20 => offset is -20 + frac(offset)

  The parameter differential_pn_seq is meant to be:
    v_k = conjugate(sqrt(2) * c_2_k / c_1_k)
  assuming that c_1_k and c_2_k are the pn sequences of the first and second preamble.
  We ignore even indices.
*/

namespace gr {
  namespace ofdm {

    class schmidl_cfo_estimator_impl : public schmidl_cfo_estimator
    {
     private:
    	  std::vector<gr_complex> d_differential_pn_seq;
    	  int d_fft_length;
    	  int d_carriers;
    	  int d_left_padding;
    	  int d_estimation_range;

     public:
      schmidl_cfo_estimator_impl(const int fft_length, const int carriers, const int estimation_range, const std::vector<gr_complex> &differential_pn_seq);
      ~schmidl_cfo_estimator_impl();

      // Where all the action really happens
      int work(int noutput_items,
	       gr_vector_const_void_star &input_items,
	       gr_vector_void_star &output_items);
    };

  } // namespace ofdm
} // namespace gr

#endif /* INCLUDED_OFDM_SCHMIDL_CFO_ESTIMATOR_IMPL_H */

