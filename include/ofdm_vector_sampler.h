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

#ifndef INCLUDED_OFDM_VECTOR_SAMPLER_H_
#define INCLUDED_OFDM_VECTOR_SAMPLER_H_

#include <ofdm_api.h>
#include <gr_block_fwd.h>
#include <gr_block.h>

class ofdm_vector_sampler;
typedef boost::shared_ptr<ofdm_vector_sampler> ofdm_vector_sampler_sptr;

OFDM_API ofdm_vector_sampler_sptr ofdm_make_vector_sampler (int itemsize,int vlen);

/*!
* \brief Sample vector on trigger
*
* inputs:
* - data stream, size=itemsize
* - trigger stream, byte stream
*
* output:
* - sampled vectors, vector stream, size=vlen*itemsize
*
* Function:
* On trigger, it takes the last vlen items, groups them into a vector and
* places the vector in the output stream.
*/
class OFDM_API ofdm_vector_sampler : public gr_block
{
  friend OFDM_API ofdm_vector_sampler_sptr ofdm_make_vector_sampler (int itemsize,int vlen);

  ofdm_vector_sampler (int itemsize,int vlen);

private:
  int d_itemsize;
  int d_vlen;

public:
  void forecast (int noutput_items, gr_vector_int &ninput_items_required);

  int general_work (int noutput_items,
            gr_vector_int &ninput_items,
            gr_vector_const_void_star &input_items,
            gr_vector_void_star &output_items);
  
  virtual int noutput_forecast( gr_vector_int &ninput_items, 
      int available_space, int max_items_avail,
      std::vector<bool> &input_done );
  
  
};

#endif
