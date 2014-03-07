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
#include "compat_read_ber_from_imgxfer_impl.h"

#include <iostream>

#define DEBUG 0

namespace gr {
  namespace ofdm {

    compat_read_ber_from_imgxfer::sptr
    compat_read_ber_from_imgxfer::make(imgtransfer_sink_sptr xfersink)
    {
      return gnuradio::get_initial_sptr
        (new compat_read_ber_from_imgxfer_impl(xfersink));
    }

    /*
     * The private constructor
     */
    compat_read_ber_from_imgxfer_impl::compat_read_ber_from_imgxfer_impl(imgtransfer_sink_sptr xfersink)
      : gr::block("compat_read_ber_from_imgxfer",
              gr::io_signature::make( 1, 1, sizeof( char )),
              gr::io_signature::make(1, 1, sizeof( float )))
    , d_xfersink( xfersink )
    {}

    /*
     * Our virtual destructor.
     */
    compat_read_ber_from_imgxfer_impl::~compat_read_ber_from_imgxfer_impl()
    {
    }

    void
    compat_read_ber_from_imgxfer_impl::forecast (int noutput_items, gr_vector_int &ninput_items_required)
    {
    	ninput_items_required[0] = 1;
    }

    int
    compat_read_ber_from_imgxfer_impl::general_work (int noutput_items,
                       gr_vector_int &ninput_items,
                       gr_vector_const_void_star &input_items,
                       gr_vector_void_star &output_items)
    {
    	  char const * in = static_cast< char const * >( input_items[0] );
    	  float * out = static_cast< float * >( output_items[0] );

    	  int nout = noutput_items;
    	  int i = 0;
    	  for( ; i < ninput_items[0]; ++i )
    	  {
    	    if( in[i] != 0 )
    	    {
    	      if( nout == 0 )
    	        break;

    	      float const ber = d_xfersink->get_BER_estimate();
    	      *out = ber;
    	      --nout;
    	      ++out;

    	    } // if in[i] != 0

    	  } // for-loop over input

    	  consume( 0 , i );

    	  return noutput_items - nout;
    }

  } /* namespace ofdm */
} /* namespace gr */

