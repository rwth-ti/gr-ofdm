/* -*- c++ -*- */
/* 
 * Copyright 2014 <+YOU OR YOUR COMPANY+>.
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
#include "vector_element_vff_impl.h"

namespace gr {
  namespace ofdm {

    vector_element_vff::sptr
    vector_element_vff::make(int vlen, int element)
    {
      return gnuradio::get_initial_sptr
        (new vector_element_vff_impl(vlen, element));
    }

    /*
     * The private constructor
     */
    vector_element_vff_impl::vector_element_vff_impl(int vlen, int element)
      : gr::sync_block("vector_element_vff",
              gr::io_signature::make(1, 1, vlen * sizeof(float)),
              gr::io_signature::make(1, 1, sizeof(float)))
        , d_vlen( vlen )
        , d_element( element )
    {}

    /*
     * Our virtual destructor.
     */
    vector_element_vff_impl::~vector_element_vff_impl()
    {
    }

    int
    vector_element_vff_impl::work(int noutput_items,
			  gr_vector_const_void_star &input_items,
			  gr_vector_void_star &output_items)
    {
        const float *in = static_cast< const float* > ( input_items[0] );
        float *out = static_cast< float* > ( output_items[0] );

        for( int i = 0; i < noutput_items; ++i )
        {
            memcpy( out, in + d_element - 1, sizeof(float) );
            in += d_vlen;
            out++;
        }
        return noutput_items;
    }

    void vector_element_vff_impl::set_element(const int element)
    {
        if ( element < 0)
            d_element = 0;
        if ( element > d_vlen )
            d_element = d_vlen;
        else
            d_element = element;
    };


  } /* namespace ofdm */
} /* namespace gr */

