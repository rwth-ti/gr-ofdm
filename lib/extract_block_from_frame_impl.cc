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
#include "extract_block_from_frame_impl.h"

#include <iostream>
#include <algorithm>

#define DEBUG 0

namespace gr {
  namespace ofdm {

    extract_block_from_frame::sptr
    extract_block_from_frame::make(int vlen, int block_no)
    {
      return gnuradio::get_initial_sptr
        (new extract_block_from_frame_impl(vlen, block_no));
    }

    /*
     * The private constructor
     */
    extract_block_from_frame_impl::extract_block_from_frame_impl(int vlen, int block_no)
      : gr::block("extract_block_from_frame",
              gr::io_signature::make2(
            	        2, 2,
            	        sizeof( gr_complex ) * vlen,
            	        sizeof( char )),
              gr::io_signature::make(1, 1,
            	        sizeof( gr_complex ) * vlen))
     , d_vlen( vlen )
     , d_block_no( block_no )
     , d_ctr( block_no + 1 )
    {}

    /*
     * Our virtual destructor.
     */
    extract_block_from_frame_impl::~extract_block_from_frame_impl()
    {
    }

    void
    extract_block_from_frame_impl::forecast (int noutput_items, gr_vector_int &ninput_items_required)
    {
        /* <+forecast+> e.g. ninput_items_required[0] = noutput_items */
    	ninput_items_required[0] = ninput_items_required[1] = 1;
    }

    int
    extract_block_from_frame_impl::general_work (int noutput_items,
                       gr_vector_int &ninput_items,
                       gr_vector_const_void_star &input_items,
                       gr_vector_void_star &output_items)
    {
    	  gr_complex const * in = static_cast< gr_complex const * >( input_items[0] );
    	  char const * frame_start = static_cast< char const * >( input_items[1] );
    	  gr_complex * out = static_cast< gr_complex * >( output_items[0] );

    	  int produced = 0;

    	  int const nin = std::min( ninput_items[0], ninput_items[1] );

    	  int i = 0;
    	  for( ; i < nin; ++i )
    	  {
    	    if( frame_start[i] != 0 )
    	    {
    	      d_ctr == 0;
    	    }

    	    if( d_ctr < d_block_no )
    	    {
    	      ++d_ctr;
    	    }
    	    else if( d_ctr == d_block_no )
    	    {
    	      std::copy( in + i * d_vlen, in + ( i + 1 ) * d_vlen,
    	        out + produced * d_vlen );

    	      ++d_ctr;
    	      ++produced;

    	    } // if d_ctr < d_block_no

    	  } // for-loop over input

    	  consume( 0, i );
    	  consume( 1, i );

    	  return produced;
    }

  } /* namespace ofdm */
} /* namespace gr */

