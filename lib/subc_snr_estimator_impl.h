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

#ifndef INCLUDED_OFDM_SUBC_SNR_ESTIMATOR_IMPL_H
#define INCLUDED_OFDM_SUBC_SNR_ESTIMATOR_IMPL_H

#include <ofdm/subc_snr_estimator.h>

/*!
 * \brief SNR Estimator with Schmidl & Cox Algorithm
 *
 * This is the implementation of the Schmidl & Cox algorithm for estimating
 * the SNR based on a periodic preamble. See the paper for more details.
 *
 * The algorithm is not numerically stable. Therefore this block additionally
 * limits the output values to an acceptable range.
 *
 * Damn it! This is heavily numerically unstable!!
 */

namespace gr {
  namespace ofdm {

    class subc_snr_estimator_impl : public subc_snr_estimator
    {
     private:
    	int  d_vlen;

     public:
      subc_snr_estimator_impl(int vlen);
      ~subc_snr_estimator_impl();

      // Where all the action really happens
      int work(int noutput_items,
	       gr_vector_const_void_star &input_items,
	       gr_vector_void_star &output_items);
    };

  } // namespace ofdm
} // namespace gr

#endif /* INCLUDED_OFDM_SUBC_SNR_ESTIMATOR_IMPL_H */

