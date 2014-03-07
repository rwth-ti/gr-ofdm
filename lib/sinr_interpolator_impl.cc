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
#include "sinr_interpolator_impl.h"

#include <string.h>
#include <iostream>

#define DEBUG 0

namespace gr {
  namespace ofdm {

    sinr_interpolator::sptr
    sinr_interpolator::make(int vlen, int skip, const std::vector<int> &load_index)
    {
      return gnuradio::get_initial_sptr
        (new sinr_interpolator_impl(vlen, skip, load_index));
    }

    /*
     * The private constructor
     */
    sinr_interpolator_impl::sinr_interpolator_impl(int vlen, int skip, const std::vector<int> &load_index)
      : gr::sync_block("sinr_interpolator",
              gr::io_signature::make(1, 1, sizeof( float ) * vlen * (skip-1)/ skip ),
              gr::io_signature::make(1, 1, sizeof( float ) * ( vlen )))
    	, d_vlen( vlen )
    	, d_skip( skip )
    	, d_load_index( load_index )
    {
    	  assert( d_vlen > 0 );
    }

    /*
     * Our virtual destructor.
     */
    sinr_interpolator_impl::~sinr_interpolator_impl()
    {
    }

    int
    sinr_interpolator_impl::work(int noutput_items,
			  gr_vector_const_void_star &input_items,
			  gr_vector_void_star &output_items)
    {
    	  const float *in = static_cast< const float* >( input_items[0] );
    	  float *out = static_cast< float* >( output_items[0] );

    	  const int partition_size = d_vlen/d_skip;


    	  for( int j = 0; j < noutput_items; ++j )
    	  {
    		  //std::cout<<"Partition size: "<<partition_size<<std::endl;
    	    for( int i = 0; i < partition_size ; ++i )
    	    {
    	    	int dsubc = d_load_index[i];

    	    	if( dsubc == 0 )
    	    	{
    	    		//memcpy( out, in, 1*sizeof( float ) );
    	    		out[dsubc] = in[dsubc];
    	    		out += 1; //in += dsubc;
    	    		memcpy( out, in, (d_skip - 1) * sizeof( float ) );
    	    		out += d_skip-1; in += d_skip-1;
    	    	      }
    	    	else
    	      {
    				//out[dsubc] = ((in[dsubc-i])+(in[dsubc-i-1]))/2.0;

    	    		//float x1 = in[dsubc-i];
    	    		//float x2 = in[dsubc-i-1];

    	    		//*(out) = (in[dsubc-i]+in[dsubc-i-1])/2.0;

    	    		*(out) = (*in + *(in-1))/2.0;

    	    		//float y0 = (*out);

    	    		//std::cout<<x1<<std::endl;
    	    		//std::cout<<x2<<std::endl;
    	    		//std::cout<<y0<<std::endl;

    	    		out += 1;
    	    		memcpy( out, in, (d_skip - 1) * sizeof( float ) );
    	    		out += d_skip-1; in += d_skip-1;
    	      }

    	    }

    	  }
    	  return noutput_items;
    }

  } /* namespace ofdm */
} /* namespace gr */

