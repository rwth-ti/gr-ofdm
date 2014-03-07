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
#include "constellation_sample_filter_impl.h"

#include <string.h>
#include <iostream>
#include <algorithm>

#define DEBUG 0

namespace gr {
  namespace ofdm {

    constellation_sample_filter::sptr
    constellation_sample_filter::make(int arity, int vlen)
    {
      return gnuradio::get_initial_sptr
        (new constellation_sample_filter_impl(arity, vlen));
    }

    /*
     * The private constructor
     */
    constellation_sample_filter_impl::constellation_sample_filter_impl(int arity, int vlen)
      : gr::block("constellation_sample_filter",
              gr::io_signature::make3( 3, 3,
            	        sizeof( gr_complex ) * vlen,        // ofdm blocks
            	        sizeof( char ) * vlen,              // bitmap
            	        sizeof( char )),
              gr::io_signature::make( 1, 1, sizeof( gr_complex )))
    , d_arity( arity )
    , d_vlen( vlen )
    , d_need_bitmap( 1 )
    , d_bitmap( new char[vlen] )
    {
    	  for( int i = 0; i < vlen; ++i )
    	  {
    	    d_bitmap[i] = 0;
    	  }
    }

    /*
     * Our virtual destructor.
     */
    constellation_sample_filter_impl::~constellation_sample_filter_impl()
    {
    }

    void
    constellation_sample_filter_impl::forecast (int noutput_items, gr_vector_int &ninput_items_required)
    {
        /* <+forecast+> e.g. ninput_items_required[0] = noutput_items */
		  ninput_items_required[0] = 1;
		  ninput_items_required[1] = d_need_bitmap;
		  ninput_items_required[2] = 1;
    }

    int
    constellation_sample_filter_impl::general_work (int noutput_items,
                       gr_vector_int &ninput_items,
                       gr_vector_const_void_star &input_items,
                       gr_vector_void_star &output_items)
    {
    	  const gr_complex *sym_in = static_cast< const gr_complex* >( input_items[0] );
    	  const char *map_in = static_cast< const char* >( input_items[1] );
    	  const char *trig = static_cast< const char* >( input_items[2] );
    	  gr_complex *sym_out = static_cast< gr_complex* >( output_items[0] );

    	  // reset
    	  set_output_multiple( 1 );

    	  // use internal state variable
    	  const char * map = d_bitmap.get();
    	  bool do_copy = false;

    	  int n_map = ninput_items[1];
    	  const int space_available = noutput_items;

    	  assert( noutput_items > 0 );

    	  const int vlen = d_vlen;
    	  const int arity = d_arity;

    	//  std::cout << "enter, vlen=" << vlen << " arity=" << arity << std::endl;


    	  int i;
    	  const int n_min = std::min( ninput_items[0], ninput_items[2] );

    	//  std::cout << "n_min=" << n_min << " noutput_items=" << noutput_items
    	//            << " n_map=" << n_map << std::endl;

    	  for( i = 0; i < n_min; ++i )
    	  {
    	//    std::cout << i << "." << std::endl;
    	    bool consume_map = false;

    	    if( trig[i] != 0 )
    	    {
    	      if( n_map == 0 )
    	      {
    	        d_need_bitmap = 1;
    	        break;
    	      }

    	      map = map_in;
    	      consume_map = true;

    	      // if we stop due to not enough output space, don't consume map
    	      // make sure we only consume the map if the correspondig trigger
    	      // is consumed

    	    } // trig[i] != 0

    	    int nout = noutput_items;
    	    bool stop = false;
    	    for( int j = 0; j < vlen; ++j )
    	    {
    	      if( map[j] == arity )
    	      {
    	        if( nout == 0 )
    	        {
    	          stop = true;
    	          break;
    	        } // nout == 0

    	        *sym_out++ = sym_in[j];
    	        --nout;

    	      } // map[j] == arity

    	    } // for-loop over vector elements

    	    if( stop )
    	    {
    	//      std::cout << "stop" << std::endl;
    	      set_output_multiple( noutput_items + 1 );
    	      break;
    	    }

    	    if( consume_map )
    	    {
    	      // at this point, we produced all items corresponding to the current
    	      // trigger, hence we can consume the map.
    	//      std::cout << "consume map" << std::endl;
    	      do_copy = true;
    	      d_need_bitmap = 0;
    	      --n_map; map_in += vlen;
    	    }

    	//    std::cout << "nout=" << nout << std::endl;

    	    noutput_items = nout;
    	    sym_in += vlen;

    	  } // for-loop over items

    	  if( do_copy )
    	  {
    	    memcpy( d_bitmap.get(), map, sizeof(char) * vlen );
    	  }

    	  consume( 0, i );
    	  consume( 2, i );
    	  consume( 1, ninput_items[1] - n_map );

    	//  std::cout << "leave " << i << " " << (ninput_items[1] - n_map)
    	//            << " " << (space_available-noutput_items) << std::endl;

    	  return space_available - noutput_items;
    }

  } /* namespace ofdm */
} /* namespace gr */

