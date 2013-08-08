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
#include "imgtransfer_src_impl.h"

#include <algorithm>
#include <iostream>

#define DEBUG 0
#define REPETITIONS 20

namespace gr {
  namespace ofdm {

    imgtransfer_src::sptr
    imgtransfer_src::make(std::string filename)
    {
      return gnuradio::get_initial_sptr
        (new imgtransfer_src_impl(filename));
    }

    /*
     * The private constructor
     */
    imgtransfer_src_impl::imgtransfer_src_impl(std::string filename)
      : gr::block("imgtransfer_src",
              gr::io_signature::make(1, 1, sizeof( unsigned int )),
              gr::io_signature::make( 1, 1, sizeof( char )))
      , d_filename( filename )
      , d_pos( -1 )
      , d_imgpos( 0 )
      , d_bitcounter(0)
      , d_bytecounter(0)
      , d_color(0)
      , d_bitcount( 0 )
    {
    	  d_bitmap.load(d_filename);
    	  d_buffer.resize(0);
    	  d_headerbuffer.resize(32*REPETITIONS);

    	  random_generator.load_from_file("random.txt");

    	  std::cout << "Initialized Imgtransfer Source\n";
    }

    /*
     * Our virtual destructor.
     */
    imgtransfer_src_impl::~imgtransfer_src_impl()
    {
    }

    void
    imgtransfer_src_impl::forecast (int noutput_items, gr_vector_int &ninput_items_required)
    {
        /* <+forecast+> e.g. ninput_items_required[0] = noutput_items */
    	ninput_items_required[0]=1;
    }

    int
    imgtransfer_src_impl::general_work (int noutput_items,
                       gr_vector_int &ninput_items,
                       gr_vector_const_void_star &input_items,
                       gr_vector_void_star &output_items)
    {
    	const unsigned int *in = static_cast< const unsigned int* >( input_items[0] );
    	  char *out = static_cast< char* >( output_items[0] );

    	  /* d_pos initialised with -1 */
    	  if (d_pos < 0)
    	  {
    	    if (ninput_items[0] == 0) return 0;
    	    /* read next Bitcount */
    	    d_bitcount = in[0];
    	    unsigned char d_imgpos_bits[32];
    	    int_to_bits(d_bitcounter/8, &d_imgpos_bits[0]);
    	    /* write header */
    	    for (int i=0; i< 32*REPETITIONS; ++i)
    	    {
    	      d_headerbuffer[i] = d_imgpos_bits[i%32];
    	    }
    	    d_pos = 0;
    	    random_generator.reset();
    	  }

    	  /* how many items are we going to give out this time:
    	   * as many items, as are suggested by the scheduler
    	   * or only the bits until the bitcount is full */
    	  unsigned int nout = (std::min)((unsigned int) noutput_items, d_bitcount-d_pos);

    	  /* initialize pointer to the bits which have to be given out */
    	  unsigned char* bits;
    	//  unsigned char temp[8];
    	  d_bitmap.get_bitpointer(0, &bits);
    	  /* for every element which has to be given out */
    	  for (unsigned int i = 0 ; i< nout ; ++i)
    	  {
    	    if ((unsigned)d_pos < d_headerbuffer.size())
    	    {
    	      out[i]=d_headerbuffer[d_pos++]^random_generator.rand_bit();
    	    }
    	    else
    	    {
    	      int pos = d_imgpos+d_pos-d_headerbuffer.size();
    	      pos = pos % (d_bitmap.get_width()*d_bitmap.get_height()*8*3);

    	      out[i]=bits[d_bitcounter]^random_generator.rand_bit();

    	      ++d_bitcounter;
    	      if (d_bitcounter>=d_bitmap.get_width()*d_bitmap.get_height()*3*8) d_bitcounter=0;
    	      ++d_pos;
    	    }
    	  }

    	  if ((unsigned)d_pos == d_bitcount)
    	  {
    	    d_imgpos+=d_bitcount-d_bitcount%8;
    	    d_bitcounter-=d_bitcount%8;
    	    d_imgpos%=(d_bitmap.get_width()*d_bitmap.get_height()*8*3);
    	    consume(0,1);
    	    d_pos=-1;
    	  }

    	  return nout;
    }

  } /* namespace ofdm */
} /* namespace gr */

