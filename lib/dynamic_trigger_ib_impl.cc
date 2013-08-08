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
#include "dynamic_trigger_ib_impl.h"

#include <cstring>


#include <iostream>
#include <algorithm>

namespace gr {
  namespace ofdm {

    dynamic_trigger_ib::sptr
    dynamic_trigger_ib::make(bool first_or_last)
    {
      return gnuradio::get_initial_sptr
        (new dynamic_trigger_ib_impl(first_or_last));
    }

    /*
     * The private constructor
     */
    dynamic_trigger_ib_impl::dynamic_trigger_ib_impl(bool first_or_last)
      : gr::block("dynamic_trigger_ib",
              gr::io_signature::make(1, 1, sizeof(unsigned int)),
              gr::io_signature::make(1, 1, sizeof(char)))
    	, d_first_or_last(first_or_last)
    	, d_produced(0)
    {}

    /*
     * Our virtual destructor.
     */
    dynamic_trigger_ib_impl::~dynamic_trigger_ib_impl()
    {
    }

    void
    dynamic_trigger_ib_impl::forecast (int noutput_items, gr_vector_int &ninput_items_required)
    {
        /* <+forecast+> e.g. ninput_items_required[0] = noutput_items */
    	ninput_items_required[0] = 1;
    }

    int
    dynamic_trigger_ib_impl::noutput_forecast( gr_vector_int &ninput_items,
        int available_space, int max_items_avail, std::vector<bool> &input_done )
    {

      // check if we are done or if we can't produce anything
      // else with at least one input item, we possibly use the whole
      // available output space.

      if( ninput_items[0] == 0 && input_done[0] )
        return -1;

      if( ninput_items[0] == 0 )
        return 0;

      return available_space;

    }

    int
    dynamic_trigger_ib_impl::general_work (int noutput_items,
                       gr_vector_int &ninput_items,
                       gr_vector_const_void_star &input_items,
                       gr_vector_void_star &output_items)
    {
    	const unsigned int *in = static_cast<const unsigned int*>(input_items[0]);
    	  char *out = static_cast<char*>(output_items[0]);

    	  int ninput = ninput_items[0];
    	  int noutput = noutput_items;

    	  memset(out,0,noutput_items*sizeof(char));

    	  //std::cout << "[dyn.trig] " << in[0] << std::endl;

    	  while( noutput > 0 && ninput > 0 ) {
    	    if(in[0] == 0){

    	      std::cerr << "warning: bitcount = 0" << std::endl;
    	      consume_each(1);
    	      --ninput;
    	      ++in;

    	    } else if(in[0] > d_produced){

    	      unsigned int n = std::min(static_cast<unsigned int>(noutput),
    	          in[0]-d_produced);
    	      assert(n > 0);

    	      if(d_first_or_last && d_produced == 0){ // first
    	        out[0] = 1;
    	      }

    	      d_produced += n;

    	      if(d_produced == in[0]){
    	        d_produced = 0;
    	        consume_each(1);
    	        //std::cout << "[dyn trig] consume, new " << in[0] << std::endl;
    	        --ninput;
    	        ++in;

    	        if(!d_first_or_last)
    	          out[n-1] = 1;
    	      }

    	      noutput -= n;
    	      out += n;

    	    } else {

    	      assert(false && "[dyn.trig] failed, in <= d_produced && != 0");

    	    }
    	  } // while (..)

    	  //std::cout << "[dyn.trig] produce " << noutput_items-noutput << std::endl;

    	  return noutput_items-noutput;
    }

  } /* namespace ofdm */
} /* namespace gr */

