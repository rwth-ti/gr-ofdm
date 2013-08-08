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
#include "repetition_encoder_sb_impl.h"

#include <iostream>

#define DEBUG 0

namespace gr {
  namespace ofdm {

    repetition_encoder_sb::sptr
    repetition_encoder_sb::make(unsigned short input_bits, unsigned short repetitions, std::vector<int> whitener)
    {
      return gnuradio::get_initial_sptr
        (new repetition_encoder_sb_impl(input_bits, repetitions, whitener));
    }

    /*
     * The private constructor
     */
    repetition_encoder_sb_impl::repetition_encoder_sb_impl(unsigned short input_bits, unsigned short repetitions, std::vector<int> whitener)
      : gr::sync_interpolator("repetition_encoder_sb",
              gr::io_signature::make(1, 1, sizeof(short)),
              gr::io_signature::make(1, 1, sizeof(char)), input_bits * repetitions)
    	, d_input_bits(input_bits)
    	, d_repetitions(repetitions)
    	, d_whitener(whitener)
    {
    	  for(std::vector<int>::const_iterator iter = d_whitener.begin(); iter != d_whitener.end(); ++iter){
    	    assert(*iter == 0 || *iter == 1);
    	  }

    	  if(DEBUG)
    	    std::cout << "[rep enc " << unique_id() << "] input_bits=" << input_bits
    	              << " repetitions=" << repetitions << std::endl;
    }

    /*
     * Our virtual destructor.
     */
    repetition_encoder_sb_impl::~repetition_encoder_sb_impl()
    {
    }

    int
    repetition_encoder_sb_impl::work(int noutput_items,
			  gr_vector_const_void_star &input_items,
			  gr_vector_void_star &output_items)
    {
    	  const short *in = static_cast<const short*>(input_items[0]);
    	  char *out = static_cast<char*>(output_items[0]);
    	  unsigned int output_pos = 0;

    	  if(DEBUG)
    	    std::cout << "[rep enc " << unique_id() << "] entered, "
    	              << "nout=" << noutput_items << std::endl;

    	  //iterate over all input items
    	  for (int item = 0; item < (noutput_items / (d_input_bits * d_repetitions)); item++)
    	  {
    		  //repeat the input d_repetitions times
    		  for (unsigned short reps = 0; reps < d_repetitions; reps++)
    		  {
    			  //and write it bit by bit to the output
    			  for (unsigned short bit = 0; bit < d_input_bits; bit++)
    			  {
    				  out[output_pos++] = ((char)(in[item] >> bit)) & 1
    				                      ^ d_whitener[reps*d_input_bits+bit];
    			  }
    		  }
    	  }

    	  if(DEBUG)
    	    std::cout << "[rep enc] leave, produce " << output_pos << " items"
    	              << std::endl;

    	  return output_pos;
    }

  } /* namespace ofdm */
} /* namespace gr */

