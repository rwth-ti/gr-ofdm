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
#include "ls_estimator_straight_slope_impl.h"

namespace gr {
  namespace ofdm {

    ls_estimator_straight_slope::sptr
    ls_estimator_straight_slope::make(int vlen)
    {
      return gnuradio::get_initial_sptr
        (new ls_estimator_straight_slope_impl(vlen));
    }

    /*
     * The private constructor
     */
    ls_estimator_straight_slope_impl::ls_estimator_straight_slope_impl(int vlen)
      : gr::sync_block("ls_estimator_straight_slope",
              gr::io_signature::make(1, 1, sizeof( float ) * vlen),
              gr::io_signature::make(2, 2, sizeof( float )))
		, d_vlen( vlen )
		, d_slope_coeff( vlen )
		, d_offset_coeff( vlen )
    {
      double ind_squares = 0.0;
      double ind_offset = 0.0;
      for( int i = -vlen/2; i < vlen/2; ++i )
      {
        double di = static_cast< double >( i );
        ind_squares += di * di;
        ind_offset += di;
      }
      double N = vlen;
      double normc = ind_squares * N - ind_offset * ind_offset;
      double slope_coeff_slope = N / normc;
      double slope_coeff_offset = -ind_offset / normc;
      double offset_coeff_slope = - slope_coeff_slope;
      double offset_coeff_offset = ind_squares / normc;

    //  std::cout << "####" << slope_coeff_slope << ":" << slope_coeff_offset << std::endl;

      for( int i = 0; i < vlen; ++i )
      {
        double di = static_cast< double >( i );
        d_slope_coeff[i] = slope_coeff_slope * ( di - N/2 ) + slope_coeff_offset;
        d_offset_coeff[i] = offset_coeff_slope * ( di - N/2 ) + offset_coeff_offset;
      }

    //  float aa= 0;
    //  for( int i = 0; i < vlen; ++i )
    //  {
    //    float fi = static_cast< double >( i ) - N/2;
    //    aa += fi * d_slope_coeff[i];
    //  }
    //  std::cout << "''''" << aa << std::endl;
    }

    /*
     * Our virtual destructor.
     */
    ls_estimator_straight_slope_impl::~ls_estimator_straight_slope_impl()
    {
    }

    int
    ls_estimator_straight_slope_impl::work(int noutput_items,
			  gr_vector_const_void_star &input_items,
			  gr_vector_void_star &output_items)
    {
    	float const * in = static_cast< float const * >( input_items[0] );
    	  float * slope = static_cast< float * >( output_items[0] );
    	  float * offset = static_cast< float * >( output_items[1] );

    	  for( int i = 0; i < noutput_items; ++i, in += d_vlen )
    	  {
    	    float a = 0;
    	    float b = 0;
    	    for( int j = 0; j < d_vlen; ++j )
    	    {
    	      a += d_slope_coeff[j] * in[j];
    	      b += d_offset_coeff[j] * in[j];
    	    }
    	    slope[i] = a;
    	    offset[i] = b;
    	  }

    	  return noutput_items;
    }

  } /* namespace ofdm */
} /* namespace gr */

