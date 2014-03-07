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

#ifndef INCLUDED_OFDM_VITERBI_COMBINED_FB_IMPL_H
#define INCLUDED_OFDM_VITERBI_COMBINED_FB_IMPL_H

#include <ofdm/viterbi_combined_fb.h>


namespace gr {
  namespace ofdm {

    class viterbi_combined_fb_impl : public viterbi_combined_fb
    {
     private:
    	  fsm d_FSM;
    	  int d_K;
    	  int d_S0;
    	  int d_SK;
    	  int d_D;
    	  int d_chunkcounter;
    	  int d_chunkdivisor;
    	  std::vector<float> d_TABLE;
    	  ofdm::ofdm_metric_type_t d_TYPE;

     public:
      viterbi_combined_fb_impl(const fsm &FSM, int K, int S0, int SK, int D, int chunkdivisor, const std::vector<float> &TABLE, ofdm::ofdm_metric_type_t TYPE);
      ~viterbi_combined_fb_impl();

      // Where all the action really happens
      void forecast (int noutput_items, gr_vector_int &ninput_items_required);

      int general_work(int noutput_items,
		       gr_vector_int &ninput_items,
		       gr_vector_const_void_star &input_items,
		       gr_vector_void_star &output_items);

        fsm FSM () const { return d_FSM; }
		int K () const { return d_K; }
		int S0 () const { return d_S0; }
		int SK () const { return d_SK; }
		int D () const { return d_D; }
		std::vector<float> TABLE () const { return d_TABLE; }
		ofdm::ofdm_metric_type_t TYPE () const { return d_TYPE; }
		//std::vector<int> trace () const { return d_trace; }
		void set_TABLE (const std::vector<float> &table);
		void set_K (int K);
    };

  } // namespace ofdm
} // namespace gr

#endif /* INCLUDED_OFDM_VITERBI_COMBINED_FB_IMPL_H */

