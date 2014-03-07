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
#include "suppress_erasure_decision_impl.h"

#include <iostream>
#include <algorithm>

#define DEBUG 0

namespace gr {
  namespace ofdm {

    suppress_erasure_decision::sptr
    suppress_erasure_decision::make()
    {
      return gnuradio::get_initial_sptr
        (new suppress_erasure_decision_impl());
    }

    /*
     * The private constructor
     */
    suppress_erasure_decision_impl::suppress_erasure_decision_impl()
      : gr::block("suppress_erasure_decision",
              gr::io_signature::make(1, 1, sizeof( short ) ),
              gr::io_signature::make(1, 1, sizeof( short )))
    {}

    /*
     * Our virtual destructor.
     */
    suppress_erasure_decision_impl::~suppress_erasure_decision_impl()
    {
    }

    void
    suppress_erasure_decision_impl::forecast (int noutput_items, gr_vector_int &ninput_items_required)
    {
        /* <+forecast+> e.g. ninput_items_required[0] = noutput_items */
    	ninput_items_required[0] = 1;
    }

    int
    suppress_erasure_decision_impl::general_work (int noutput_items,
                       gr_vector_int &ninput_items,
                       gr_vector_const_void_star &input_items,
                       gr_vector_void_star &output_items)
    {
    	  short const * in = static_cast< short const * >( input_items[0] );
    	  short * out = static_cast< short * >( output_items[0] );

    	  int prod = 0;
    	  int nout = noutput_items;
    	  int const nin = ninput_items[0];

    	  int i = 0;
    	  while( nout > 0 && i < nin )
    	  {
    	    if( in[i] >= 0 )
    	    {
    	      out[prod++] = in[i];
    	      --nout;
    	    }
    	    ++i;
    	  }


    	//  std::cout << "produce " << prod << " consume " << i << std::endl;

    	  consume( 0, i );
    	  return prod;
    }

  } /* namespace ofdm */
} /* namespace gr */

