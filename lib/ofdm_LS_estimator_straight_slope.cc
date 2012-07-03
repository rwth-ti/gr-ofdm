
/* $Id: ofdm_LS_estimator_straight_slope.cc 1110 2009-08-27 20:41:54Z auras $ */

#ifdef HAVE_CONFIG_H
#include "config.h"
#endif

#include <gr_sync_block.h>
#include <gr_io_signature.h>
#include <ofdm_LS_estimator_straight_slope.h>

#include <iostream>

#define DEBUG 0


ofdm_LS_estimator_straight_slope ::
ofdm_LS_estimator_straight_slope( int vlen )
  : gr_sync_block(
      "LS_estimator_straight_slope",
      gr_make_io_signature(
        1, 1,
        sizeof( float ) * vlen ),
      gr_make_io_signature(
        2, 2,
        sizeof( float ) ) )

  , d_vlen( vlen )
  , d_slope_coeff( vlen )
  , d_offset_coeff( vlen )

{
  double ind_squares = 0.0;
  double ind_offset = 0.0;
  for( int i = -vlen/2; i < vlen/2; ++i )
  {
    double di = static_cast< double >( i );
    ind_squares += di * di;
    ind_offset += di;
  }
  double N = vlen;
  double normc = ind_squares * N - ind_offset * ind_offset;
  double slope_coeff_slope = N / normc;
  double slope_coeff_offset = -ind_offset / normc;
  double offset_coeff_slope = - slope_coeff_slope;
  double offset_coeff_offset = ind_squares / normc;

//  std::cout << "####" << slope_coeff_slope << ":" << slope_coeff_offset << std::endl;

  for( int i = 0; i < vlen; ++i )
  {
    double di = static_cast< double >( i );
    d_slope_coeff[i] = slope_coeff_slope * ( di - N/2 ) + slope_coeff_offset;
    d_offset_coeff[i] = offset_coeff_slope * ( di - N/2 ) + offset_coeff_offset;
  }

//  float aa= 0;
//  for( int i = 0; i < vlen; ++i )
//  {
//    float fi = static_cast< double >( i ) - N/2;
//    aa += fi * d_slope_coeff[i];
//  }
//  std::cout << "''''" << aa << std::endl;
}

int
ofdm_LS_estimator_straight_slope ::
work(
  int                         noutput_items,
  gr_vector_const_void_star & input_items,
  gr_vector_void_star       & output_items )
{
  float const * in = static_cast< float const * >( input_items[0] );
  float * slope = static_cast< float * >( output_items[0] );
  float * offset = static_cast< float * >( output_items[1] );

  for( int i = 0; i < noutput_items; ++i, in += d_vlen )
  {
    float a = 0;
    float b = 0;
    for( int j = 0; j < d_vlen; ++j )
    {
      a += d_slope_coeff[j] * in[j];
      b += d_offset_coeff[j] * in[j];
    }
    slope[i] = a;
    offset[i] = b;
  }

  return noutput_items;
}


ofdm_LS_estimator_straight_slope_sptr
ofdm_make_LS_estimator_straight_slope( int vlen )
{
  return ofdm_LS_estimator_straight_slope::create( vlen );
}


ofdm_LS_estimator_straight_slope_sptr
ofdm_LS_estimator_straight_slope ::
create( int vlen )
{
  try
  {
    ofdm_LS_estimator_straight_slope_sptr tmp(
      new ofdm_LS_estimator_straight_slope( vlen ) );

    return tmp;
  }
  catch ( ... )
  {
    std::cerr << "[ERROR] Caught exception at creation of "
              << "ofdm_LS_estimator_straight_slope" << std::endl;
    throw;
  } // catch ( ... )
}



