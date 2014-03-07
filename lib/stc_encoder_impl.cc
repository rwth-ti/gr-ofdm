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
#include "stc_encoder_impl.h"

#include <iostream>
#include <algorithm>

#define DEBUG 0

namespace gr {
  namespace ofdm {

    stc_encoder::sptr
    stc_encoder::make( int vlen, int num_symbols, std::vector< int > const &pilot_subcarriers )
    {
      return gnuradio::get_initial_sptr
        (new stc_encoder_impl(vlen, num_symbols, pilot_subcarriers));
    }

    /*
     * The private constructor
     */
    stc_encoder_impl::stc_encoder_impl( int vlen, int num_symbols, std::vector< int > const &pilot_subcarriers )
      : gr::sync_block("stc_encoder",
              gr::io_signature::make(1, 1, sizeof( gr_complex ) * vlen ),	// ofdm_blocks
              gr::io_signature::make2(2, 2,
            	        sizeof( gr_complex ) * vlen,            // encoded ofdm_blocks
            	        sizeof( gr_complex ) * vlen))			// encoded ofdm_blocks2
		, d_vlen( vlen )
		, d_num_symbols( num_symbols )
		, d_pcount( pilot_subcarriers.size() )
		, d_pilot_tone(pilot_subcarriers)
    {
    	  assert( ( vlen % 2 ) == 0 ); // alignment 16 byte
    	  //init_stc_encoder( pilot_subcarriers );
    }

    /*
     * Our virtual destructor.
     */
    stc_encoder_impl::~stc_encoder_impl()
    {
    }

    int
    stc_encoder_impl::work(int noutput_items,
			  gr_vector_const_void_star &input_items,
			  gr_vector_void_star &output_items)
    {
    	  gr_complex const * ofdm_blocks = static_cast< gr_complex const * >( input_items[0] );
    	  gr_complex * out = static_cast< gr_complex * >( output_items[0] );
    	  gr_complex * out2 = static_cast< gr_complex * >( output_items[1] );

    	  int k = 0;
    	  int kk = 0;
    	  gr_complex norm_c = sqrt(2);
    	  gr_complex null = 0.0;

    	  for( int j = 0; j < noutput_items*d_vlen; ++j )
    	  {
    	      //std::cout << "LMS: k is " << k << std::endl;
    	      //std::cout << "LMS: pilot is " << d_pilot_tone[k] << std::endl;
    	//      std::cout << "LMS: pilot is " << d_pilot_tone[0] << std::endl;
    	//      std::cout << "LMS: pilot is " << d_pilot_tone[1] << std::endl;
    	//      std::cout << "LMS: pilot is " << d_pilot_tone[7] << std::endl;
    	      if (j == d_pilot_tone[k] + kk*d_vlen || j == d_pilot_tone[k]+1+ kk*d_vlen)
    	        {
    	          //std::cout << "LMS: pilot is " << d_pilot_tone[k] << std::endl;
    	          if( j % 2 == 0 )
    	        {
    	          out[j] =  norm_c*ofdm_blocks[j];
    	          out2[j] = 0.0;
    	          //std::cout << "LMS: out2 is " << out[j] << std::endl;
    	          //std::cout << "LMS: out2 is " << out2[j] << std::endl;
    	        } else {
    	            out[j] = - norm_c*std::conj( ofdm_blocks[j] );
    	            out2[j] = null;
    	            //k++;
    	           if (k == d_pilot_tone.size()-1)
    	                              {k=0;
    	                              kk++;}
    	                          else
    	                              k++;
    	        }

    	        }
    	      else
    	      {
    	          if( j % 2 == 0 )
    	              {
    	                out[j] = ofdm_blocks[j];
    	                out2[j] = ofdm_blocks[j+1];
    	              } else {
    	                  out[j] = - std::conj( ofdm_blocks[j] );
    	                  out2[j] = std::conj( ofdm_blocks[j-1] );
    	              }
    	      }
    	  }

    	  return noutput_items;
    }

  } /* namespace ofdm */
} /* namespace gr */

