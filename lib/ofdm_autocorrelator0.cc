
/* $Id: ofdm_autocorrelator0.cc 923 2009-04-21 14:03:45Z auras $ */

#ifdef HAVE_CONFIG_H
#include "config.h"
#endif

#include <gr_sync_block.h>
#include <gr_hier_block2.h>
#include <gr_io_signature.h>
#include <ofdm_autocorrelator0.h>

#include <ofdm_autocorrelator_stage1.h>
#include <ofdm_autocorrelator_stage2.h>

#include <iostream>

#define DEBUG 0


ofdm_autocorrelator0 ::
ofdm_autocorrelator0( int lag, int n_samples )
  : gr_hier_block2("autocorrelator0",
    gr_make_io_signature(1, 1,sizeof( gr_complex ) ),
    gr_make_io_signature(1, 1,sizeof( float ) ) ) ,

    d_lag( lag ),
    d_n_samples( n_samples ),
    d_s1(ofdm_make_autocorrelator_stage1( lag )),
    d_s2(ofdm_make_autocorrelator_stage2( n_samples ))

{
/*
    ofdm_autocorrelator_stage1_sptr s1 =
    ofdm_make_autocorrelator_stage1( lag );

  ofdm_autocorrelator_stage2_sptr s2 =
    ofdm_make_autocorrelator_stage2( n_samples );
*/
  connect( self(), 0, d_s1, 0 );
  connect( d_s1, 0, d_s2, 0 );
  connect( d_s1, 1, d_s2, 1 );
  connect( d_s2, 0, self(), 0 );
/*
  d_s1 = s1;
  d_s2 = s2;
  */

}


ofdm_autocorrelator0_sptr
ofdm_make_autocorrelator0( int lag, int n_samples )
{
  return ofdm_autocorrelator0::create( lag, n_samples );
}


ofdm_autocorrelator0_sptr
ofdm_autocorrelator0 ::
create( int lag, int n_samples )
{
  try
  {
    ofdm_autocorrelator0_sptr tmp = gnuradio::get_initial_sptr(
      new ofdm_autocorrelator0( lag, n_samples ) );

    return tmp;
  }
  catch ( ... )
  {
    std::cerr << "[ERROR] Caught exception at creation of "
              << "ofdm_autocorrelator0" << std::endl;
    throw;
  }
}



