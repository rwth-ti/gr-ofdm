/* -*- c++ -*- */
/* 
 * Copyright 2015 <+YOU OR YOUR COMPANY+>.
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

#include <gnuradio/io_signature.h>
#include "fbmc_asymmetrical_vector_mask_vcvc_impl.h"

namespace gr {
  namespace ofdm {

	fbmc_asymmetrical_vector_mask_vcvc::sptr
	fbmc_asymmetrical_vector_mask_vcvc::make(int M, int start, int end)
	{
	  return gnuradio::get_initial_sptr
		(new fbmc_asymmetrical_vector_mask_vcvc_impl(M, start, end));
	}	

	/*
	 * The private constructor
	 */
	fbmc_asymmetrical_vector_mask_vcvc_impl::fbmc_asymmetrical_vector_mask_vcvc_impl(int M, int start, int end)
	  : gr::sync_block("fbmc_asymmetrical_vector_mask_vcvc",
			  gr::io_signature::make(1, 1, sizeof(gr_complex)*M),
			  gr::io_signature::make(1, 1, sizeof(gr_complex)*(end-start+1))),
	  d_M(M),
	  d_start(start),
	  d_end(end),
	  d_num_carriers(end-start+1)
	{
		assert(d_M>=d_end);
		assert(d_end>d_start);
	}

	/*
	 * Our virtual destructor.
	 */
	fbmc_asymmetrical_vector_mask_vcvc_impl::~fbmc_asymmetrical_vector_mask_vcvc_impl()
	{
	}

	int
	fbmc_asymmetrical_vector_mask_vcvc_impl::work(int noutput_items,
			  gr_vector_const_void_star &input_items,
			  gr_vector_void_star &output_items)
	{
		const gr_complex *in = static_cast< const gr_complex* > ( input_items[0] );
		gr_complex *out = static_cast< gr_complex* > ( output_items[0] );

		const int bytelen = d_num_carriers * sizeof( gr_complex );
		in += d_start;

		for( int i = 0; i < noutput_items; ++i )
		{
		  memcpy( out, in, bytelen );
		  out += d_num_carriers;
		  in += d_M;
		}

		return noutput_items;
	}

  } /* namespace ofdm */
} /* namespace gr */

