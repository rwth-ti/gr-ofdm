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
#include "generic_softdemapper_vcf_impl.h"

#include <string.h>


#include <iostream>
#include <stdexcept>
#include <algorithm>

#define DEBUG 0

namespace gr {
  namespace ofdm {

    generic_softdemapper_vcf::sptr
    generic_softdemapper_vcf::make(int vlen,bool coding)
    {
      return gnuradio::get_initial_sptr
        (new generic_softdemapper_vcf_impl(vlen, coding));
    }

    /*
     * The private constructor
     */
    generic_softdemapper_vcf_impl::generic_softdemapper_vcf_impl(int vlen,bool coding)
      : gr::block("generic_softdemapper_vcf",
              gr::io_signature::make4 (
                      4, 4,
                      sizeof(gr_complex)*vlen, // ofdm blocks
                      sizeof(char)*vlen,       // bitmap
                      sizeof(float)*vlen,	   // CSI
                      sizeof(char)),           // update trigger
              gr::io_signature::make(
                      1, 1,
                      sizeof(float)))          // bitdata
    	, d_vlen( vlen )
        , d_coding( coding )
        , d_items_req( 1 )
        , d_need_bitmap( 1 )
        , d_bitmap( new char[vlen] )
        , d_need_csi( 1 )
        , d_csi( new float[vlen] )
        , d_demod( new ofdmi_modem() )
    {
    	  memset(d_bitmap.get(), 0, d_vlen);
    	  memset(d_csi.get(), 1, d_vlen);
    	  if( DEBUG )
    	      std::cout << "[softdemapper " << unique_id() << "] vlen=" << vlen << " coding=" << d_coding << std::endl;
    }

    /*
     * Our virtual destructor.
     */
    generic_softdemapper_vcf_impl::~generic_softdemapper_vcf_impl()
    {
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
    		  throw std::out_of_range("SOFTDEMAPPER: Mode higher than 9 not supported");
    		if(cv[i] < 0)
    		  throw std::out_of_range("MAPPER: Cannot allocate less than zero bits");
    	    if (cv[i] > 0)
    	      bits_per_symbol += bits_per_mode[cv[i]-1];

    			//std::cout << "MODE: " << cv[i] <<std::endl;
    			//std::cout << "bits_per_symbol: " << bits_per_symbol <<std::endl;
    	  }
      }
      else
      {
    	  for(int i = 0; i < vlen; ++i) {
    		if(cv[i] > 8)
    		  throw std::out_of_range("SOFTDEMAPPER: More than 8 bits per symbol not supported");
    		if(cv[i] < 0)
    		  throw std::out_of_range("SOFTDEMAPPER: Cannot allocate less than zero bits");
    		bits_per_symbol += cv[i];
    	  }
      }


      return bits_per_symbol;
    }

    static inline float
    max_csi(const float* csi, int vlen)
    {
    	float max = 0;

    	for(int i = 0; i < vlen; ++i)
    	{
    		if(csi[i]>max)
    			max = csi[i];
    	}
    	return max;
    }

    void
    generic_softdemapper_vcf_impl::forecast (int noutput_items, gr_vector_int &ninput_items_required)
    {
        /* <+forecast+> e.g. ninput_items_required[0] = noutput_items */
      // how may input items do we need _at least_
	  // 1 bitmap, but 1 or more data vectors and trigger points if the last
	  // bitmap will be used several times
	  ninput_items_required[0] = d_items_req;
	  ninput_items_required[1] = d_need_bitmap;
	  ninput_items_required[2] = d_need_csi;
	  ninput_items_required[3] = d_items_req;
	  ninput_items_required[2] = d_need_csi;
    }

    int
    generic_softdemapper_vcf_impl::noutput_forecast( gr_vector_int &ninput_items,
        int available_space, int max_items_avail, std::vector<bool> &input_done )
    {

      // we don't know much about the rate.
      //  - if we have no input ofdm block, we won't produce anything
      //  - ofdm blocks and trigger items are consumed at the same rate
      //  - if we need a new bitmap and don't have one, we can't proceed
      //  - one item may need more output space we have but also zero

      if( ninput_items[1] < d_need_bitmap ){
        if( input_done[1] ){
          return -1;
        }

        return 0;
      }

      if( ninput_items[0] == 0 ){
        if( input_done[0] ){
          return -1;
        }
        return 0;
      }

      if( ninput_items[3] == 0 ){
        if( input_done[3] ){
          return -1;
        }
        return 0;
      }

      return available_space;

    }

    int
    generic_softdemapper_vcf_impl::general_work (int noutput_items,
                       gr_vector_int &ninput_items,
                       gr_vector_const_void_star &input_items,
                       gr_vector_void_star &output_items)
    {
    	// input streams
    	  const gr_complex * sym_in = static_cast<const gr_complex*>(input_items[0]);
    	  const char * cv_in = static_cast<const char*>(input_items[1]);
    	  const float * csi_in = static_cast<const float*>(input_items[2]);
    	  const char * trig = static_cast<const char*>(input_items[3]);

    	  // output streams
    	  float * out = static_cast<float*>(output_items[0]);

    	  memset( out, 0, noutput_items );

    	  // reset
    	  set_output_multiple( 1 );

    	  const int n_sym = ninput_items[0];
    	  int n_cv = ninput_items[1];
    	  int n_csi = ninput_items[2];
    	  const int n_trig = ninput_items[3];
    	  int nout = noutput_items;

    	  if(DEBUG)
    	    std::cout << "[softdemapper " << unique_id() << "] state, n_sym=" << n_sym
    	              << " n_cv=" << n_cv
    	              << " n_csi=" << n_csi
    	              << " n_trig=" << n_trig << " nout=" << nout
    	              << std::endl;

    	  // use internal state variable
    	  const char * cv = d_bitmap.get();

    	  const float * csi = d_csi.get();
    	  bool do_copy = false;
    	  bool do_copy_csi = false;

    	  const int n_min = std::min( n_sym, n_trig );
    	  int bps = calc_bit_amount( cv, d_vlen, d_coding );
    	  int i;
    	  for( i = 0; i < n_min; ++i ){

    	    if( trig[i] != 0 )
    	    {
    	      if( n_cv == 0 )
    	      {
    	        d_need_bitmap = 1;
    	        break;
    	      }

    	      //std::cout << "MODE MAP: " << int(cv_in[1])<< std::endl;
    	      bps = calc_bit_amount( cv_in, d_vlen, d_coding );

    	      if( nout < bps )
    	      {
    	        set_output_multiple( bps );
    	        //std::cout << "BPS: " << bps <<std::endl;
    	        break;
    	      }

    	      //std::cout << "Update MODEMAP and CSI" << std::endl;

    	      cv = cv_in;
    	      do_copy = true;
    	      d_need_bitmap = 0;
    	      --n_cv;
    	      cv_in += d_vlen;

    	      if(trig[i]==2)
    		  {
    	    	  if( n_csi == 0)
    				{
    				  d_need_csi = 1;
    				}
    	    	  else
    	    	  {
    				  csi = csi_in;
    				  d_need_csi = 0;
    				  --n_csi;
    				  csi_in += d_vlen;
    				  do_copy_csi=true;
    	    	  }
    		  }

    	    } // trig[i] != 0

    	    if( nout < bps )
    	    {
    	      set_output_multiple( bps );
    	      //std::cout << "BPS_2: " << bps <<std::endl;
    	      break;
    	    }

    	    // demodulation

    	    for( int x = 0; x < d_vlen; ++x ) {
    	      if( cv[x] == 0 )
    	        continue;
    	      if(DEBUG)
    	          std::cout << "Demap OFDM symbol" << std::endl;
    	      d_demod->softdemodulate( sym_in[x], out, cv[x], d_csi[x], max_csi(d_csi.get(),d_vlen), d_coding ); //advances out
    	    }

    	    sym_in += d_vlen;
    	    nout -= bps;

    	  } // for-loop

    	  if( do_copy ){
    		  if(DEBUG)
    			std::cout << "Copy data to state buffers" << std::endl;
    	    memcpy( d_bitmap.get(), cv, sizeof(char)*d_vlen );
    	  }
    	  if( do_copy_csi ){
    	  	  if(DEBUG)
    	  		std::cout << "Copy csi data to state buffers" << std::endl;
    	      memcpy( d_csi.get(), csi, sizeof(float)*d_vlen );
    	    }

    	  assert( i <= ninput_items[0] && i <= ninput_items[3] && i >= 0 );
    	  assert( n_cv <= ninput_items[1] && n_cv >= 0 );
    	  assert( n_csi <= ninput_items[2] && n_csi >= 0 );
    	  consume( 1, ninput_items[1] - n_cv );
    	  consume( 2, ninput_items[2] - n_csi );
    	  consume( 0, i );
    	  consume( 3, i );

    	  if( DEBUG ) {
    	    std::cout << "[softdemapper] produced " << noutput_items-nout << " items"
    	              << " and consumed " << i << " symbols and triggers and "
    	              << ninput_items[1]-n_cv << " bitmap items" << std::endl;
    	  }

    	  assert( nout <= noutput_items && nout >= 0 );
    	  return noutput_items - nout;
    }

    std::vector<gr_complex>
    generic_softdemapper_vcf_impl::get_constellation( int bits, bool coding )
    {
      std::vector<gr_complex> x;
      try {

        x = d_demod->get_constellation( bits, coding );

      } catch ( modulation_not_supported ex ) {

        std::cerr << "Error: requested modulation is not supported" << std::endl;

      } catch ( ... ) {

        throw;

      }

      return x;
    }

  } /* namespace ofdm */
} /* namespace gr */

