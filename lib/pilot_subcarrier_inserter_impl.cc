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
#include "pilot_subcarrier_inserter_impl.h"

#include <string.h>
#include <iostream>

#define DEBUG 0

namespace gr {
  namespace ofdm {

    pilot_subcarrier_inserter::sptr
    pilot_subcarrier_inserter::make(int vlen, const std::vector<gr_complex> &symbols, const std::vector<int> &subc_index)
    {
      return gnuradio::get_initial_sptr
        (new pilot_subcarrier_inserter_impl(vlen, symbols, subc_index));
    }

    /*
     * The private constructor
     */
    pilot_subcarrier_inserter_impl::pilot_subcarrier_inserter_impl(int vlen, const std::vector<gr_complex> &symbols, const std::vector<int> &subc_index)
      : gr::sync_block("pilot_subcarrier_inserter",
              gr::io_signature::make( 1, 1, sizeof( gr_complex ) * vlen),
              gr::io_signature::make( 1, 1,
            	        sizeof( gr_complex ) * ( vlen + symbols.size() )))
    	, d_vlen( vlen + symbols.size() )
    	,  d_symbols( symbols )
    {
    	  assert( d_vlen > 0 );
    	  assert( symbols.size() > 0 );
    	  assert( symbols.size() == subc_index.size() );

    	  int last_ind = 0;
    	  int sum = 0;
    	  for( int i = 0; i < subc_index.size(); ++i)
    	  {
    	    const int subc_ind = subc_index[i] + d_vlen / 2;
    	    int p = subc_ind - last_ind;

    	    d_partition.push_back( p ); // data subcarriers
    	    sum += p + 1;

    	    last_ind = subc_ind + 1;
    	  } // for( int i = 0; i < subc_index.size(); ++i)

    	  d_partition.push_back( d_vlen - last_ind ); // data subcarriers
    	  sum += d_partition.back();

    	  assert( sum == d_vlen );
    }

    /*
     * Our virtual destructor.
     */
    pilot_subcarrier_inserter_impl::~pilot_subcarrier_inserter_impl()
    {
    }

    int
    pilot_subcarrier_inserter_impl::work(int noutput_items,
			  gr_vector_const_void_star &input_items,
			  gr_vector_void_star &output_items)
    {
    	  const gr_complex *in = static_cast< const gr_complex* >( input_items[0] );
    	  gr_complex *out = static_cast< gr_complex* >( output_items[0] );

    	  const int partition_size = d_partition.size();

    	  for( int j = 0; j < noutput_items; ++j )
    	  {
    	    // copy data subcarrier partition and insert pilot subcarrier
    	    for( int i = 0; i < partition_size - 1; ++i )
    	    {
    	      const int dsubc = d_partition[i];

    	      out[dsubc] = d_symbols[i];
    	      if( dsubc > 0 )
    	      {
    		memcpy( out, in, dsubc * sizeof( gr_complex ) );
    		out += dsubc+1; in += dsubc;
    	      }

    	    } // for( int i = 0; i < partition_size - 1; ++i )

    	    // copy final data subcarrier partition
    	    const int dsubc = d_partition[ partition_size - 1 ];
    	    if( dsubc > 0 )
    	    {
    	      memcpy( out, in, dsubc * sizeof( gr_complex ) );
    	      out += dsubc; in += dsubc;
    	    }

    	  } // for( int j = 0; j < noutput_items; ++j )

    	  return noutput_items;
    }

  } /* namespace ofdm */
} /* namespace gr */

