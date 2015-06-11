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

#ifndef INCLUDED_OFDM_MM_FREQUENCY_ESTIMATOR_IMPL_H
#define INCLUDED_OFDM_MM_FREQUENCY_ESTIMATOR_IMPL_H

#include <ofdm/mm_frequency_estimator.h>

#include <vector>

/*!
 * \brief Frequency Offset estimator with Morelli & Mengali algorithm
 *
 * Based on preambles with several identical parts, the algorithm estimates
 * an existing frequency offset in the range of [-L/2, L/2] where
 * L = \param identical_parts. See the paper for more details.
 *
 * Simply said we use the correlation between the parts and put them in
 * weighted sum, where the weights more or less define our confidence
 * in this particular value.
 */

namespace gr {
  namespace ofdm {

    class mm_frequency_estimator_impl : public mm_frequency_estimator
    {
     private:
    	int  d_vlen;
		int  d_L;
		int  d_M;
		int  d_O;
		bool  d_fbmc;

		std::vector<float> d_weights;

     public:
      mm_frequency_estimator_impl(int vlen, int identical_parts, int scale, bool fbmc = 0);
      ~mm_frequency_estimator_impl();

      // Where all the action really happens
      int work(int noutput_items,
	       gr_vector_const_void_star &input_items,
	       gr_vector_void_star &output_items);
    };

  } // namespace ofdm
} // namespace gr

#endif /* INCLUDED_OFDM_MM_FREQUENCY_ESTIMATOR_IMPL_H */

