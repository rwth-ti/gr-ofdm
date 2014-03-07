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

#ifndef INCLUDED_OFDM_CHANNEL_ESTIMATOR_02_IMPL_H
#define INCLUDED_OFDM_CHANNEL_ESTIMATOR_02_IMPL_H

#include <ofdm/channel_estimator_02.h>

#include <vector>
#include <boost/shared_array.hpp>

namespace gr {
  namespace ofdm {

    class channel_estimator_02_impl : public channel_estimator_02
    {
     private:
    	  typedef boost::shared_array<float> norm_ctf_t;
    	  typedef boost::shared_array<gr_complex> block_t;

    	  block_t d_inv_ctf_estimate;
    	  norm_ctf_t d_norm_ctf_estimate;
    	  block_t d_tmp_ctf_estimate;
    	  block_t d_tmp_inv_ctf_estimate;
    	  norm_ctf_t d_tmp_norm_ctf_estimate;


    	  int d_blk;
    	  int d_dblk;
    	  int d_vlen;
    	  int d_pcount;

    	  float d_acc_gamma;
    	  float d_acc_b;

    	  struct ofdm_block
    	  {
    	    ofdm_block() : known_block(false), pilot(false) {};
    	    bool known_block;
    	    bool pilot;
    	    block_t block;
    	    std::vector<bool> subc_used;
    	  };

    	  typedef boost::shared_ptr<ofdm_block> ofdm_block_sptr;

    	  std::vector<bool>         d_nondata_block;
    	  std::vector<float>        d_pilot_tone;
    	  std::vector<int>          d_pilot;
    	  std::vector<bool>         d_is_pilot;
    	  std::vector<float>        d_gamma_coeff;
    	  std::vector<float>        d_acc_phase;

    	  std::vector<ofdm_block_sptr>   d_ofdm_frame;




    	  inline void
    	  LMS_phasetracking( gr_complex* out );

    	  inline block_t
    	  channel_estimation(
    	      const gr_complex* in,
    	      gr_complex* out,
    	      float* ctf );

    	  void
    	  init_LMS_phasetracking(
    	      const std::vector<int> &pilot_tones,
    	      const std::vector<int> &nondata_block );

    	  void init_channel_estimation();

     public:
      channel_estimator_02_impl(int vlen, const std::vector<int> &pilot_tones, const std::vector<int> &nondata_block);
      ~channel_estimator_02_impl();

      void set_known_block(int no,
            const std::vector<gr_complex> &block, bool pilot);

      // Where all the action really happens
      int work(int noutput_items,
	       gr_vector_const_void_star &input_items,
	       gr_vector_void_star &output_items);
    };

  } // namespace ofdm
} // namespace gr

#endif /* INCLUDED_OFDM_CHANNEL_ESTIMATOR_02_IMPL_H */

