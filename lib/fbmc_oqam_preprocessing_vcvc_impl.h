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

#ifndef INCLUDED_OFDM_FBMC_OQAM_PREPROCESSING_VCVC_IMPL_H
#define INCLUDED_OFDM_FBMC_OQAM_PREPROCESSING_VCVC_IMPL_H

#include <ofdm/fbmc_oqam_preprocessing_vcvc.h>

namespace gr {
  namespace ofdm {

    class fbmc_oqam_preprocessing_vcvc_impl : public fbmc_oqam_preprocessing_vcvc
    {
     private:
      // Nothing to declare in this block.
      unsigned int d_M;
      int d_offset;
      int d_theta_sel;
      std::vector<int> d_offsets;
      std::vector<gr_complex> d_v1_re;
      std::vector<gr_complex> d_v1_im;
      std::vector<gr_complex> d_v2_re;
      std::vector<gr_complex> d_v2_im;
      std::vector<gr_complex> d_v3_re;
      std::vector<gr_complex> d_v3_im;
      std::vector<gr_complex> d_v4_re;
      std::vector<gr_complex> d_v4_im;
      //std::vector<gr_complex> d_js;

      float *xreal;
	  float *ximag;
	  gr_complex *sum1;
	  gr_complex *sum2;
	  gr_complex *sum3;
	  gr_complex *sum4;
	  gr_complex *sumc;
	  gr_complex *sumcc;
	  float *sum1_i;
	  float *sum1_q;
	  float *sum2_i;
	  float *sum2_q;
	  float *sum3_i;
	  float *sum3_q;
	  float *sum4_i;
	  float *sum4_q;
	  float *sumc_i;
	  float *sumc_q;
	  float *sumcc_i;
	  float *sumcc_q;;

     public:
      fbmc_oqam_preprocessing_vcvc_impl(unsigned int M, int offset, int theta_sel);
      ~fbmc_oqam_preprocessing_vcvc_impl();

      // Where all the action really happens
      int work(int noutput_items,
         gr_vector_const_void_star &input_items,
         gr_vector_void_star &output_items);

      unsigned int get_M();
      void set_M(unsigned int new_M);
      int get_offset();
      void set_offset(int new_offset);

      gr_complex vre0[2];
      gr_complex vre1[2];
      gr_complex vim0[2];
      gr_complex vim1[2];
    };

  } // namespace ofdm
} // namespace gr

#endif /* INCLUDED_OFDM_FBMC_OQAM_PREPROCESSING_VCVC_IMPL_H */

