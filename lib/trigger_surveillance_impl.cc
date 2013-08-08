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
#include "trigger_surveillance_impl.h"

#include <iostream>
#include <cmath>

namespace gr {
  namespace ofdm {

    trigger_surveillance::sptr
    trigger_surveillance::make(int ideal_distance, int max_shift)
    {
      return gnuradio::get_initial_sptr
        (new trigger_surveillance_impl(ideal_distance, max_shift));
    }

    /*
     * The private constructor
     */
    trigger_surveillance_impl::trigger_surveillance_impl(int ideal_distance, int max_shift)
      : gr::sync_block("trigger_surveillance",
              gr::io_signature::make(1, 1, sizeof(char)),
              gr::io_signature::make(0, 0, 0))
    	, d_ideal_distance(ideal_distance)
        , d_max_shift(max_shift)
    	, d_dist(0)
    	, d_lost(0)
    	, d_first(true)
    {}

    /*
     * Our virtual destructor.
     */
    trigger_surveillance_impl::~trigger_surveillance_impl()
    {
    }

    int
    trigger_surveillance_impl::work(int noutput_items,
			  gr_vector_const_void_star &input_items,
			  gr_vector_void_star &output_items)
    {
    	  const char *in = static_cast<const char*>(input_items[0]);

    	  for(int i = 0; i < noutput_items; ++i, ++d_dist){
    	    if(in[i] != 1){
    	      if(!d_first){
    	        if(d_dist <= d_ideal_distance+d_max_shift){
    	          continue;
    	        }else{
    	          ++d_lost;
    	          d_dist = d_dist-d_ideal_distance;
    	          //std::cout << "Missed one trigger point" << std::endl;
    	          std::cout << "X"; // << std::flush;
    	        }
    	      }
    	    }else{
    	      if(d_first){
    	        d_first = false;
    	      } else {
    	        long long x = d_dist-d_ideal_distance;
    	        if(std::abs(x) > static_cast<long long>(d_max_shift)){
    	          ++d_lost;
    	          //std::cout << "Shifted trigger, shift of " << x << std::endl;
    	          std::cout << "S"; // << std::flush;
    	        }
    	      }

    	      d_dist = 0;
    	    }
    	  }

    	  return noutput_items;
    }

  } /* namespace ofdm */
} /* namespace gr */

