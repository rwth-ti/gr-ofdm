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
#include "reference_data_source_ib_impl.h"

#include <algorithm>
#include <iostream>

#define DEBUG 0

namespace gr {
  namespace ofdm {

    reference_data_source_ib::sptr
    reference_data_source_ib::make(const std::vector<int> &ref_data)
    {
      return gnuradio::get_initial_sptr
        (new reference_data_source_ib_impl(ref_data));
    }

    /*
     * The private constructor
     */
    reference_data_source_ib_impl::reference_data_source_ib_impl(const std::vector<int> &ref_data)
      : gr::block("reference_data_source_ib",
              gr::io_signature::make(1, 1, sizeof(unsigned int)),
              gr::io_signature::make(1, 1, sizeof(char)))
    	, d_produced(0)
    {
      // unpack byte array
      d_ref_data.resize(ref_data.size()*8*10);
      for(std::vector<char>::size_type i = 0; i < ref_data.size()*8; ++i){
        std::vector<char>::size_type pos = i / 8, bpos = i % 8;
        std::vector<char>::value_type b = ((ref_data[pos] & 0xFF) >> bpos) & 0x01;
        d_ref_data[i] = b;
      }
      for(int i = 1; i < 10; ++i )
      {
        for( int j = 0; j < ref_data.size()*8; ++j )
        {
          d_ref_data[i*ref_data.size()*8 + j] = d_ref_data[j];
        }
      }
      // FIXME: generate longer random data
      d_bpos = d_ref_data.begin();
    }

    /*
     * Our virtual destructor.
     */
    reference_data_source_ib_impl::~reference_data_source_ib_impl()
    {
    }

    void
    reference_data_source_ib_impl::forecast (int noutput_items, gr_vector_int &ninput_items_required)
    {
        /* <+forecast+> e.g. ninput_items_required[0] = noutput_items */
    	ninput_items_required[0] = 1;
    }

    int
    reference_data_source_ib_impl::general_work (int noutput_items,
                       gr_vector_int &ninput_items,
                       gr_vector_const_void_star &input_items,
                       gr_vector_void_star &output_items)
    {
    	  const unsigned int *in = static_cast<const unsigned int*>(input_items[0]);
    	  char *out = static_cast<char*>(output_items[0]);

    	  if(DEBUG)
    	    std::cout << "[dref.src " << unique_id() << "] entered, state "
    	              << "nin=" << ninput_items[0] << " nout=" << noutput_items
    	              << " d_produced=" << d_produced
    	              << " in[0]=" << in[0]
    	              << std::endl;

    	  if(in[0] == 0){

    	      std::cerr << "warning: bitcount = 0" << std::endl;
    	      consume_each(1);
    	      return 0;

    	  } else if(in[0] > d_produced){

    	    assert( in[0] <= d_ref_data.size() );

    	    std::vector<char>::size_type p = std::min(
    	        static_cast<std::vector<char>::size_type>(in[0]-d_produced),
    	        static_cast<std::vector<char>::size_type>(noutput_items));

    	    if(DEBUG)
    	      std::cout << "produce " << p << " items" << std::endl;

    	    std::copy(d_bpos, d_bpos+p, out);
    	    d_bpos += p;
    	    d_produced += p;

    	    if(d_produced >= in[0]){
    	      d_bpos = d_ref_data.begin();
    	      d_produced = 0;
    	      consume_each(1);

    	      if(DEBUG)
    	        std::cout << "consume input value" << std::endl;
    	    }

    	    return p;

    	  }

    	  assert(false && "should never get here");
    	  return -1;
    }

  } /* namespace ofdm */
} /* namespace gr */

