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
#include "vector_element_impl.h"

#include <iostream>

namespace gr {
  namespace ofdm {

    vector_element::sptr
    vector_element::make(int vlen, int element)
    {
      return gnuradio::get_initial_sptr
        (new vector_element_impl(vlen, element));
    }

    /*
     * The private constructor
     */
    vector_element_impl::vector_element_impl(int vlen, int element)
      : gr::sync_block("vector_element",
              gr::io_signature::make(1, 1, vlen * sizeof(gr_complex)),
              gr::io_signature::make(1, 1, sizeof(gr_complex)))
    	, d_vlen( vlen )
        , d_element( element )
    {
        assert( element <= vlen );
        assert( element > 0 );
    }

    /*
     * Our virtual destructor.
     */
    vector_element_impl::~vector_element_impl()
    {
    }

    int
    vector_element_impl::work(int noutput_items,
			  gr_vector_const_void_star &input_items,
			  gr_vector_void_star &output_items)
    {
        const gr_complex *in = static_cast< const gr_complex* > ( input_items[0] );
        gr_complex *out = static_cast< gr_complex* > ( output_items[0] );

        for( int i = 0; i < noutput_items; ++i )
        {
            memcpy( out, in + d_element - 1, sizeof(gr_complex) );
            in += d_vlen;
            out++;
        }
        return noutput_items;
    }

    void vector_element_impl::set_element(const int element)
    {
        if ( element < 0)
            d_element = 0;
        if ( element > d_vlen )
            d_element = d_vlen;
        else
            d_element = element;
        //std::cout << "set element: " << element << std::endl;
    };

  } /* namespace ofdm */
} /* namespace gr */

