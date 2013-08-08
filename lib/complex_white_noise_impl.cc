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
#include "complex_white_noise_impl.h"

#include <cmath>

#include <boost/random.hpp>
#include <boost/random/normal_distribution.hpp>
#include <boost/random/variate_generator.hpp>

#include <iostream>

#include <stdexcept>

#include <ofdm/ofdmi_shared_generator.h>

typedef boost::lagged_fibonacci44497 base_generator_type;
typedef boost::shared_ptr<base_generator_type> base_generator_sptr;

typedef boost::normal_distribution<float> distribution_type;
typedef boost::variate_generator<base_generator_type&, distribution_type> rng_type;
typedef boost::shared_ptr<rng_type> rng_sptr;

#define DEBUG 0
#if DEBUG
#include <iostream>
#endif

namespace gr {
  namespace ofdm {

	 class complex_white_noise_impl::rng_detail
	  {

		distribution_type dist_r, dist_i;
		rng_sptr rng_r,rng_i;

		base_generator_sptr generator;

	  	public:

		rng_detail( gr_complex mean, float sigma )
		  : dist_r( mean.real(), sigma / std::sqrt(2.0) ),
			dist_i( mean.imag(), sigma / std::sqrt(2.0) )
		{
		  base_generator_sptr u( new base_generator_type( ) );
		  generator = u;
		  generator->seed( *get_shared_generator() );

		  rng_sptr t( new rng_type( *generator, dist_r ) );
		  rng_r = t;

		  rng_sptr v( new rng_type( *generator, dist_i ) );
		  rng_i = v;

		  volatile float f;
		  for( int i = 0; i < 1000000; ++i ){
			f = (*rng_r)();
			f = (*rng_i)();
		  }
		}

		gr_complex
		get_complex_sample(void)
		{
		  return gr_complex( (*rng_r)(), (*rng_i)() );
		}
	  };

    complex_white_noise::sptr
    complex_white_noise::make(gr_complex mean, float sigma)
    {
      return gnuradio::get_initial_sptr
        (new complex_white_noise_impl(mean, sigma));
    }

    /*
     * The private constructor
     */
    complex_white_noise_impl::complex_white_noise_impl(gr_complex mean, float sigma)
      : gr::sync_block("complex_white_noise",
              gr::io_signature::make(0, 0, 0),
              gr::io_signature::make(1, 1, sizeof(gr_complex)))
    , d_rng_detail( new rng_detail( mean, sigma ) )
    , d_mean( mean )
    , d_sigma( sigma )
    {}

    /*
     * Our virtual destructor.
     */
    complex_white_noise_impl::~complex_white_noise_impl()
    {
    }

    int
    complex_white_noise_impl::work(int noutput_items,
			  gr_vector_const_void_star &input_items,
			  gr_vector_void_star &output_items)
    {
    	gr_complex * out = static_cast<gr_complex*>(output_items[0]);

    	  for( int i = 0; i < noutput_items; ++i ){
    	    out[i] = d_rng_detail->get_complex_sample();
    	  }

    	  return noutput_items;
    }

  } /* namespace ofdm */
} /* namespace gr */

