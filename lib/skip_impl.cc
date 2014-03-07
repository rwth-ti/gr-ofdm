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
#include "skip_impl.h"

#include <cstring>
#include <algorithm>
#include <iostream>

namespace gr {
  namespace ofdm {

    skip::sptr
    skip::make(std::size_t itemsize, unsigned int blocklen)
    {
      return gnuradio::get_initial_sptr
        (new skip_impl(itemsize, blocklen));
    }

    /*
     * The private constructor
     */
    skip_impl::skip_impl(std::size_t itemsize, unsigned int blocklen)
      : gr::block("skip",
              gr::io_signature::make2 (2, 2, itemsize, sizeof(char)),
              gr::io_signature::make2 (1, 2, itemsize, sizeof(char)))
    	, d_itemsize(itemsize)
    	, d_blocklen(blocklen)
    	, d_item(blocklen)
    	, d_skip(0)
    	, d_items(blocklen,false)
    	, d_first_item(blocklen,false)
    {
    	  d_first_item[0] = true;

    	  //set_output_multiple(d_blocklen);
    	  set_relative_rate(1.0);
    	  set_fixed_rate(true);
    }

    /*
     * Our virtual destructor.
     */
    skip_impl::~skip_impl()
    {
    }

    void
    skip_impl::forecast (int noutput_items, gr_vector_int &ninput_items_required)
    {
        /* <+forecast+> e.g. ninput_items_required[0] = noutput_items */
    	  int nreqd = fixed_rate_noutput_to_ninput(noutput_items);
    	  for(unsigned int i = 0; i < ninput_items_required.size(); ++i){
    	    ninput_items_required[i] = nreqd;
    	  }
    }

    int
    skip_impl::noutput_forecast( gr_vector_int &ninput_items,
        int available_space, int max_items_avail, std::vector<bool> &input_done )
    {

      if( ninput_items[0] < (d_blocklen-d_skip) && input_done[0] )
        return -1;

      if( ninput_items[1] < (d_blocklen-d_skip) && input_done[1] )
        return -1;


      if( max_items_avail == 0 )
        return 0;

      return available_space;

    }

    int
    skip_impl::general_work (int noutput_items,
                       gr_vector_int &ninput_items,
                       gr_vector_const_void_star &input_items,
                       gr_vector_void_star &output_items)
    {
    	const char *in = static_cast<const char*>(input_items[0]);
    	  const char *trigger = static_cast<const char*>(input_items[1]);
    	  char *out = static_cast<char*>(output_items[0]);

    	  char *filt_trigger = 0;

    	  if(output_items.size() > 1) {
    	    filt_trigger = static_cast<char*>(output_items[1]);
    	    memset(filt_trigger, 0, noutput_items);
    	  }

    	  int i = 0;
    	  int produced = 0;

    	  int i_max = std::min( ninput_items[0], ninput_items[1] );

    	  while( produced < noutput_items && i < i_max )
    	  {
    	    if( trigger[i] == 1 )
    	    { // reset
    	      d_item = 0;
    	    }

    	    if( d_item < d_items.size() )
    	    {
    	      if( d_items[d_item] ) // skip flag set
    	      {
    		++d_item;
    		++i;
    		continue;
    	      }

    	      if(filt_trigger != 0)
    	      {
    	        if( d_first_item[d_item])
    	        {
    	  	  *filt_trigger = 1;
    	        }
    	        ++filt_trigger;
    	      }

    	      ++d_item;
    	    }


    	    // skip flag not set
    	    memcpy( out, in + i * d_itemsize, d_itemsize );
    	    out += d_itemsize;
    	    ++produced;

    	    ++i;
    	  } // for-loop

    	  consume_each( i );
    	  return produced;
    }


    void
    skip_impl::skip_call(unsigned int no)
    {
      assert(no < d_blocklen);

      d_items[no] = true;
      ++d_skip;

      assert(d_skip < d_blocklen);

    //  set_output_multiple(d_blocklen-d_skip);
      set_relative_rate(static_cast<float>(d_blocklen-d_skip)/d_blocklen);


      bool first = true;
      for(unsigned int i = 0; i < d_first_item.size(); ++i) {
        d_first_item[i] = false;
        if(!d_items[i]){
          d_first_item[i] = first;
          first = false;
        }
      }
    }

    int skip_impl::fixed_rate_noutput_to_ninput(int noutput_items)
    {
      return noutput_items * d_blocklen/(d_blocklen-d_skip);
    }

    int skip_impl::fixed_rate_ninput_to_noutput(int ninput_items)
    {
      return std::max(0U,ninput_items * (d_blocklen-d_skip)/d_blocklen);
    }


  } /* namespace ofdm */
} /* namespace gr */

