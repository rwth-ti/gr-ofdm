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

#ifndef INCLUDED_OFDM_AUTOCORRELATOR_STAGE2_IMPL_H
#define INCLUDED_OFDM_AUTOCORRELATOR_STAGE2_IMPL_H

#include <ofdm/autocorrelator_stage2.h>

namespace gr {
  namespace ofdm {

    class autocorrelator_stage2_impl : public autocorrelator_stage2
    {
     private:
    	int  d_n_samples;
    	int  d_delay;
        gr_complex d_acc1;
    	float      d_acc2;

     public:
      autocorrelator_stage2_impl(int n_samples);
      ~autocorrelator_stage2_impl();

      // Where all the action really happens
      int work(int noutput_items,
	       gr_vector_const_void_star &input_items,
	       gr_vector_void_star &output_items);
    };

  } // namespace ofdm
} // namespace gr

#endif /* INCLUDED_OFDM_AUTOCORRELATOR_STAGE2_IMPL_H */

