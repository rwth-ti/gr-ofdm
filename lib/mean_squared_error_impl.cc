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
#include "mean_squared_error_impl.h"

#include <iostream>


#define DEBUG 0

namespace gr {
  namespace ofdm {

    mean_squared_error::sptr
    mean_squared_error::make(int vlen, unsigned long window, bool reset, double norm_factor)
    {
      return gnuradio::get_initial_sptr
        (new mean_squared_error_impl(vlen, window, reset, norm_factor));
    }

    /*
     * The private constructor
     */
    mean_squared_error_impl::mean_squared_error_impl(int vlen, unsigned long window, bool reset, double norm_factor)
      : gr::block("mean_squared_error",
              gr::io_signature::make(1, 1, sizeof( gr_complex ) * vlen),
              gr::io_signature::make(1, 1, sizeof( float ) * vlen))
    	, d_vlen( vlen )
    	, d_window( window )
    	, d_reset( reset )
    	, d_norm_factor( norm_factor )
    	, d_cnt( window )
    	, d_acc( 0.0 )
    {
    	  if( DEBUG > 0 )
    	    std::cout << "[ofdm mean_squared_error(" << unique_id() << ")] : window = "
    	              << window << " norm_factor = " << norm_factor << " vlen = "
    	              << vlen << std::endl;
    }

    /*
     * Our virtual destructor.
     */
    mean_squared_error_impl::~mean_squared_error_impl()
    {
    }

    void
    mean_squared_error_impl::forecast (int noutput_items, gr_vector_int &ninput_items_required)
    {
        /* <+forecast+> e.g. ninput_items_required[0] = noutput_items */
    	ninput_items_required[0] = d_cnt > 0UL ? 1 : 0;
    }

    int
    mean_squared_error_impl::general_work (int noutput_items,
                       gr_vector_int &ninput_items,
                       gr_vector_const_void_star &input_items,
                       gr_vector_void_star &output_items)
    {
    	const float * in = static_cast< const float* >( input_items[0] );
    	  float * out = static_cast< float* >( output_items[0] );

    	  if( d_cnt == 0 && ! d_reset )
    	  {
    	    return -1;
    	  }

    	  unsigned long const avail = static_cast< unsigned long >( ninput_items[0] );

    	  unsigned int i_max = 0;
    	  if( d_cnt > avail )
    	  {
    	    i_max = ninput_items[0];
    	  }
    	  else
    	  {
    	    i_max = static_cast< unsigned int >( d_cnt );
    	  }

    	  unsigned int const consumed = i_max;

    	  i_max *= 2 * d_vlen; // complex stream treated as float stream

    	  double acc = 0.0;
    	  for( unsigned int i = 0; i < i_max; ++i )
    	  {
    	    float const x = in[i]*in[i];
    	    acc += x;
    	  }
    	  d_acc += acc;

    	  d_cnt -= static_cast< unsigned long >( consumed );
    	  consume( 0, consumed );

    	  if( d_cnt == 0 )
    	  {
    	    assert( noutput_items >  0 );
    	    out[0] = static_cast< float >( d_acc / d_norm_factor );

    	    if( d_reset )
    	    {
    	      d_cnt = d_window;
    	      d_acc = 0.0;
    	    }

    	    return 1;

    	  } // if( d_cnt == 0 )

    	  return 0;
    }

  } /* namespace ofdm */
} /* namespace gr */

