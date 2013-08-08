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
#include "imgtransfer_testkanal_impl.h"

#include <iostream>
#include <algorithm>

#define DEBUG 0

namespace gr {
  namespace ofdm {

    imgtransfer_testkanal::sptr
    imgtransfer_testkanal::make()
    {
      return gnuradio::get_initial_sptr
        (new imgtransfer_testkanal_impl());
    }

    /*
     * The private constructor
     */
    imgtransfer_testkanal_impl::imgtransfer_testkanal_impl()
      : gr::block("imgtransfer_testkanal",
              gr::io_signature::make3(3, 3,
            	        sizeof(unsigned int ),
            	        sizeof(char), sizeof(int)),
              gr::io_signature::make(1, 1, sizeof(  char )))
    ,d_bitcount(0)
    ,d_pos(-1)
    ,d_frameno(0)
    ,d_flag(0)
    ,d_produced(0)
    {}

    /*
     * Our virtual destructor.
     */
    imgtransfer_testkanal_impl::~imgtransfer_testkanal_impl()
    {
    }

    void
    imgtransfer_testkanal_impl::forecast (int noutput_items, gr_vector_int &ninput_items_required)
    {
        /* <+forecast+> e.g. ninput_items_required[0] = noutput_items */
    }

    int
    imgtransfer_testkanal_impl::general_work (int noutput_items,
                       gr_vector_int &ninput_items,
                       gr_vector_const_void_star &input_items,
                       gr_vector_void_star &output_items)
    {
    	const unsigned int *in = static_cast< const unsigned int* >( input_items[0] );
    	  const  char *in_1 = static_cast< const  char* >( input_items[1] );
    	  const  int *in_2 = static_cast< const  int* >( input_items[2] );
    	  char *out = static_cast< char* >( output_items[0] );

    	  if ((ninput_items[0]==0)||(ninput_items[2]==0)) return 0;

    	  if (d_pos==-1)
    	  {
    	  	d_bitcount=in[0];
    	  	d_flag=in_2[0];
    	  	d_pos=0;
    	  	d_frameno++;
    	  }

    	  int ninput;
    	  if (d_flag==0)
    	  {
    	  	ninput = std::min(d_bitcount-d_pos,(unsigned int)std::min(ninput_items[1],noutput_items));
    	  	std::copy(in_1,in_1+ninput,out);
    	  	d_pos+=ninput;
    	  	consume(1,ninput);

    	  	if (d_pos==d_bitcount)
    	    {
    	      consume(0,1);
    	  	  consume(2,1);
    	  	  d_pos=-1;
    	    }

    	    return ninput;
    	  }
    	  else
    	  {
    	  	int nskip = std::min(d_bitcount-d_pos,(unsigned int)ninput_items[1]);
    	  	consume(1,nskip);
    	  	ninput=std::min(d_bitcount-d_produced+d_flag,(unsigned int)noutput_items);
    	  	d_pos+=nskip;
    	  	d_produced+=ninput;

    	    if ((d_pos==d_bitcount)&&(d_produced==(d_bitcount+d_flag)))
    	    {
    	   	  consume(0,1);
    	  	  consume(2,1);
    	  	  d_pos=-1;
    	  	  d_produced=0;
    	    }

    	    return ninput;
    	  }
    }

  } /* namespace ofdm */
} /* namespace gr */

