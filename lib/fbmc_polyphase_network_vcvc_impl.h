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

#ifndef INCLUDED_OFDM_FBMC_POLYPHASE_NETWORK_VCVC_IMPL_H
#define INCLUDED_OFDM_FBMC_POLYPHASE_NETWORK_VCVC_IMPL_H

#include <ofdm/fbmc_polyphase_network_vcvc.h>

#include <iostream>
#include <fstream>

namespace gr {
  namespace ofdm {

    class fbmc_polyphase_network_vcvc_impl : public fbmc_polyphase_network_vcvc
    {
     private:
      // Nothing to declare in this block.
      unsigned int d_M;
      unsigned int d_K;
      unsigned int d_lp;
      bool d_reverse;
      float* d_taps;

/*	  gr_complex *sum1;
	  gr_complex *sum2;
	  gr_complex *sum3;
	  gr_complex *sum4;
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
	  float *sumcc_q;
	  float *sumccc_i;
	  float *sumccc_q;*/



     public:
      fbmc_polyphase_network_vcvc_impl(unsigned int M, unsigned int K, unsigned int lp, bool reverse);
      ~fbmc_polyphase_network_vcvc_impl();
      void createTaps(unsigned int M, unsigned int K, unsigned int lp, bool reverse, float* taps);

      // Where all the action really happens
      int work(int noutput_items,
	       gr_vector_const_void_star &input_items,
	       gr_vector_void_star &output_items);
      std::ofstream tapdata;
    };

  } // namespace ofdm
} // namespace gr

#endif /* INCLUDED_OFDM_FBMC_POLYPHASE_NETWORK_VCVC_IMPL_H */

