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
#include "frequency_shift_vcc_impl.h"

#include <ofdm/ofdmi_fast_math.h>


#include <gnuradio/sincos.h>

#include <cmath>
#include <iostream>

#define DEBUG 0

namespace gr {
  namespace ofdm {

    static const double two_pi = 2.0 * M_PI;

    frequency_shift_vcc::sptr
    frequency_shift_vcc::make(int vlen, double sensitivity, int cp_length )
    {
      return gnuradio::get_initial_sptr
        (new frequency_shift_vcc_impl(vlen, sensitivity, cp_length));
    }

    /*
     * The private constructor
     */
    frequency_shift_vcc_impl::frequency_shift_vcc_impl(int vlen, double sensitivity, int cp_length )
      : gr::block("frequency_shift_vcc",
              gr::io_signature::make3(3, 3, sizeof (gr_complex) * vlen,
                      sizeof(float),
                      sizeof(char)),
              gr::io_signature::make(1, 1, sizeof (gr_complex) * vlen))
    	, d_sensitivity (sensitivity)
    	, d_vlen(vlen)
    	, d_phase(0.0)
    	, d_cp_length(cp_length)
    	, d_eps(0.0)
    	, d_need_eps(1)
    {
    	assert( ( vlen % 2 ) == 0 );
    }

    /*
     * Our virtual destructor.
     */
    frequency_shift_vcc_impl::~frequency_shift_vcc_impl()
    {
    }

    void
    frequency_shift_vcc_impl::forecast (int noutput_items, gr_vector_int &ninput_items_required)
    {
        /* <+forecast+> e.g. ninput_items_required[0] = noutput_items */
    	ninput_items_required[0] = noutput_items;  // blocks
    	ninput_items_required[2] = noutput_items;  // trigger
    	ninput_items_required[1] = d_need_eps;  // eps
    }

    int
    frequency_shift_vcc_impl::noutput_forecast( gr_vector_int &ninput_items,
        int available_space, int max_items_avail, std::vector<bool> &input_done )
    {

      if( ninput_items[1] < d_need_eps ){
        if( input_done[1] )
          return -1;

        return 0;
      }

      int nout = std::min( available_space,
                 std::min( ninput_items[0], ninput_items[2] ) );

      if( nout == 0 && ( input_done[0] || input_done[2] ) )
        return -1;

      return nout;

    }

    int
    frequency_shift_vcc_impl::general_work (int noutput_items,
                       gr_vector_int &ninput_items,
                       gr_vector_const_void_star &input_items,
                       gr_vector_void_star &output_items)
    {
    	const gr_complex *in = static_cast<const gr_complex *>(input_items[0]);
    	  const float *eps = static_cast<const float *>(input_items[1]);
    	  const char *frame_trigger = static_cast<const char *>(input_items[2]);
    	  gr_complex *out = static_cast<gr_complex *>(output_items[0]);

    	  int n_in = ninput_items[0];
    	  int n_eps = ninput_items[1];
    	  int n_trig = ninput_items[2];
    	  int nout = noutput_items;

    	  int n_min = std::min(nout, std::min(n_in, n_trig));


    	  if(DEBUG)
    	    std::cout << "[freqshift " << unique_id() << "] entered, state "
    	              << "n_in=" << n_in << " n_eps=" << n_eps << " n_trig=" << n_trig
    	              << " nout=" << nout << "  n_min=" << n_min << std::endl;

    	  for( int i = 0; i < n_min; ++i, in += d_vlen, out += d_vlen, --nout )
    	  {
    	    // Update internal state, reset phase accumulator
    	    if( frame_trigger[i] == 1 )
    	    {
    	      d_phase = 0.0;

    	      if( n_eps == 0 )
    	      {
    	        d_need_eps = 1;
    	        break;
    	      }

    	      d_eps = *eps;
    	      ++eps; --n_eps;

    	      d_need_eps = 0;

    	      if(DEBUG)
    	        std::cout << "consume one eps value, left " << n_eps << " values"
    	                  << " and " << nout << " input/output items" << std::endl;

    	    } // frame_trigger

    	    // perform frequency shift

    	    double phase_step = two_pi * d_sensitivity * d_eps;

    	    // skip cyclic prefix
    	    if( d_cp_length > 0 )
    	    {
    	      d_phase += static_cast< float >( d_cp_length ) * phase_step;
    	    }


    	    perform_frequency_shift( in, out, d_vlen, d_phase, phase_step );


    	//    gr_complex phasor( std::cos( d_phase ), std::sin( d_phase ) );
    	//    const gr_complex step_phasor( std::cos( phase_step ),
    	//      std::sin( phase_step ) );
    	//
    	//    for( int j = 0; j < d_vlen; ++j )
    	//    {
    	//      out[j] = in[j] * phasor;
    	//      phasor *= step_phasor;
    	//    }

    	    d_phase += static_cast<float>( d_vlen ) * phase_step;

    	    // Limit the phase accumulator to [-16*pi,16*pi]
    	    if (fabs(d_phase) > 16 * M_PI)
    	    {
    	      d_phase =  fmod(d_phase, 2*M_PI);
    	      if(DEBUG)
    	        std::cout << "Limit phase accumulator" << std::endl;
    	    }

    	  } // for-loop


    	  if(DEBUG)
    	    std::cout << "[freqshift " << unique_id() << "] leaving, produce "
    	              << noutput_items-nout << " items" << std::endl;

    	  consume( 1, ninput_items[1] - n_eps );

    	  int t = noutput_items - nout;

    	  consume(0, t);
    	  consume(2, t);

    	  return t;
    }

  } /* namespace ofdm */
} /* namespace gr */

