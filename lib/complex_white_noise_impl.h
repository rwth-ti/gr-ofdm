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

#ifndef INCLUDED_OFDM_COMPLEX_WHITE_NOISE_IMPL_H
#define INCLUDED_OFDM_COMPLEX_WHITE_NOISE_IMPL_H

#include <ofdm/complex_white_noise.h>

namespace gr {
  namespace ofdm {

    class complex_white_noise_impl : public complex_white_noise
    {
     private:
      class rng_detail;
	  boost::shared_ptr<rng_detail> d_rng_detail;
	  gr_complex  d_mean;
	  float  d_sigma;

     public:
      complex_white_noise_impl(gr_complex mean, float sigma);
      ~complex_white_noise_impl();

      // Where all the action really happens
      int work(int noutput_items,
	       gr_vector_const_void_star &input_items,
	       gr_vector_void_star &output_items);
    };

  } // namespace ofdm
} // namespace gr

#endif /* INCLUDED_OFDM_COMPLEX_WHITE_NOISE_IMPL_H */

