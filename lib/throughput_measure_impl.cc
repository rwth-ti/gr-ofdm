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
#include "throughput_measure_impl.h"

#include <cmath>
#ifdef HAVE_TIME_H
#include <time.h>
#endif

#include <string.h>

#include <iostream>
#include <algorithm>

namespace gr {
  namespace ofdm {

    throughput_measure::sptr
    throughput_measure::make(int itemsize)
    {
      return gnuradio::get_initial_sptr
        (new throughput_measure_impl(itemsize));
    }

    /*
     * The private constructor
     */
    throughput_measure_impl::throughput_measure_impl(int itemsize)
      : gr::sync_block("throughput_measure",
              gr::io_signature::make(1, 1, itemsize),
              gr::io_signature::make(1, 1, itemsize))
    	, d_itemsize(itemsize)
    	, d_total_samples(0)
    	, d_init(false)
    	, d_min(-1)
    	, d_max(0)
    	, d_avg(0)
    {
		#ifdef HAVE_GETTIMEOFDAY
		  gettimeofday(&d_start, 0);
		#endif
    }

    /*
     * Our virtual destructor.
     */
    throughput_measure_impl::~throughput_measure_impl()
    {
    }

    int
    throughput_measure_impl::work(int noutput_items,
			  gr_vector_const_void_star &input_items,
			  gr_vector_void_star &output_items)
    {
    	  const char *in = static_cast<const char*>(input_items[0]);
    	  char *out = static_cast<char*>(output_items[0]);

    	#if defined(HAVE_GETTIMEOFDAY)
    	  if(!d_init) {
    	    gettimeofday(&d_start, 0);
    	    d_init=true;
    	  } else {
    	    struct timeval now;
    	    gettimeofday(&now, 0);
    	    long t_usec = now.tv_usec - d_start.tv_usec;
    	    long t_sec  = now.tv_sec - d_start.tv_sec;
    	    double t = (double)t_sec + (double)t_usec * 1e-6;
    	    if (t < 1e-6)    // avoid unlikely divide by zero
    	      t = 1e-6;

    	    double actual_samples_per_sec = d_total_samples / t;

    	    d_avg = 0.995 * d_avg + 0.005 * actual_samples_per_sec;
    	    if(d_min < 0)
    	      d_min = actual_samples_per_sec;
    	    else
    	      d_min = std::min(d_min,actual_samples_per_sec);
    	    d_max = std::max(d_max,actual_samples_per_sec);

    	    //std::cout << "samplerate " << actual_samples_per_sec << "/s" << std::endl;
    	  }
    	#endif

    	  d_total_samples += noutput_items;
    	  memcpy(out, in, noutput_items * d_itemsize);

    	  return noutput_items;
    }

  } /* namespace ofdm */
} /* namespace gr */

