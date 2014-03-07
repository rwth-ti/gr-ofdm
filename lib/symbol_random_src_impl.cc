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
#include "symbol_random_src_impl.h"

#include <iostream>


#include <boost/random.hpp>
#include <boost/random/uniform_smallint.hpp>
#include <boost/random/variate_generator.hpp>

#include <ofdm/ofdmi_shared_generator.h>

#define DEBUG 0

namespace gr {
  namespace ofdm {

    typedef boost::mt19937 base_generator_type;
    typedef boost::shared_ptr<base_generator_type> base_generator_sptr;
    typedef boost::uniform_smallint<int> distribution_type;
    typedef boost::variate_generator<base_generator_type&, distribution_type> rng_type;
    typedef boost::shared_ptr<rng_type> rng_sptr;

    class symbol_random_src_impl::rng_detail
    {

      distribution_type dist;
      base_generator_sptr generator;
      rng_sptr rng;

    public:

      rng_detail( int max )
        : dist( 0, max ),
          generator( new base_generator_type() ),
          rng( new rng_type( *generator, dist ) )
      {
        generator->seed( *get_shared_generator() );

        volatile rng_type::result_type f;
        for( int i = 0; i < 1000000; ++i ){
          f = (*rng)();
        }
      }

      rng_type::result_type
      get_sample( void )
      {
        return (*rng)();
      }

    };



    symbol_random_src::sptr
    symbol_random_src::make(const std::vector<gr_complex> &symbols, int vlen)
    {
      return gnuradio::get_initial_sptr
        (new symbol_random_src_impl(symbols, vlen));
    }

    /*
     * The private constructor
     */
    symbol_random_src_impl::symbol_random_src_impl(const std::vector<gr_complex> &symbols, int vlen)
      : gr::sync_block("symbol_random_src",
              gr::io_signature::make(0, 0, 0),
              gr::io_signature::make2( 1, 2, sizeof(gr_complex)*vlen, sizeof(char)*vlen ))
    	, d_symbols( symbols )
    	, d_vlen( vlen )
    	, d_rng_detail( new rng_detail( symbols.size()-1 ) )
    {}

    /*
     * Our virtual destructor.
     */
    symbol_random_src_impl::~symbol_random_src_impl()
    {
    }

    int
    symbol_random_src_impl::work(int noutput_items,
			  gr_vector_const_void_star &input_items,
			  gr_vector_void_star &output_items)
    {
    	  gr_complex *out = static_cast<gr_complex*>( output_items[0] );
    	  char *ind_out = 0;

    	  if( output_items.size() > 1 ){
    	    ind_out = static_cast<char*>( output_items[1] );
    	  }

    	  for( int i = 0; i < noutput_items * d_vlen; ++i ) {

    	    const rng_type::result_type ind = d_rng_detail->get_sample();

    	    out[i] = d_symbols[ ind ];

    	    if ( ind_out != 0 ) {
    	      ind_out[i] = static_cast<char>( ind );
    	    }

    	  }

    	  if( DEBUG ) {
    	    std::cout << "[sym rand src " << unique_id() << "] produced "
    	              << noutput_items << " items" << std::endl;
    	  }

    	  return noutput_items;
    }

  } /* namespace ofdm */
} /* namespace gr */

