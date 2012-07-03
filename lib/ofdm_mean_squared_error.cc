
/* $Id$ */

#ifdef HAVE_CONFIG_H
#include "config.h"
#endif

#include <gr_block.h>
#include <gr_io_signature.h>
#include <ofdm_mean_squared_error.h>

#include <iostream>


#define DEBUG 0


ofdm_mean_squared_error::ofdm_mean_squared_error( int vlen,
  unsigned long window, bool reset, double norm_factor )

  : gr_block(
      "mean_squared_error",
      gr_make_io_signature(
        1, 1,
        sizeof( gr_complex ) * vlen ),
      gr_make_io_signature(
        1, 1,
        sizeof( float ) ) ),

  d_vlen( vlen ),
  d_window( window ),
  d_reset( reset ),
  d_norm_factor( norm_factor ),
  d_cnt( window ),
  d_acc( 0.0 )


{
  if( DEBUG > 0 )
    std::cout << "[ofdm mean_squared_error(" << unique_id() << ")] : window = "
              << window << " norm_factor = " << norm_factor << " vlen = "
              << vlen << std::endl;
}


void
ofdm_mean_squared_error::forecast( int noutput_items,
  gr_vector_int &ninput_items_required )
{
  ninput_items_required[0] = d_cnt > 0UL ? 1 : 0;
}


int
ofdm_mean_squared_error::general_work(
  int                         noutput_items,
  gr_vector_int             & ninput_items,
  gr_vector_const_void_star & input_items,
  gr_vector_void_star       & output_items )
{
  const float * in = static_cast< const float* >( input_items[0] );
  float * out = static_cast< float* >( output_items[0] );

  if( d_cnt == 0 && ! d_reset )
  {
    return -1;
  }

  unsigned long const avail = static_cast< unsigned long >( ninput_items[0] );

  unsigned int i_max = 0;
  if( d_cnt > avail )
  {
    i_max = ninput_items[0];
  }
  else
  {
    i_max = static_cast< unsigned int >( d_cnt );
  }

  unsigned int const consumed = i_max;

  i_max *= 2 * d_vlen; // complex stream treated as float stream

  double acc = 0.0;
  for( unsigned int i = 0; i < i_max; ++i )
  {
    float const x = in[i]*in[i];
    acc += x;
  }
  d_acc += acc;

  d_cnt -= static_cast< unsigned long >( consumed );
  consume( 0, consumed );

  if( d_cnt == 0 )
  {
    assert( noutput_items >  0 );
    out[0] = static_cast< float >( d_acc / d_norm_factor );

    if( d_reset )
    {
      d_cnt = d_window;
      d_acc = 0.0;
    }

    return 1;

  } // if( d_cnt == 0 )

  return 0;
}


ofdm_mean_squared_error_sptr
ofdm_make_mean_squared_error( int vlen, unsigned long window, bool reset,
  double norm_factor )
{
  return ofdm_mean_squared_error::create( vlen, window, reset, norm_factor );
}


ofdm_mean_squared_error_sptr
ofdm_mean_squared_error::create( int vlen, unsigned long window, bool reset,
  double norm_factor )
{
  try
  {
    ofdm_mean_squared_error_sptr tmp(
      new ofdm_mean_squared_error( vlen, window, reset, norm_factor ) );

    return tmp;
  }
  catch ( ... )
  {
    std::cerr << "[ERROR] Caught exception at creation of "
              << "ofdm_mean_squared_error" << std::endl;
    throw;
  } // catch ( ... )
}



