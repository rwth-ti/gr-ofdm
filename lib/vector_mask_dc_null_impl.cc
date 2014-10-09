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

#ifdef HAVE_CONFIG_H
#include "config.h"
#endif

#include <gnuradio/io_signature.h>
#include "vector_mask_dc_null_impl.h"

#include <iostream>
#include <string.h>

namespace gr {
  namespace ofdm {

    vector_mask_dc_null::sptr
    vector_mask_dc_null::make(size_t vlen, size_t cut_left, size_t mask_len, size_t dc_zeros, std::vector<unsigned char> mask)
    {
      return gnuradio::get_initial_sptr
        (new vector_mask_dc_null_impl(vlen, cut_left, mask_len, dc_zeros, mask));
    }

    /*
     * The private constructor
     */
    vector_mask_dc_null_impl::vector_mask_dc_null_impl(size_t vlen, size_t cut_left, size_t mask_len, size_t dc_zeros, std::vector<unsigned char> mask)
      : gr::sync_block("vector_mask_dc_null",
              gr::io_signature::make(1, 1, vlen * sizeof(gr_complex) ),
              gr::io_signature::make(1, 1, mask_len * sizeof(gr_complex)))
		, d_vlen( vlen )
		, d_cut_left( cut_left )
		, d_mask_len( mask_len )
    	, d_dc_zeros (dc_zeros)
		, d_mask( mask )
    {}

    /*
     * Our virtual destructor.
     */
    vector_mask_dc_null_impl::~vector_mask_dc_null_impl()
    {
    }

    int
    vector_mask_dc_null_impl::work(int noutput_items,
			  gr_vector_const_void_star &input_items,
			  gr_vector_void_star &output_items)
    {
  	  const gr_complex *in = static_cast< const gr_complex* > ( input_items[0] );
  	  gr_complex *out = static_cast< gr_complex* > ( output_items[0] );

  	  const int bytelen = d_mask_len/2 * sizeof( gr_complex );
  	  in += d_cut_left;

  	  for( int i = 0; i < noutput_items; ++i )
  	  {
  	    memcpy( out, in, bytelen );
  	    out += d_mask_len/2;
  	    in += d_mask_len/2 +d_dc_zeros;
  	    memcpy( out, in, bytelen );
  	    out += d_mask_len/2;
  	    in += d_vlen - d_mask_len/2 -d_dc_zeros;
  	  }

      return noutput_items;
    }

  } /* namespace ofdm */
} /* namespace gr */

