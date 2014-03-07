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
#include "ber_measurement_impl.h"

#include <iostream>

#define DEBUG 0

namespace gr {
  namespace ofdm {

    ber_measurement::sptr
    ber_measurement::make(unsigned long long sliding_window_length)
    {
      return gnuradio::get_initial_sptr
        (new ber_measurement_impl(sliding_window_length));
    }

    /*
     * The private constructor
     */
    ber_measurement_impl::ber_measurement_impl(unsigned long long sliding_window_length)
      : gr::sync_block("ber_measurement",
              gr::io_signature::make(2, 2, sizeof(char)),
              gr::io_signature::make(1, 1, sizeof(float)))
    , d_sliding_window_length(sliding_window_length)
    , d_bits_in_win(sliding_window_length), d_errs_in_win(0)

    {
    	set_history(sliding_window_length+1);
    }

    /*
     * Our virtual destructor.
     */
    ber_measurement_impl::~ber_measurement_impl()
    {
    }

    int
    ber_measurement_impl::work(int noutput_items,
			  gr_vector_const_void_star &input_items,
			  gr_vector_void_star &output_items)
    {
      const char *dat = static_cast<const char*>(input_items[0])+d_sliding_window_length;
	  const char *dat_prev = static_cast<const char*>(input_items[0]);
	  const char *ref = static_cast<const char*>(input_items[1])+d_sliding_window_length;
	  const char *ref_prev = static_cast<const char*>(input_items[1]);

	  float *out = static_cast<float*>(output_items[0]);

	  if(DEBUG)
		std::cout << "[bermst " << unique_id() << "] entered, state "
				  << "nout=" << noutput_items << " d_bits_in_win=" << d_bits_in_win
				  << " d_errs_in_win=" << d_errs_in_win
				  << std::endl;

	  for( int i = 0;
		   i < noutput_items;
		   ++i, ++dat, ++dat_prev, ++ref, ++ref_prev, ++out )
	  {

		// erst rausfallen lassen
		if( *dat_prev < 2 ){
		  --d_bits_in_win;
		  if(*dat_prev != *ref_prev)
			--d_errs_in_win;
		}

		if( *dat < 2 ){
		  ++d_bits_in_win;
		  if(*dat != *ref)
			++d_errs_in_win;
		}

		*out = get_ber();

    	}
        // Tell runtime system how many output items we produced.
        return noutput_items;
    }

  } /* namespace ofdm */
} /* namespace gr */

