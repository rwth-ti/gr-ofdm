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

#ifndef INCLUDED_OFDM_LMS_PHASE_TRACKING_03_IMPL_H
#define INCLUDED_OFDM_LMS_PHASE_TRACKING_03_IMPL_H

#include <ofdm/lms_phase_tracking_03.h>

#include <vector>

namespace gr {
  namespace ofdm {

    class lms_phase_tracking_03_impl : public lms_phase_tracking_03
    {
     private:
    	int  d_vlen;
    	  int  d_dc_null;

    	  float d_acc_gamma;    //! gradient estimate accumulator
    	  float d_acc_b;        //! offset estimate accumulator

    	  int d_pcount; //! No. of pilot subcarriers
    	  int d_blk;    //! OFDM block counter, reset at frame start
    	  int d_in_da;    //! iterator

    	  std::vector< bool >  d_nondata_block;
    	  std::vector< gr_complex > d_pilot_tone;
    	  std::vector< int >   d_pilot;
    	  std::vector< bool >  d_is_pilot;
    	  std::vector< float > d_gamma_coeff;
    	  std::vector< float > d_acc_phase;
    	  //std::vector< float > d_phase_last;
    	  int  d_need_input_h1;
    	  gr_complex * d_buffer_h1;
    	  //int  d_need_input_h2;
    	  //gr_complex * d_buffer_h2;
    	  //std::vector< gr_complex const> d_ina;

    	  void
    	  init_LMS_phasetracking(
    	      const std::vector<int> &pilot_tones,
    	      const std::vector<int> &nondata_block,
    	      int dc_nulled);

    	  inline void
    	  //LMS_phasetracking( gr_complex const * in_1, gr_complex const * in_2, gr_complex const * inv_ctf_1, gr_complex const * inv_ctf_2,   gr_complex * out );
    	  LMS_phasetracking( gr_complex const * in_1, gr_complex const * inv_ctf_1,  gr_complex * out );

     public:
      lms_phase_tracking_03_impl(int vlen, const std::vector<int> &pilot_subc, std::vector< int > const &nondata_blocks, std::vector< gr_complex > const &pilot_subcarriers, int dc_null);
      ~lms_phase_tracking_03_impl();

      // Where all the action really happens
      void forecast (int noutput_items, gr_vector_int &ninput_items_required);

      int general_work(int noutput_items,
		       gr_vector_int &ninput_items,
		       gr_vector_const_void_star &input_items,
		       gr_vector_void_star &output_items);
    };

  } // namespace ofdm
} // namespace gr

#endif /* INCLUDED_OFDM_LMS_PHASE_TRACKING_03_IMPL_H */

