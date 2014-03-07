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
#include "limit_vff_impl.h"

#include <gnuradio/math.h>

//include <math.h>
#include <cmath>

namespace gr {
  namespace ofdm {

    limit_vff::sptr
    limit_vff::make(int vlen, float up_limit, float lo_limit)
    {
      return gnuradio::get_initial_sptr
        (new limit_vff_impl(vlen, up_limit, lo_limit));
    }

    /*
     * The private constructor
     */
    limit_vff_impl::limit_vff_impl(int vlen, float up_limit, float lo_limit)
      : gr::sync_block("limit_vff",
              gr::io_signature::make(1, 1, sizeof(float)*vlen),
              gr::io_signature::make(1, 1, sizeof(float)*vlen))
    	, d_up_limit(up_limit)
    	, d_lo_limit(lo_limit)
    	, d_vlen(vlen)
    {}

    /*
     * Our virtual destructor.
     */
    limit_vff_impl::~limit_vff_impl()
    {
    }

    int
    limit_vff_impl::work(int noutput_items,
			  gr_vector_const_void_star &input_items,
			  gr_vector_void_star &output_items)
    {
    	const float *in = static_cast<const float*>(input_items[0]);
    	  float *out = static_cast<float*>(output_items[0]);

    	  for(int i = 0; i < noutput_items*d_vlen; ++i){
    	    if(std::isnan(in[i])){
    	      out[i] = 0.0;
    	    }else if(in[i] > d_up_limit){
    	      out[i] = d_up_limit;
    	    }else if(in[i] < d_lo_limit){
    	      out[i] = -d_lo_limit;
    	    }else{
    	      out[i] = in[i];
    	    }
    	  }

    	  return noutput_items;
    }

  } /* namespace ofdm */
} /* namespace gr */

