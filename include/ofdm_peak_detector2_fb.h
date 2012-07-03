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

#ifndef INCLUDED_OFDM_PEAK_DETECTOR2_FF_H
#define INCLUDED_OFDM_PEAK_DETECTOR2_FF_H

#include <ofdm_api.h>
#include <gr_block_fwd.h>
#include <gr_block.h>

class ofdm_peak_detector2_fb;
typedef boost::shared_ptr<ofdm_peak_detector2_fb> ofdm_peak_detector2_fb_sptr;

OFDM_API ofdm_peak_detector2_fb_sptr ofdm_make_peak_detector2_fb(int look_ahead = 10,
    float threshold = 0.0);

class OFDM_API ofdm_peak_detector2_fb : public gr_block
{
private:
  friend OFDM_API ofdm_peak_detector2_fb_sptr ofdm_make_peak_detector2_fb(
      int look_ahead, float threshold);

  ofdm_peak_detector2_fb(int look_ahead, float threshold);

  int d_look_ahead;
  int d_state;
  float d_threshold;

  void forecast(int noutput_items, gr_vector_int &ninput_items_required);

public:
  
  virtual ~ofdm_peak_detector2_fb() {};

  int general_work(
          int noutput_items, gr_vector_int &ninput_items,
          gr_vector_const_void_star &input_items,
          gr_vector_void_star &output_items);
  
  
  virtual int noutput_forecast( gr_vector_int &ninput_items, 
      int available_space, int max_items_avail, std::vector<bool> &input_done );
};

#endif
