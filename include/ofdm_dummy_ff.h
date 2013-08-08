/* -*- c++ -*- */
/* 
 * Copyright 2013 <+YOU OR YOUR COMPANY+>.
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


#ifndef INCLUDED_OFDM_DUMMY_FF_H
#define INCLUDED_OFDM_DUMMY_FF_H

#include <ofdm_api.h>
#include <gr_block.h>

class ofdm_dummy_ff;

typedef boost::shared_ptr<ofdm_dummy_ff> ofdm_dummy_ff_sptr;

OFDM_API ofdm_dummy_ff_sptr ofdm_make_dummy_ff ();

/*!
 * \brief <+description+>
 * \ingroup ofdm
 *
 */
class OFDM_API ofdm_dummy_ff : public gr_block
{
 private:
	friend OFDM_API ofdm_dummy_ff_sptr ofdm_make_dummy_ff ();

	ofdm_dummy_ff();

 public:
  ~ofdm_dummy_ff();

	void forecast (int noutput_items, gr_vector_int &ninput_items_required);

	// Where all the action really happens
	int general_work (int noutput_items,
	    gr_vector_int &ninput_items,
	    gr_vector_const_void_star &input_items,
	    gr_vector_void_star &output_items);
};

#endif /* INCLUDED_OFDM_DUMMY_FF_H */

