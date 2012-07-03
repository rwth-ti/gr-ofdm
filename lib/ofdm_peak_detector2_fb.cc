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


#ifdef HAVE_CONFIG_H
#include "config.h"
#endif

#include <gr_block.h>
#include <string.h>



#include <ofdm_peak_detector2_fb.h>
#include <gr_io_signature.h>

#include <iostream>
#include <algorithm>

#define DEBUG(x)

ofdm_peak_detector2_fb_sptr
ofdm_make_peak_detector2_fb (int look_ahead /* = 10 */,
    float threshold)
{
  return ofdm_peak_detector2_fb_sptr (new ofdm_peak_detector2_fb (look_ahead,
      threshold));
}

ofdm_peak_detector2_fb::ofdm_peak_detector2_fb (int look_ahead,
    float threshold)
  : gr_block ("peak_detector2_fb",
        gr_make_io_signature (1, 1, sizeof (float)),
        gr_make_io_signature (1, 1, sizeof (char))),
  d_look_ahead(look_ahead),
  d_state(0),
  d_threshold(threshold)
{
  // no output multiple!
}

void ofdm_peak_detector2_fb::forecast (int noutput_items,
    gr_vector_int &ninput_items_required)
{
  if(d_state == 0)
    ninput_items_required[0] = noutput_items;
  else
    // Last time, we didn't consume all items since there was a peak
    // that has not been followd by enough items (min. look ahead items!).
    // Therefore, constrain input to a minimal size (i.e. our look ahead window).
    ninput_items_required[0] = std::max(d_look_ahead+1,noutput_items);
}

int ofdm_peak_detector2_fb::general_work (
    int noutput_items,
    gr_vector_int &ninput_items,
    gr_vector_const_void_star &input_items,
    gr_vector_void_star &output_items)
{
  const float *iptr = static_cast<const float*>(input_items[0]);
  char *optr = static_cast<char*>(output_items[0]);

  memset(optr, 0, noutput_items*sizeof(char));
  assert(ninput_items[0] >= noutput_items);

  DEBUG(std::cout << "peak detect inp: " << noutput_items << std::endl;)

  int peak_ind = 0;
  float peak_val = d_threshold;

  for(int i = 0; i < noutput_items; ++i) {
    // search for peak
    if(iptr[i] > peak_val) {
      peak_val = iptr[i];
      peak_ind = i;
      d_state = 1;
    }

    if(peak_val > d_threshold && (i - peak_ind) >= d_look_ahead) {
      // no greater peak followed, i.e. trigger
      optr[peak_ind] = 1;
      peak_val = d_threshold;
      d_state = 0;
    }
  }

  if(peak_val > d_threshold) {
    DEBUG(std::cout << "peak detector passes up to " << peak_ind << std::endl;)
    consume_each(peak_ind);
    return peak_ind;
  } else {
    DEBUG(std::cout << "peak detector consumes all" << std::endl;)
    consume_each(noutput_items);
    return noutput_items;
  }
}


int
ofdm_peak_detector2_fb::noutput_forecast( gr_vector_int &ninput_items,
    int available_space, int max_items_avail, std::vector<bool> &input_done )
{
  // we can possibly consume all input items at once, but may
  // consume less. our rate is <= 1.0. but we cannot consume more
  // than we will possible produce.
  // thus give us the minimum of available space and available items.

  // optim: only one input, no output multiple


  int items = std::min( available_space, ninput_items[0] );


  if( items == 0 && input_done[0] ){
    // If the upstream block is done and we can't produce anything, we're done
    return -1;
  }

  return items;

}
