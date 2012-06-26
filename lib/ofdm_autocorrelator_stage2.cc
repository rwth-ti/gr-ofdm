
/* $Id: ofdm_autocorrelator_stage2.cc 923 2009-04-21 14:03:45Z auras $ */

#ifdef HAVE_CONFIG_H
#include "config.h"
#endif

#include <gr_sync_block.h>
#include <gr_io_signature.h>
#include <ofdm_autocorrelator_stage2.h>

#include <iostream>

#define DEBUG 0


ofdm_autocorrelator_stage2 ::
ofdm_autocorrelator_stage2( int n_samples )
  : gr_sync_block(
      "autocorrelator_stage2",
      gr_make_io_signature2(
        2, 2,
        sizeof( gr_complex ),
        sizeof( float ) ),
      gr_make_io_signature(
        1, 1,
        sizeof( float ) ) )

  , d_n_samples( n_samples )
  , d_delay( n_samples + 1 )
  , d_acc1( 0.0, 0.0 )
  , d_acc2( 0.0 )

{
  set_history( d_delay + 1 );
}

int
ofdm_autocorrelator_stage2 ::
work(
  int                         noutput_items,
  gr_vector_const_void_star & input_items,
  gr_vector_void_star       & output_items )
{
  gr_complex const * p_del =
    static_cast< gr_complex const * >( input_items[0] );
  gr_complex const * p = p_del + d_delay;

  float const * r_del = static_cast< float const * >( input_items[1] );
  float const * r = r_del + d_delay;

  float * out = static_cast< float * >( output_items[0] );

  // use local variable for accumulators, read recent values
  gr_complex acc1 = d_acc1;
  float      acc2 = d_acc2;

  // use references for simpler access
  float & x = acc1.real();
  float & y = acc1.imag();

  // NOTE: GCC performs better if we use temporary constants for
  // every expression

  for( int i = 0; i < noutput_items; ++i )
  {
    {
      gr_complex const t1 = p[i];
      gr_complex const t2 = p_del[i];
      gr_complex const t = t1 - t2;
      acc1 += t;
    }

    {
      float const t1 = r[i];
      float const t2 = r_del[i];
      float const t = t1 - t2;
      acc2 += t;
    }

    float const acc2_sq = acc2 * acc2;
    float const x2 = x*x; // squared real part of acc1
    float const y2 = y*y; // same for imaginary part
    float const x2y2 = x2 + y2;
    out[i] = x2y2 / acc2_sq;

  } // for-loop

  d_acc1 = acc1;
  d_acc2 = acc2;

  return noutput_items;
}


ofdm_autocorrelator_stage2_sptr
ofdm_make_autocorrelator_stage2( int n_samples )
{
  return ofdm_autocorrelator_stage2::create( n_samples );
}


ofdm_autocorrelator_stage2_sptr
ofdm_autocorrelator_stage2 ::
create( int n_samples )
{
  try
  {
    ofdm_autocorrelator_stage2_sptr tmp(
      new ofdm_autocorrelator_stage2( n_samples ) );

    return tmp;
  }
  catch ( ... )
  {
    std::cerr << "[ERROR] Caught exception at creation of "
              << "ofdm_autocorrelator_stage2" << std::endl;
    throw;
  } // catch ( ... )
}



