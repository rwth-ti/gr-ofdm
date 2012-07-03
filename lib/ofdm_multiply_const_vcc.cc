
/* $Id: ofdm_multiply_const_vcc.cc 923 2009-04-21 14:03:45Z auras $ */

#ifdef HAVE_CONFIG_H
#include "config.h"
#endif

#include <gr_sync_block.h>
#include <gr_io_signature.h>
#include <ofdm_multiply_const_vcc.h>

#include <malloc16.h>

#include <iostream>
#include <algorithm>

#define DEBUG 0


ofdm_multiply_const_vcc ::
ofdm_multiply_const_vcc( std::vector< gr_complex > const & k )
  : gr_sync_block(
      "multiply_const_vcc",
      gr_make_io_signature(
        1, 1,
        sizeof( gr_complex ) * k.size() ),
      gr_make_io_signature(
        1, 1,
        sizeof( gr_complex ) * k.size() ) )

  , d_vlen( k.size() )
  , d_buffer( static_cast< gr_complex * >(
      malloc16Align( sizeof( gr_complex ) * k.size() ) ) )

{
  assert( ( d_vlen % 2 ) == 0 ); // 16 byte alignment
  std::copy( k.begin(), k.end(), d_buffer );
}

ofdm_multiply_const_vcc ::
~ofdm_multiply_const_vcc()
{
  if( d_buffer )
    free16Align( d_buffer );
}

typedef float __attribute__((vector_size(16))) v4sf;
typedef float const __attribute__((vector_size(16))) v4sfc;

int
ofdm_multiply_const_vcc ::
work(
  int                         noutput_items,
  gr_vector_const_void_star & input_items,
  gr_vector_void_star       & output_items )
{
  v4sfc const * in = static_cast< v4sfc * >( input_items[0] );
  v4sf * out = static_cast< v4sf * >( output_items[0] );

  v4sf * buf = reinterpret_cast< v4sf * >( d_buffer );

  for( int i = 0; i < noutput_items; ++i, in += d_vlen/2, out += d_vlen/2 )
  {
    for( int j = 0; j < d_vlen/2; ++j )
    {
      v4sf x0 = __builtin_ia32_movsldup( buf[ j ] );
      v4sf x1 = in[ j ];
      x0 *= x1;

      x1 = __builtin_ia32_shufps( x1, x1, 0xB1 );
      v4sf x2 = __builtin_ia32_movshdup( buf[ j ] );
      x2 *= x1;

      x0 = __builtin_ia32_addsubps( x0, x2 );
      out[ j ] = x0;

    } // element-wise complex multiplication with d_buffer

  } // for-loop over input

  return noutput_items;

} // work


ofdm_multiply_const_vcc_sptr
ofdm_make_multiply_const_vcc( std::vector< gr_complex > const & k )
{
  return ofdm_multiply_const_vcc::create( k );
}


ofdm_multiply_const_vcc_sptr
ofdm_multiply_const_vcc ::
create( std::vector< gr_complex > const & k )
{
  try
  {
    ofdm_multiply_const_vcc_sptr tmp(
      new ofdm_multiply_const_vcc( k ) );

    return tmp;
  }
  catch ( ... )
  {
    std::cerr << "[ERROR] Caught exception at creation of "
              << "ofdm_multiply_const_vcc" << std::endl;
    throw;
  } // catch ( ... )
}



