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
#include "autocorrelator0_impl.h"

#include <iostream>

namespace gr {
  namespace ofdm {

    autocorrelator0::sptr
    autocorrelator0::make(int lag, int n_samples)
    {
      return gnuradio::get_initial_sptr
        (new autocorrelator0_impl(lag, n_samples));
    }

    /*
     * The private constructor
     */
    autocorrelator0_impl::autocorrelator0_impl(int lag, int n_samples)
      : gr::hier_block2("autocorrelator0",
              gr::io_signature::make(1, 1,sizeof( gr_complex ) ),
              gr::io_signature::make(1, 1,sizeof( float ) ))
    , d_lag( lag )
    , d_n_samples( n_samples )
    , d_s1(ofdm::autocorrelator_stage1::make(lag))
    , d_s2(ofdm::autocorrelator_stage2::make(n_samples))
    {
        connect( self(), 0, d_s1, 0 );
        connect( d_s1, 0, d_s2, 0 );
        connect( d_s1, 1, d_s2, 1 );
        connect( d_s2, 0, self(), 0 );
    }

    /*
     * Our virtual destructor.
     */
    autocorrelator0_impl::~autocorrelator0_impl()
    {
    }


  } /* namespace ofdm */
} /* namespace gr */

