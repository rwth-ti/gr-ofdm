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
#include "bernoulli_bit_src_impl.h"

#include <boost/random.hpp>
#include <boost/random/bernoulli_distribution.hpp>
#include <boost/random/variate_generator.hpp>

#include <ofdm/ofdmi_shared_generator.h>

namespace gr {
  namespace ofdm {

  typedef boost::mt19937 base_generator_type;
  typedef boost::shared_ptr<base_generator_type> base_generator_sptr;
  typedef boost::bernoulli_distribution<double> distribution_type;
  typedef boost::variate_generator<base_generator_type&, distribution_type> rng_type;
  typedef boost::shared_ptr<rng_type> rng_sptr;

  class bernoulli_bit_src_impl::rng_detail
  {

    distribution_type dist;
    base_generator_sptr generator;
    rng_sptr rng;

  public:

    rng_detail( double p )
      : dist( p ),
        generator( new base_generator_type() ),
        rng( new rng_type( *generator, dist ) )
    {
      generator->seed( *get_shared_generator() );

      volatile rng_type::result_type f;
      for( int i = 0; i < 1000000; ++i ){
        f = (*rng)();
      }
    }

    void
    gen_bernoulli_sequence( char* out, int N )
    {
      for( int i = 0; i < N; ++i ) {
        out[i] = (*rng)() ? 1 : 0;
      }
    }
  };

    bernoulli_bit_src::sptr
    bernoulli_bit_src::make(double p)
    {
      return gnuradio::get_initial_sptr
        (new bernoulli_bit_src_impl(p));
    }

    /*
     * The private constructor
     */
    bernoulli_bit_src_impl::bernoulli_bit_src_impl(double p)
      : gr::sync_block("bernoulli_bit_src",
              gr::io_signature::make(0, 0, 0),
              gr::io_signature::make(1, 1, sizeof(char)))
    , d_p(p)
    , d_rng_detail( new rng_detail( p ) )
    {}

    /*
     * Our virtual destructor.
     */
    bernoulli_bit_src_impl::~bernoulli_bit_src_impl()
    {
    }

    int
    bernoulli_bit_src_impl::work(int noutput_items,
			  gr_vector_const_void_star &input_items,
			  gr_vector_void_star &output_items)
    {
    	char *out = static_cast<char*>( output_items[0] );
    	d_rng_detail->gen_bernoulli_sequence( out, noutput_items );

        // Tell runtime system how many output items we produced.
        return noutput_items;
    }

  } /* namespace ofdm */
} /* namespace gr */

