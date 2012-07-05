/*
 * ofdm_vector_element.cc
 *
 *  Created on: 01.02.2012
 *      Author: schmitz
 */

#ifdef HAVE_CONFIG_H
#include "config.h"
#endif

#include <gr_sync_decimator.h>

#include <ofdm_vector_element.h>
#include <gr_io_signature.h>
#include <iostream>

ofdm_vector_element_sptr ofdm_make_vector_element( int vlen, int element )
{
    return ofdm_vector_element_sptr( new ofdm_vector_element( vlen, element ) );
}

ofdm_vector_element::ofdm_vector_element( int vlen, int element ) :

    gr_sync_block( "vector_element",
            gr_make_io_signature( 1, 1, vlen * sizeof(gr_complex) ),
            gr_make_io_signature( 1, 1, sizeof(gr_complex) )),

    d_vlen( vlen ),
    d_element( element )
{
    assert( element <= vlen );
    assert( element > 0 );
}

int
ofdm_vector_element::work(
        int noutput_items,
        gr_vector_const_void_star &input_items,
        gr_vector_void_star &output_items )
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

void ofdm_vector_element::set_element(const int element)
{
    if ( element < 0)
        d_element = 0;
    if ( element > d_vlen )
        d_element = d_vlen;
    else
        d_element = element;
    //std::cout << "set element: " << element << std::endl;
};

