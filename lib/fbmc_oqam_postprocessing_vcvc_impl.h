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

#ifndef INCLUDED_OFDM_FBMC_OQAM_POSTPROCESSING_VCVC_IMPL_H
#define INCLUDED_OFDM_FBMC_OQAM_POSTPROCESSING_VCVC_IMPL_H

#include <ofdm/fbmc_oqam_postprocessing_vcvc.h>

namespace gr {
  namespace ofdm {

    class fbmc_oqam_postprocessing_vcvc_impl : public fbmc_oqam_postprocessing_vcvc
    {
     private:
      unsigned int d_M;
      int d_offset;
      int d_tracker;
      int d_theta_sel;
      std::vector<int> d_tc; //theta array counter
      std::vector<gr_complex> d_ones;
      std::vector<gr_complex> d_twos;
      //std::vector< std::vector<gr_complex> > thetas(4, std::vector<gr_complex>(4));
      //gr_complex thetas[100][100];
      std::vector<std::vector<gr_complex> > thetas;
      gr_complex *d_buf;
      gr_complex *d_help2;
      float *d_help3;
      gr_complex *d_help7;
      gr_complex *d_help8;
      float *d_buf_i;
      float *d_buf_q;
      float *d_help7_i;
      float *d_help7_q;
      float *d_help8_i;
      float *d_help8_q;

     public:
      fbmc_oqam_postprocessing_vcvc_impl(unsigned int M, int offset, int theta_sel=0);
      ~fbmc_oqam_postprocessing_vcvc_impl();

      // Where all the action really happens
      int work(int noutput_items,
         gr_vector_const_void_star &input_items,
         gr_vector_void_star &output_items);


    };

  } // namespace ofdm
} // namespace gr

#endif /* INCLUDED_OFDM_FBMC_OQAM_POSTPROCESSING_VCVC_IMPL_H */

