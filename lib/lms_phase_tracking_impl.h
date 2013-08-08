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

#ifndef INCLUDED_OFDM_LMS_PHASE_TRACKING_IMPL_H
#define INCLUDED_OFDM_LMS_PHASE_TRACKING_IMPL_H

#include <ofdm/lms_phase_tracking.h>

/*!
 * \brief Phase tracking to correct SFO in freq. domain
 *
 * Input:
 *  1. OFDM blocks, frequency domain
 *  2. frame trigger
 *
 *
 */

namespace gr {
  namespace ofdm {

    class lms_phase_tracking_impl : public lms_phase_tracking
    {
     private:
      int d_blk;
      int d_dblk;

      int d_vlen;
      std::vector<bool> d_is_data_symbol;

      int d_pcount;
      std::vector<float> d_pilot_tone;
      std::vector<int> d_pilot;

      std::vector<float> d_gamma_coeff;
      //std::vector<float> d_b_coeff;

      std::vector<float> d_acc_phase;
      std::vector<bool> d_is_pilot;

     public:
      lms_phase_tracking_impl(int vlen, const std::vector<int> &pilot_tones, const std::vector<int> &data_symbols);
      ~lms_phase_tracking_impl();

      // Where all the action really happens
      int work(int noutput_items,
	       gr_vector_const_void_star &input_items,
	       gr_vector_void_star &output_items);
    };

  } // namespace ofdm
} // namespace gr

#endif /* INCLUDED_OFDM_LMS_PHASE_TRACKING_IMPL_H */

