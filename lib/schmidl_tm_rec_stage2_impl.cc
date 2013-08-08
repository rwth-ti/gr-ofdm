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
#include "schmidl_tm_rec_stage2_impl.h"

namespace gr {
  namespace ofdm {

    schmidl_tm_rec_stage2::sptr
    schmidl_tm_rec_stage2::make(int window)
    {
      return gnuradio::get_initial_sptr
        (new schmidl_tm_rec_stage2_impl(window));
    }

    /*
     * The private constructor
     */
    schmidl_tm_rec_stage2_impl::schmidl_tm_rec_stage2_impl(int window)
      : gr::sync_block("schmidl_tm_rec_stage2",
              gr::io_signature::make2(2, 2, sizeof(gr_complex), sizeof(float) ),
              gr::io_signature::make(1, 1, sizeof(float)))
    , d_delay( window+1 )
    , d_acc1( 0.0,0.0 )
    , d_acc2( 0.0 )
    {
    	  set_history( d_delay + 1 );
    }

    /*
     * Our virtual destructor.
     */
    schmidl_tm_rec_stage2_impl::~schmidl_tm_rec_stage2_impl()
    {
    }

    int
    schmidl_tm_rec_stage2_impl::work(int noutput_items,
			  gr_vector_const_void_star &input_items,
			  gr_vector_void_star &output_items)
    {
    	  const gr_complex * p_del = static_cast<const gr_complex*>(input_items[0]);
    	  const gr_complex * p = p_del + d_delay;

    	  const float * r_del = static_cast<const float*>(input_items[1]);
    	  const float * r = r_del + d_delay;

    	  float * out = static_cast<float*>(output_items[0]);

    	  // use local variable for accumulators, read recent values
    	  gr_complex acc1 = d_acc1;
    	  float      acc2 = d_acc2;

    	  // use references for simpler access
    	  float & x = acc1.real();
    	  float & y = acc1.imag();

    	  // NOTE: GCC performs better if we use temporary constants for
    	  // every expression

    	  for( int i = 0; i < noutput_items; ++i )
    	  {
    	    {
    	      gr_complex const t1 = p[i];
    	      gr_complex const t2 = p_del[i];
    	      gr_complex const t = t1 - t2;
    	      acc1 += t;
    	    }

    	    {
    	      float const t1 = r[i];
    	      float const t2 = r_del[i];
    	      float const t = t1 - t2;
    	      acc2 += t;
    	    }

    	    float const acc2_sq = acc2 * acc2;
    	    float const x2 = x*x; // squared real part of acc1
    	    float const y2 = y*y; // same for imaginary part
    	    float const x2y2 = x2 + y2;
    	    out[i] = x2y2 / acc2_sq;

    	  } // for-loop

    	  d_acc1 = acc1;
    	  d_acc2 = acc2;

    	  return noutput_items;
    }

  } /* namespace ofdm */
} /* namespace gr */

