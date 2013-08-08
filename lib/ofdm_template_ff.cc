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
#include "ofdm_template_ff.h"

ofdm_template_ff_sptr
ofdm_make_template_ff ()
{
	return gnuradio::get_initial_sptr (new ofdm_template_ff());
}

/*
 * Specify constraints on number of input and output streams.
 * This info is used to construct the input and output signatures
 * (2nd & 3rd args to gr_block's constructor).  The input and
 * output signatures are used by the runtime system to
 * check that a valid number and type of inputs and outputs
 * are connected to this block.  In this case, we accept
 * only 1 input and 1 output.
 */
static const int MIN_IN = 1;	// mininum number of input streams
static const int MAX_IN = 1;	// maximum number of input streams
static const int MIN_OUT = 1;	// minimum number of output streams
static const int MAX_OUT = 1;	// maximum number of output streams


/*
 * The private constructor
 */
ofdm_template_ff::ofdm_template_ff ()
  : gr_block ("template_ff",
		   gr_make_io_signature(<+MIN_IN+>, <+MAX_IN+>, sizeof(<+ITYPE+>)),
		   gr_make_io_signature(<+MIN_OUT+>, <+MAX_OUT+>, sizeof(<+OTYPE+>)))
{
	// Put in <+constructor stuff+> here
}


/*
 * Our virtual destructor.
 */
ofdm_template_ff::~ofdm_template_ff()
{
	// Put in <+destructor stuff+> here
}


void
ofdm_template_ff::forecast (int noutput_items, gr_vector_int &ninput_items_required)
{
	/* <+forecast+> e.g. ninput_items_required[0] = noutput_items */
}

int
ofdm_template_ff::general_work (int noutput_items,
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

