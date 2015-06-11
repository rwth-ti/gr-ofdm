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

#ifndef INCLUDED_OFDM_FBMC_SUBCHANNEL_PROCESSING_VCVC_IMPL_H
#define INCLUDED_OFDM_FBMC_SUBCHANNEL_PROCESSING_VCVC_IMPL_H

#include <ofdm/fbmc_subchannel_processing_vcvc.h>

 #include <iostream>
#include <fstream>

namespace gr {
  namespace ofdm {

    class fbmc_subchannel_processing_vcvc_impl : public fbmc_subchannel_processing_vcvc
    {
     private:
      unsigned int d_M;
      unsigned int d_syms_per_frame;
      std::vector<gr_complex> d_preamble;
      std::vector<float> d_preamble_1;
      std::vector<gr_complex> d_preamble_2;
      int d_sel_eq;
      unsigned int d_preamble_length;
      unsigned int d_frame_length;
      std::vector<gr_complex> d_estimation;
      std::vector<gr_complex> d_estimation_1;
      std::vector<gr_complex> d_estimation_2;
      std::vector<gr_complex> d_eq_coef;
      int ii;
      int fr;
      int estimation_point;
      float normalization_factor;
      float normalization_factor2;
      int d_sel_preamble;
      // std::vector<gr_complex> d_zero_v;
      // std::vector<gr_complex> d_center;
      int d_zero_pads;
      bool d_extra_pad;
      gr_complex *d_conj;
      float *d_squared;
      float *d_divide;
      std::vector<float> d_norm_vect;
      std::vector<float> d_norm_vect2;
      gr_complex *d_conj1;
      gr_complex *d_conj2;
      gr_complex *d_conj3;
      float *d_squared1;
      float *d_divide1;
      std::vector<float> d_ones;

      gr_complex *d_sum1;
      gr_complex *d_sum2;
      gr_complex *d_sum3;;
	  float *d_sum1_i;
	  float *d_sum1_q;
	  float *d_sum2_i;
	  float *d_sum2_q;
	  float *d_sum3_i;
	  float *d_sum3_q;
	  float *d_sumc_i;
	  float *d_sumc_q;

	  gr_complex *d_starte;
	  float *d_starte_i;
	  float *d_starte_q;
	  float *d_start1_i;
	  float *d_start1_q;
	  float *d_start2_i;
	  float *d_start2_q;
	  float *d_estimation_1_i;
	  float *d_estimation_1_q;
	  float *d_estimation_2_i;
	  float *d_estimation_2_q;
	  float *d_estimation_i;
	  float *d_estimation_q;



     public:
      fbmc_subchannel_processing_vcvc_impl(unsigned int M, unsigned int syms_per_frame, int sel_preamble, int zero_pads, bool extra_pad, int sel_eq);
      ~fbmc_subchannel_processing_vcvc_impl();

      // Where all the action really happens
      int work(int noutput_items,
	       gr_vector_const_void_star &input_items,
	       gr_vector_void_star &output_items);
      void get_estimation(const gr_complex  *start);
      void get_equalizer_coefficients(int order);
      std::ofstream estimation_data;
      std::ofstream equalizer_data;
      std::ofstream output_data;
    };

  } // namespace ofdm
} // namespace gr

#endif /* INCLUDED_OFDM_FBMC_SUBCHANNEL_PROCESSING_VCVC_IMPL_H */

