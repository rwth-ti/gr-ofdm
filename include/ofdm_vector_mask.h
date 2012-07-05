/* -*- c++ -*- */
/*
 * Copyright 2004,2005,2006 Free Software Foundation, Inc.
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

#ifndef INCLUDED_OFDM_VECTOR_MASK_H_
#define INCLUDED_OFDM_VECTOR_MASK_H_

#include <ofdm_api.h>
#include <gr_block_fwd.h>
#include <gr_sync_block.h>

#include <vector>

class ofdm_vector_mask;
typedef boost::shared_ptr<ofdm_vector_mask> ofdm_vector_mask_sptr;

OFDM_API ofdm_vector_mask_sptr ofdm_make_vector_mask (size_t vlen, size_t cut_left, size_t mask_len, std::vector<unsigned char> mask);

class OFDM_API ofdm_vector_mask : public gr_sync_block
{
	friend OFDM_API ofdm_vector_mask_sptr
		ofdm_make_vector_mask (size_t vlen, size_t cut_left, size_t mask_len, std::vector<unsigned char> mask);
    
	private:
		size_t d_vlen;
		size_t d_cut_left;
		size_t d_mask_len;
		std::vector<unsigned char> d_mask;    

	protected:
		ofdm_vector_mask (size_t vlen, size_t cut_left, size_t mask_len, std::vector<unsigned char> mask);

	public:
		int work (int noutput_items,
			gr_vector_const_void_star &input_items,
			gr_vector_void_star &output_items);
};

#endif /* INCLUDED_OFDM_VECTOR_MASK_H_ */
