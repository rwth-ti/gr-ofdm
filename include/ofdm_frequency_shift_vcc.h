/* -*- c++ -*- */
/*
 * Copyright 2004 Free Software Foundation, Inc.
 * 
 * This file is part of GNU Radio
 * 
 * GNU Radio is free software; you can redistribute it and/or modify
 * it under the terms of the GNU General Public License as published by
 * the Free Software Foundation; either version 2, or (at your option)
 * any later version.
 * 
 * GNU Radio is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 * GNU General Public License for more details.
 * 
 * You should have received a copy of the GNU General Public License
 * along with GNU Radio; see the file COPYING.  If not, write to
 * the Free Software Foundation, Inc., 51 Franklin Street,
 * Boston, MA 02110-1301, USA.
 */

#ifndef INCLUDED_OFDM_FREQUENCY_SHIFT_VCC_H_
#define INCLUDED_OFDM_FREQUENCY_SHIFT_VCC_H_

#include <ofdm_api.h>
#include <gr_block_fwd.h>
#include <gr_block.h>

class ofdm_frequency_shift_vcc;
typedef boost::shared_ptr<ofdm_frequency_shift_vcc> ofdm_frequency_shift_vcc_sptr;

OFDM_API ofdm_frequency_shift_vcc_sptr ofdm_make_frequency_shift_vcc 
	(int vlen, double sensitivity, int cp_length = 0);

/*!
 * @brief Translates ofdm symbols in frequency domain
 * 
 * Input streams:
 * 		1. OFDM blocks
 * 		2. Frequency offset
 * 		3. Frame start trigger
 * 
 * Takes the symbols and multiplies them with a signal whose frequency
 * will be determined by the frequency offset input. This is identical
 * to a shift in frequency domain, except that we can also correct
 * fractional offsets to restore, for example, orthogonality in the
 * fourier spectrum.
 * 
 * A phase accumulator is maintained to have a constant phase shift
 * between adjacent symbols. In presence of a cyclic prefix, the phase
 * shift during the prefix will be corrected. This assumes the offset
 * to be constant per symbol.
 * 
 * A trigger > 0.5 in the third stream causes a reset of the phase
 * accumulator.
 * 
 * We have an internal state variable to buffer the last frequency offset
 * value. It is updated on a trigger. Hence we only need one offset per
 * frame for example.
 * We must have one frame trigger value (0 or 1) per OFDM block.
 */
class OFDM_API ofdm_frequency_shift_vcc : public gr_block
{
  double	d_sensitivity;
  int 		d_vlen;
  double	d_phase;
  int 		d_cp_length;

  friend OFDM_API ofdm_frequency_shift_vcc_sptr
  ofdm_make_frequency_shift_vcc (int vlen, double sensitivity, int cp_length);

  ofdm_frequency_shift_vcc (int vlen, double sensitivity, int cp_length);
  
  
  // internal state
  float d_eps;
  int d_need_eps;
  
  
  void forecast (int noutput_items, gr_vector_int &ninput_items_required);
  

 public:

   int 
   general_work(
       int noutput_items,
       gr_vector_int &ninput_items,
       gr_vector_const_void_star &input_items,
       gr_vector_void_star &output_items ); 
   
   
   virtual int noutput_forecast( gr_vector_int &ninput_items, 
       int available_space, int max_items_avail,
       std::vector<bool> &input_done );
   
 };

#endif /* INCLUDED_OFDM_FREQUENCY_SHIFT_VCC_H_ */
