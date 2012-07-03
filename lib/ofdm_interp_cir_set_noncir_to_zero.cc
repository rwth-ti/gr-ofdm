
/* $Id: ofdm_interp_cir_set_noncir_to_zero.cc 923 2009-04-21 14:03:45Z auras $ */

#ifdef HAVE_CONFIG_H
#include "config.h"
#endif

#include <gr_sync_block.h>
#include <gr_io_signature.h>
#include <ofdm_interp_cir_set_noncir_to_zero.h>

#include <iostream>
#include <algorithm>

#define DEBUG 0


ofdm_interp_cir_set_noncir_to_zero ::
ofdm_interp_cir_set_noncir_to_zero( int vlen, int window )
  : gr_sync_block(
      "interp_cir_set_noncir_to_zero",
      gr_make_io_signature2(
        2, 2,
        sizeof( gr_complex ) * vlen,
        sizeof( short ) ),
      gr_make_io_signature(
        1, 1,
        sizeof( gr_complex ) * vlen ) )

  , d_vlen( vlen )
  , d_window( window )

{
}

int
ofdm_interp_cir_set_noncir_to_zero ::
work(
  int                         noutput_items,
  gr_vector_const_void_star & input_items,
  gr_vector_void_star       & output_items )
{
  gr_complex const * in = static_cast< gr_complex const * >( input_items[0] );
  short const * in_1 = static_cast< short const * >( input_items[1] );
  gr_complex * out = static_cast< gr_complex * >( output_items[0] );

  // only copy d_window items from in to out vectors
  // where start of window within in vector is given by in_1

  std::fill_n( out, d_vlen * noutput_items, gr_complex( 0, 0 ) );

  for( int i = 0; i < noutput_items; ++i )
  {

    int pos = in_1[ i ];

    for( int x = 0; x < d_window; ++x )
    {
      out[ pos ] = in[ pos ];

      ++pos;

      if( pos >= d_vlen )
      {
        pos = 0;
      }

    } // for

    in += d_vlen;
    out += d_vlen;

  } // for

  return noutput_items;
}


ofdm_interp_cir_set_noncir_to_zero_sptr
ofdm_make_interp_cir_set_noncir_to_zero( int vlen, int window )
{
  return ofdm_interp_cir_set_noncir_to_zero::create( vlen, window );
}


ofdm_interp_cir_set_noncir_to_zero_sptr
ofdm_interp_cir_set_noncir_to_zero ::
create( int vlen, int window )
{
  try
  {
    ofdm_interp_cir_set_noncir_to_zero_sptr tmp(
      new ofdm_interp_cir_set_noncir_to_zero( vlen, window ) );

    return tmp;
  }
  catch ( ... )
  {
    std::cerr << "[ERROR] Caught exception at creation of "
              << "ofdm_interp_cir_set_noncir_to_zero" << std::endl;
    throw;
  } // catch ( ... )
}



