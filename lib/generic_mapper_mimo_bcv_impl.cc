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
#include "generic_mapper_mimo_bcv_impl.h"

#include <string.h>

#include <vector>
#include <stdexcept>
#include <iostream>
#include <complex>

#define DEBUG 0

namespace gr {
  namespace ofdm {

    generic_mapper_mimo_bcv::sptr
    generic_mapper_mimo_bcv::make(int vlen, bool coding)
    {
      return gnuradio::get_initial_sptr
        (new generic_mapper_mimo_bcv_impl(vlen, coding));
    }

    /*
     * The private constructor
     */
    generic_mapper_mimo_bcv_impl::generic_mapper_mimo_bcv_impl(int vlen, bool coding)
      : gr::block("generic_mapper_mimo_bcv",
              gr::io_signature::make3(3, 3, sizeof(char),                 // bit stream
                      sizeof(char)*vlen,            // bitmap
                      sizeof(char) ),               // trigger
              gr::io_signature::make(2, 2, sizeof(gr_complex)*vlen ) )  // ofdm blocks
    	, d_vlen( vlen )
    	, d_coding( coding )
    	, d_need_bits( 0 )
    	, mod( new ofdmi_modem() )
    	, mod_2( new ofdmi_modem() )
    	, d_need_bitmap( 1 )
    	, d_bitmap( new char[vlen] )
    {
    	for( int i = 0; i < vlen; ++i ){
    	    d_bitmap[i] = 0;
    	  }

    	  if(DEBUG)
    	    std::cout << "[mapper " << unique_id() << "] vlen=" << vlen << " coding=" << d_coding << std::endl;
    }

    static inline int
    calc_bit_amount( const char* cv, const int& vlen, bool coding )
    {
      int bits_per_symbol = 0;
      int bits_per_mode[9] = {1,2,2,4,4,6,6,6,8};

      if(coding)
      {
    	  for(int i = 0; i < vlen; ++i) {
    		if(cv[i] > 9)
    		  throw std::out_of_range("MAPPER: Mode higher than 9 not supported");
    		if(cv[i] < 0)
    		  throw std::out_of_range("MAPPER: Cannot allocate less than zero bits");
    		if(cv[i] > 0)
    			bits_per_symbol += bits_per_mode[cv[i]-1];
    	  }
      }
      else
      {
    	  for(int i = 0; i < vlen; ++i) {
    		if(cv[i] > 8)
    		  throw std::out_of_range("MAPPER: More than 8 bits per symbol not supported");
    		if(cv[i] < 0)
    		  throw std::out_of_range("MAPPER: Cannot allocate less than zero bits");
    		bits_per_symbol += cv[i];
    	  }
      }
      std::cout << "bits_per_symbol = " << bits_per_symbol << std::endl;
      return bits_per_symbol;
    }

    static inline int
    calc_bit_amount_2( const char* cv, const int& vlen, bool coding )
    {
      int bits_per_symbol = 0;
      int bits_per_mode[9] = {1,2,2,4,4,6,6,6,8};

      if(coding)
      {
    	  for(int i = 0; i < vlen; ++i) {
    		if(cv[i] > 9)
    		  throw std::out_of_range("MAPPER: Mode higher than 9 not supported");
    		if(cv[i] < 0)
    		  throw std::out_of_range("MAPPER: Cannot allocate less than zero bits");
    		if(cv[i] > 0)
    			bits_per_symbol += bits_per_mode[cv[i]-1];
    	  }
      }
      else
      {
    	  for(int i = 0; i < vlen; ++i) {
    		if(cv[i] > 8)
    		  throw std::out_of_range("MAPPER: More than 8 bits per symbol not supported");
    		if(cv[i] < 0)
    		  throw std::out_of_range("MAPPER: Cannot allocate less than zero bits");
    		bits_per_symbol += cv[i];
    	  }
      }
    //  bits_per_symbol *= 2;
      std::cout << "bits_per_symbol_2 = " << bits_per_symbol << std::endl;
      return bits_per_symbol;
    }

    /*
     * Our virtual destructor.
     */
    generic_mapper_mimo_bcv_impl::~generic_mapper_mimo_bcv_impl()
    {
    }

    void
    generic_mapper_mimo_bcv_impl::forecast (int noutput_items, gr_vector_int &ninput_items_required)
    {
        /* <+forecast+> e.g. ninput_items_required[0] = noutput_items */ninput_items_required[0] = d_need_bits;
        ninput_items_required[1] = d_need_bitmap;
        ninput_items_required[2] = noutput_items;
        std::cout << "\treq[0] = " << ninput_items_required[0] << "\treq[1] = " << ninput_items_required[1] << "\treq[2] = " << ninput_items_required[2] << std::endl;
    }

    int
    generic_mapper_mimo_bcv_impl::noutput_forecast( gr_vector_int &ninput_items,
        int available_space, int max_items_avail, std::vector<bool> &input_done )
    {

      if( ninput_items[0] < d_need_bits ){
        if( input_done[0] ){
          return -1;
        }

        return 0;
      }

      if( ninput_items[1] < d_need_bitmap ){
        if( input_done[1] ){
          return -1;
        }

        return 0;
      }

      if( ninput_items[2] == 0 && input_done[2] ){
        return -1;
      }

      return std::min( available_space, ninput_items[2] );

    }

    int
    generic_mapper_mimo_bcv_impl::general_work (int noutput_items,
                       gr_vector_int &ninput_items,
                       gr_vector_const_void_star &input_items,
                       gr_vector_void_star &output_items)
    {
    	const char *data = static_cast<const char*>(input_items[0]);
    	  const char *cv = static_cast<const char*>(input_items[1]);
    	  const char *trig = static_cast<const char*>(input_items[2]);

    	  gr_complex *blk = static_cast<gr_complex*>(output_items[0]);
    	  gr_complex *blk_2 = static_cast<gr_complex*>(output_items[1]);

    	  int n_bits = ninput_items[0];
    	  int n_cv = ninput_items[1];
    	  int n_trig = ninput_items[2];
    	  int nout = noutput_items;

    	  std::cout << "\tn_bits = " << n_bits
    			    << "\n\tn_cv = " << n_cv
    			    << "\n\tn_trig = " << n_trig
    			    << "\n\tnout = " << nout << std::endl;

    	  int n_min = std::min( nout, n_trig );


    	  if(DEBUG)
    	    std::cout << "[mapper " << unique_id() << "] entered, state is "
    	              << "n_bits=" << n_bits << " n_cv=" << n_cv
    	              << " n_trig=" << n_trig << " nout=" << nout
    	              << " d_need_bits=" << d_need_bits
    	              << " d_need_bitmap=" << d_need_bitmap << std::endl;

    	  bool copy = false;
    	  const char *map = d_bitmap.get();

    	  for( int i = 0; i < n_min; ++i, ++trig ){
    	    if( *trig == 1 )
    	    {
    	      if( n_cv > 0 )
    	      {
    	        // update bitmap buffer
    	        map = cv;

    	        d_need_bits = calc_bit_amount( map, d_vlen, d_coding );

    	        // if not enough input, won't consume trigger, therefore
    	        // don't consume bitmap item
    	        if( n_bits < d_need_bits ){
    	          d_need_bitmap = 1;
    	          break;
    	        }

    	        copy = true;
    	        d_need_bitmap = 0;

    	        --n_cv; cv += d_vlen;
    	        consume(1, 1);
    	        std::cout << "consumed(1, 1) for *trig == 1" << std::endl;

    	        if(DEBUG)
    	          std::cout << "Consume 1 bitmap item, leave " << n_cv << " items"
    	                    << " and need " << d_need_bits << " bits while "
    	                    << n_bits << " bits left" << std::endl;

    	      } else {

    	        if(DEBUG)
    	          std::cout << "Need bitmap flag set" << std::endl;

    	        d_need_bitmap = 1;
    	        break;

    	      } // n_cv > 0
    	    } // *trig == 1

    	      if( *trig == 2 ) //n_cv > 0 )
    	      {
    	        // update bitmap buffer
    	//    	if( *trig == 2 ){
    		if( n_cv > 0 ){
    	            map = cv;
    		    d_need_bits = 2*calc_bit_amount_2( map, d_vlen, d_coding );
    	//    	}
    	    	std::cout << "d_need_bits = " << d_need_bits << std::endl;

    	        // if not enough input, won't consume trigger, therefore
    	        // don't consume bitmap item
    	        if( n_bits < d_need_bits ){
    	          d_need_bitmap = 1;
    	          break;
    	        }

    	        copy = true;
    	        d_need_bitmap = 0;

    	        --n_cv; cv += d_vlen;
    	        consume(1, 1);
    	        std::cout << "consumed(1, 1) for *trig != 1" << std::endl;

    	        if(DEBUG)
    	          std::cout << "Consume 1 bitmap item, leave " << n_cv << " items"
    	                    << " and need " << d_need_bits << " bits while "
    	                    << n_bits << " bits left" << std::endl;

    	      } else {

    	        if(DEBUG)
    	          std::cout << "Need bitmap flag set" << std::endl;

    	        d_need_bitmap = 1;
    	        break;

    	      } // n_cv > 0
    	    } // *trig != 1

    	    // check if we have enough bits

    	    if( n_bits < d_need_bits ){

    	      if(DEBUG)
    	        std::cout << "Do not have enough bits, need " << d_need_bits
    	                  << " have " << n_bits << std::endl;

    	      break;

    	    } // n_bits < d_need_bits


    	    if(DEBUG)
    	      std::cout << ".";


    	    // modulate block
    	    if( *trig == 1 ){

    	    	std::cout << "\n\t MODULATE ID SYMBOL" << std::endl;

    	    	for( int i = 0; i < d_vlen; ++i, ++blk, ++blk_2){

    	      		if( map[i] == 0 ){
    	        		*blk = gr_complex( 0.0, 0.0 );
    	//        		*blk_2 = gr_complex( 0.0, 0.0 );

    	      		}else{
    	       			mod->modulate( blk, data, map[i], d_coding );
    	//       			mod->modulate( blk_2, data, map[i], d_coding );
    	      		} // map[i] == 0
    	      		*blk_2 = *blk;
    	    	} // for-loop

    	    	--nout;
    	    	n_bits -= d_need_bits;

    	    } else {

    	    	std::cout << "\n\t MODULATE 1st DATA SYMBOLS" << std::endl;

    	    	for( int i = 0; i < d_vlen; ++i, ++blk, ++blk_2){

    	      		if( map[i] == 0 ){
    	        		*blk = gr_complex( 0.0, 0.0 );
    	//        		*blk_2 = gr_complex( 0.0, 0.0 );

    		      	}else{
    				       	mod->modulate( blk, data, map[i], d_coding );		// S1
    	//					mod->modulate( blk_2, data, map[i], d_coding );		// S1
    	      		} // map[i] == 0
    	      		*blk_2 = *blk;
    	    	} // for-loop

    			--nout;
    	//		n_bits -= d_need_bits;

    			std::cout << "\t MODULATE 2nd DATA SYMBOLS\n" << std::endl;

    	    	for( int i = d_vlen; i < d_vlen + d_vlen; ++i, ++blk, ++blk_2){

    				if( map[i] == 0 ){
    					*blk = gr_complex( 0.0, 0.0 );
    	//				*blk_2 = gr_complex( 0.0, 0.0 );

    				}else{
    						mod->modulate( blk, data, map[i], d_coding );		// S2
    	//					mod->modulate( blk_2, data, map[i], d_coding );		// S2
    	      		} // map[i] == 0
    				*blk_2 = *blk;
    	    	} // for-loop

    			--nout;
    			n_bits -= d_need_bits;

    	    } // if
    	  } // for-loop


    	  // store to internal state variable
    	  if( copy ){

    	    memcpy( d_bitmap.get(), map, d_vlen*sizeof(char) );

    	    if(DEBUG)
    	      std::cout << "Copy bitmap to internal state buffer" << std::endl;

    	  } // copy


    	  if(DEBUG)
    	    std::cout << "[mapper] Leaving process, d_need_bits=" << d_need_bits
    	              << " d_need_bitmap=" << d_need_bitmap << " consume "
    	              << ninput_items[0]-n_bits << " bits and consume/produce "
    	              << noutput_items-nout << " triggers/ofdm blocks"
    	              << std::endl;


    	  consume(0, ninput_items[0]-n_bits);		// consume at input 0: ninput_items[0] -ninput_items[0] + d_need_bits = d_need_bits
    	  std::cout << "consumed(0, ninput_items[0]-n_bits)" << std::endl;

    	  int p = noutput_items - nout;
    	  consume(2, p); // trigger items
    	  std::cout << "consumed(2, p)" << std::endl;
    	  std::cout << "p = " << p << std::endl;
    	  std::cout << "nout = " << nout << std::endl;
    	  std::cout << "noutput_items = " << noutput_items << std::endl;
    	  return p;
    }

  } /* namespace ofdm */
} /* namespace gr */

