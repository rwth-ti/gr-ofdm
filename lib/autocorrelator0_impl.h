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

#ifndef INCLUDED_OFDM_AUTOCORRELATOR0_IMPL_H
#define INCLUDED_OFDM_AUTOCORRELATOR0_IMPL_H

#include <ofdm/autocorrelator0.h>
#include <ofdm/autocorrelator_stage1.h>
#include <ofdm/autocorrelator_stage2.h>

namespace gr {
  namespace ofdm {

    //typedef boost::shared_ptr<ofdm_autocorrelator0> ofdm_autocorrelator0_sptr;
    class autocorrelator_stage1_impl;
    class autocorrelator_stage2_impl;
    typedef boost::shared_ptr< autocorrelator_stage1_impl > ofdm_autocorrelator_stage1_sptr;
    typedef boost::shared_ptr< autocorrelator_stage2_impl > ofdm_autocorrelator_stage2_sptr;
    class autocorrelator0_impl : public autocorrelator0
    {
     private:
    	int  d_lag;
    	int  d_n_samples;
    	ofdm::autocorrelator_stage1::sptr d_s1;
    	ofdm::autocorrelator_stage2::sptr d_s2;

     public:
      autocorrelator0_impl(int lag, int n_samples);
      ~autocorrelator0_impl();

      // Where all the action really happens
    };

  } // namespace ofdm
} // namespace gr

#endif /* INCLUDED_OFDM_AUTOCORRELATOR0_IMPL_H */

