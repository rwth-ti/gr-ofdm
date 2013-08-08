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

#include <gnuradio/io_signature.h>
#include "vector_mask_impl.h"

#include <iostream>
#include <string.h>

namespace gr {
  namespace ofdm {

    vector_mask::sptr
    vector_mask::make(size_t vlen, size_t cut_left, size_t mask_len, std::vector<unsigned char> mask)
    {
      return gnuradio::get_initial_sptr
        (new vector_mask_impl(vlen, cut_left, mask_len, mask));
    }

    /*
     * The private constructor
     */
    vector_mask_impl::vector_mask_impl(size_t vlen, size_t cut_left, size_t mask_len, std::vector<unsigned char> mask)
      : gr::sync_block("vector_mask",
              gr::io_signature::make(1, 1, vlen * sizeof(gr_complex) ),
              gr::io_signature::make(1, 1, mask_len * sizeof(gr_complex)))
    	, d_vlen( vlen )
    	, d_cut_left( cut_left )
    	, d_mask_len( mask_len )
    	, d_mask( mask )
    {}

    /*
     * Our virtual destructor.
     */
    vector_mask_impl::~vector_mask_impl()
    {
    }

    int
    vector_mask_impl::work(int noutput_items,
			  gr_vector_const_void_star &input_items,
			  gr_vector_void_star &output_items)
    {
    	  const gr_complex *in = static_cast< const gr_complex* > ( input_items[0] );
    	  gr_complex *out = static_cast< gr_complex* > ( output_items[0] );

    	  const int bytelen = d_mask_len * sizeof( gr_complex );
    	  in += d_cut_left;

    	  for( int i = 0; i < noutput_items; ++i )
    	  {
    	    memcpy( out, in, bytelen );
    	    out += d_mask_len;
    	    in += d_vlen;
    	  }

    	  return noutput_items;
    }

  } /* namespace ofdm */
} /* namespace gr */

