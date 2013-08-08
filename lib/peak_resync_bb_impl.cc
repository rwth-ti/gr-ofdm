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
#include "peak_resync_bb_impl.h"

#include <algorithm>
#include <iostream>

#define DEBUG(x)

namespace gr {
  namespace ofdm {

    peak_resync_bb::sptr
    peak_resync_bb::make(bool replace)
    {
      return gnuradio::get_initial_sptr
        (new peak_resync_bb_impl(replace));
    }

    /*
     * The private constructor
     */
    peak_resync_bb_impl::peak_resync_bb_impl(bool replace)
      : gr::block("peak_resync_bb",
              gr::io_signature::make(2, 2, sizeof(char)),
              gr::io_signature::make(1, 1, sizeof(char)))
    	, d_replace(replace)
    	, d_resync(0)
    {}

    /*
     * Our virtual destructor.
     */
    peak_resync_bb_impl::~peak_resync_bb_impl()
    {
    }

    void
    peak_resync_bb_impl::forecast (int noutput_items, gr_vector_int &ninput_items_required)
    {
        /* <+forecast+> e.g. ninput_items_required[0] = noutput_items */
    	ninput_items_required[0] = noutput_items;
    	ninput_items_required[1] = d_resync;
    }

    int
    peak_resync_bb_impl::general_work (int noutput_items,
                       gr_vector_int &ninput_items,
                       gr_vector_const_void_star &input_items,
                       gr_vector_void_star &output_items)
    {
    		const char *in = static_cast<const char*>(input_items[0]);
    		const char *in_2 = static_cast<const char*>(input_items[1]);
    		char *out = static_cast<char*>(output_items[0]);

    		if(d_resync > 0 && ninput_items[1] == 0)
    			/* we need at least one item from the second stream */
    			return 0;

    		const int nitems = std::min(ninput_items[0], noutput_items);
    		int nitems_2 = ninput_items[1];

    		int i, j;
    		for(i = 0, j = 0; i < nitems; ++i) {
    			if(in[i] == 1) {
    				/* we got a peak */
    				if(nitems_2 > 0) {
    					/* we can consume one more item from the second stream */
    					out[i] = d_replace ? in_2[j++] : in [i];
    					d_resync = 0;
    					--nitems_2;
    				} else {
    					/* there are no items from the second stream available, so we wait */
    					if(i > 0)
    						consume(0, i); /* consume up to the item before the peak */
    					if(j > 0)
    						consume(1, j);

    					d_resync = 1;
    					DEBUG(std::cout << "waiting for second stream, passed up " << i << " and consumed " << j << std::endl;)
    					return i;
    				}
    			} else {
    				out[i] = in[i];
    			}
    		}

    		DEBUG(std::cout << "consumed " << i << " and " << j << std::endl;)

    		/* tell the system what we consumed */
    		if(i > 0)
    			consume(0, i);
    		if(j > 0)
    			consume(1, j);

    		return i;
    }

  } /* namespace ofdm */
} /* namespace gr */

