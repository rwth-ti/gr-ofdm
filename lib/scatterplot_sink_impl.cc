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
#include "scatterplot_sink_impl.h"

#include <iostream>

#define DEBUG 0

namespace gr {
  namespace ofdm {

    scatterplot_sink::sptr
    scatterplot_sink::make(int vlen, std::string shm_id)
    {
      return gnuradio::get_initial_sptr
        (new scatterplot_sink_impl(vlen, shm_id));
    }

    /*
     * The private constructor
     */
    scatterplot_sink_impl::scatterplot_sink_impl(int vlen, std::string shm_id)
      : gr::block("scatterplot_sink",
              gr::io_signature::make3( 3, 3, sizeof(gr_complex)
            	      * vlen, sizeof(char) * vlen, sizeof(char) ),
              gr::io_signature::make(0,0,0))
    	, d_vlen( vlen )
    {
    	  if( DEBUG > 0 )
    	    std::cout << "SCATTERPLOT_SINK initializes IPC\n";
    	  d_shm = c_interprocess::create( d_vlen, 64, shm_id ); //64 Buffers of length d_vlen
    	  temp_buffer = new c_point[d_vlen];
    	  std::cout << "finished init\n";
    }

    /*
     * Our virtual destructor.
     */
    scatterplot_sink_impl::~scatterplot_sink_impl()
    {
    }

    void
    scatterplot_sink_impl::forecast (int noutput_items, gr_vector_int &ninput_items_required)
    {
        /* <+forecast+> e.g. ninput_items_required[0] = noutput_items */
    	  ninput_items_required[0] = 1;
    	  ninput_items_required[1] = 1;
    	  ninput_items_required[2] = 1;
    }

    int
    scatterplot_sink_impl::general_work (int noutput_items,
                       gr_vector_int &ninput_items,
                       gr_vector_const_void_star &input_items,
                       gr_vector_void_star &output_items)
    {
    	  const gr_complex * sym_in =
    	      static_cast< const gr_complex* > ( input_items[0] );
    	  const char * cv_in = static_cast< const char* > ( input_items[1] );
    	  const char * trig = static_cast< const char* > ( input_items[2] );

    	  int n_min = std::min( ninput_items[0], ninput_items[2] );
    	  int n_cv = ninput_items[1];

    	  int cv_counter = 0;

    	  if( DEBUG > 0 )
    	    std::cout << "SCATTERPLOT_SINK works... n_min=" << n_min << "\n";

    	  int k;
    	  for( k = 0; k < n_min; ++k )
    	  {
    	    if( trig[k] == 0 ) //use old cv
    	    {
    	      for( int i = 0; i < d_vlen; ++i )
    	      {
    	        temp_buffer[i].x = sym_in->real();
    	        temp_buffer[i].y = sym_in->imag();
    	        if( DEBUG > 0 )
    	          std::cout << "(" << temp_buffer[i].x << "," << temp_buffer[i].y
    	              << ")";
    	        sym_in++ ;
    	      }
    	      d_shm->add_points( temp_buffer, NULL );
    	    }
    	    else //use new cv
    	    {
    	      if( n_cv > 0 ) // there is a cv vector left
    	      {
    	        for( int i = 0; i < d_vlen; ++i )
    	        {
    	          temp_buffer[i].x = sym_in->real();
    	          temp_buffer[i].y = sym_in->imag();
    	          if( DEBUG > 0 )
    	            std::cout << "(" << temp_buffer[i].x << "," << temp_buffer[i].y
    	                << ")";
    	          sym_in++ ;
    	        }
    	        d_shm->add_points( temp_buffer, &cv_in[cv_counter * d_vlen] );
    	        ++cv_counter;
    	        --n_cv;
    	      }
    	      else // there is no cv_vector left
    	      {
    	        break;
    	      }
    	    }
    	  }

    	  if( DEBUG > 0 )
    	    std::cout << "\n";

    	  consume( 0, k );
    	  consume( 1, cv_counter );
    	  consume( 2, k );

    	  return 0;
    }

  } /* namespace ofdm */
} /* namespace gr */

