
/* $Id: ofdm_autocorrelator.cc 923 2009-04-21 14:03:45Z auras $ */

#ifdef HAVE_CONFIG_H
#include "config.h"
#endif

#include <gr_sync_block.h>
#include <gr_hier_block2.h>
#include <gr_io_signature.h>
#include <ofdm_autocorrelator.h>

#include <ofdm_autocorrelator_stage1.h>
#include <ofdm_autocorrelator_stage2.h>

#include <iostream>

#define DEBUG 0


ofdm_autocorrelator ::
ofdm_autocorrelator( int lag, int n_samples )
  : gr_hier_block2(
      "autocorrelator",
      gr_make_io_signature(
        1, 1,
        sizeof( gr_complex ) ),
      gr_make_io_signature(
        1, 1,
        sizeof( float ) ) )

  , d_lag( lag )
  , d_n_samples( n_samples )

{
  ofdm_autocorrelator_stage1_sptr s1 =
    ofdm_make_autocorrelator_stage1( lag );

  ofdm_autocorrelator_stage2_sptr s2 =
    ofdm_make_autocorrelator_stage2( n_samples );

  connect( self(), 0, s1, 0 );
  connect( s1, 0, s2, 0 );
  connect( s1, 1, s2, 1 );
  connect( s2, 0, self(), 0 );

  d_s1 = s1;
  d_s2 = s2;
}


ofdm_autocorrelator_sptr
ofdm_make_autocorrelator( int lag, int n_samples )
{
  return ofdm_autocorrelator::create( lag, n_samples );
}


ofdm_autocorrelator_sptr
ofdm_autocorrelator ::
create( int lag, int n_samples )
{
  try
  {
    ofdm_autocorrelator_sptr tmp = gnuradio::get_initial_sptr(
      new ofdm_autocorrelator( lag, n_samples ) );

    return tmp;
  }
  catch ( ... )
  {
    std::cerr << "[ERROR] Caught exception at creation of "
              << "ofdm_autocorrelator" << std::endl;
    throw;
  } // catch ( ... )
}



