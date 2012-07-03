
/* $Id$ */

#ifdef HAVE_CONFIG_H
#include "config.h"
#endif

#include <gr_sync_block.h>
#include <gr_io_signature.h>
#include <ofdm_multiply_const_ccf.h>

#include <iostream>

#include <malloc16.h>

#define DEBUG 0

typedef float v4sf __attribute__ ((vector_size(16)));




ofdm_multiply_const_ccf::ofdm_multiply_const_ccf( float k )
  : gr_sync_block(
      "multiply_const_ccf",
      gr_make_io_signature(
        1, 1,
        sizeof( gr_complex ) ),
      gr_make_io_signature(
        1, 1,
        sizeof( gr_complex ) ) )

  , d_cache( static_cast< float * >(
      malloc16Align( cache_line ) ) )

{
  set_k( k );
  set_output_multiple( cache_size / 2 ); // because treat complex as 2 floats
}

ofdm_multiply_const_ccf ::
~ofdm_multiply_const_ccf()
{
  if( d_cache )
    free16Align( d_cache );
}

void
ofdm_multiply_const_ccf ::
set_k( float k )
{
  for( size_type i = 0; i < cache_size; ++i )
  {
    d_cache[ i ] = k;
  }
  d_k = k;
}

typedef v4sf * v4sf_ptr __attribute__ ((aligned(16)));
typedef v4sf const * v4sfc_ptr __attribute__ ((aligned(16)));


int
ofdm_multiply_const_ccf::work(
  int                         noutput_items,
  gr_vector_const_void_star & input_items,
  gr_vector_void_star       & output_items )
{
  //assert( ( (long)input_items[0] & 15 ) == 0 );
  //assert( ( (long)output_items[0] & 15 ) == 0 );

  // because treat complex as 2 floats

  size_type cnt = 2 * noutput_items; // multiple of cache_size

  {
    v4sfc_ptr __restrict in  = static_cast< v4sfc_ptr >( input_items[0] );
    v4sf_ptr  __restrict out = static_cast< v4sf_ptr >( output_items[0] );
    v4sfc_ptr __restrict cache = reinterpret_cast< v4sfc_ptr >( d_cache );

    size_type i = 0;

    while( cnt >= cache_size )
    {
      out[ i + 0 ] = in[ i + 0 ] * cache[ 0 ];
      out[ i + 1 ] = in[ i + 1 ] * cache[ 1 ];
      out[ i + 2 ] = in[ i + 2 ] * cache[ 2 ];
      out[ i + 3 ] = in[ i + 3 ] * cache[ 3 ];
      out[ i + 4 ] = in[ i + 4 ] * cache[ 4 ];
      out[ i + 5 ] = in[ i + 5 ] * cache[ 5 ];
      out[ i + 6 ] = in[ i + 6 ] * cache[ 6 ];
      out[ i + 7 ] = in[ i + 7 ] * cache[ 7 ];

      cnt -= cache_size;
      i += 8;
    }
  }

  return noutput_items;
}


ofdm_multiply_const_ccf_sptr
ofdm_make_multiply_const_ccf( float k )
{
  return ofdm_multiply_const_ccf::create( k );
}


ofdm_multiply_const_ccf_sptr
ofdm_multiply_const_ccf::create( float k )
{
  try
  {
    ofdm_multiply_const_ccf_sptr tmp(
      new ofdm_multiply_const_ccf( k ) );

    return tmp;
  }
  catch ( ... )
  {
    std::cerr << "[ERROR] Caught exception at creation of "
              << "ofdm_multiply_const_ccf" << std::endl;
    throw;
  } // catch ( ... )
}



