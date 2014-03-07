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
#include "schmidl_tm_rec_stage1_impl.h"

#include <cmath>

namespace gr {
  namespace ofdm {

    schmidl_tm_rec_stage1::sptr
    schmidl_tm_rec_stage1::make(int fft_length)
    {
      return gnuradio::get_initial_sptr
        (new schmidl_tm_rec_stage1_impl(fft_length));
    }

    /*
     * The private constructor
     */
    schmidl_tm_rec_stage1_impl::schmidl_tm_rec_stage1_impl(int fft_length)
      : gr::sync_block("schmidl_tm_rec_stage1",
              gr::io_signature::make(1, 1, sizeof(gr_complex)),
              gr::io_signature::make2(2, 2, sizeof(gr_complex), sizeof(float)))
    	, d_fft_length( fft_length )
    	, d_delay( fft_length/2 )
    {
    	  set_history( d_delay + 1 );
    }

    /*
     * Our virtual destructor.
     */
    schmidl_tm_rec_stage1_impl::~schmidl_tm_rec_stage1_impl()
    {
    }

    int
    schmidl_tm_rec_stage1_impl::work(int noutput_items,
			  gr_vector_const_void_star &input_items,
			  gr_vector_void_star &output_items)
    {
    	  // NOTE: GCC likes temporary constants and simple expressions

    	  const gr_complex * in_del = static_cast<const gr_complex*>(input_items[0]);
    	  const gr_complex * in = in_del + d_delay;

    	  gr_complex * p = static_cast<gr_complex*>(output_items[0]);
    	  float * r = static_cast<float*>(output_items[1]);



    	  for( int i = 0; i < noutput_items; ++i ){

    	    float const x = in[i].real();
    	    float const y = in[i].imag();

    	    float const x2 = x*x;
    	    float const y2 = y*y;


    	    gr_complex const id = in_del[i];
    	    gr_complex const cid = std::conj( id );

    	    gr_complex const in_t = in[i];

    	    p[i] = cid * in_t;

    	    r[i] = x2 + y2;

    	  } // for-loop

    	  return noutput_items;
    }

  } /* namespace ofdm */
} /* namespace gr */

