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

#ifdef HAVE_CONFIG_H
#include "config.h"
#endif

#include <gr_io_signature.h>
#include "ofdm_dummy_ff.h"

ofdm_dummy_ff_sptr
ofdm_make_dummy_ff ()
{
	return gnuradio::get_initial_sptr (new ofdm_dummy_ff());
}


/*
 * The private constructor
 */
ofdm_dummy_ff::ofdm_dummy_ff ()
  : gr_block ("dummy_ff",
		   gr_make_io_signature(<+MIN_IN+>, <+MAX_IN+>, sizeof(<+ITYPE+>)),
		   gr_make_io_signature(<+MIN_OUT+>, <+MAX_OUT+>, sizeof(<+OTYPE+>)))
{
	// Put in <+constructor stuff+> here
}


/*
 * Our virtual destructor.
 */
ofdm_dummy_ff::~ofdm_dummy_ff()
{
	// Put in <+destructor stuff+> here
}


void
ofdm_dummy_ff::forecast (int noutput_items, gr_vector_int &ninput_items_required)
{
	/* <+forecast+> e.g. ninput_items_required[0] = noutput_items */
}

int
ofdm_dummy_ff::general_work (int noutput_items,
				   gr_vector_int &ninput_items,
				   gr_vector_const_void_star &input_items,
				   gr_vector_void_star &output_items)
{
	const <+ITYPE+> *in = (const <+ITYPE+> *) input_items[0];
	<+OTYPE+> *out = (<+OTYPE+> *) output_items[0];

	// Do <+signal processing+>
	// Tell runtime system how many input items we consumed on
	// each input stream.
	consume_each (noutput_items);

	// Tell runtime system how many output items we produced.
	return noutput_items;
}

