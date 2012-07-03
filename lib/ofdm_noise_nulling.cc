
/* $Id: ofdm_sinr_interpolator.cc 620 2008-11-13 13:34:20Z zivkovic $ */

#ifdef HAVE_CONFIG_H
#include "config.h"
#endif
#include <gr_sync_block.h>
#include <gr_io_signature.h>
#include <ofdm_noise_nulling.h>
#include <string.h>
#include <iostream>

#define DEBUG 0


ofdm_noise_nulling::ofdm_noise_nulling(
  int vlen, int keep)

  : gr_sync_block(
      "noise_nulling",
      gr_make_io_signature(
        1, 1,
        sizeof(gr_complex) * vlen),
      gr_make_io_signature(
    		  1, 1,
        sizeof(gr_complex) * vlen) ),

  d_vlen( vlen ),
  d_keep( keep )

{
  assert( d_vlen > 0 );

}

int ofdm_noise_nulling::work (
  int                         noutput_items,
  gr_vector_const_void_star & input_items,
  gr_vector_void_star       & output_items )
{
  const gr_complex *in = static_cast< const gr_complex* >( input_items[0] );
  gr_complex *out = static_cast< gr_complex* >( output_items[0] );


  for( int j = 0; j < noutput_items; ++j)
  {

    for( int i = 0; i < d_vlen ; ++i )
    {

    	if ( i < d_keep+1)
    	{
    		out[i] = in[i];
    		out += 1;
    	}
    	else
    	{
    		out[i] = 0.0;
    		out += 1;
    	}

	}


  }
  return noutput_items;
}


ofdm_noise_nulling_sptr
ofdm_make_noise_nulling( int vlen, int keep)
{
  return ofdm_noise_nulling::create( vlen, keep);
}


ofdm_noise_nulling_sptr
ofdm_noise_nulling::create( int vlen, int keep)
{
  try
  {
    ofdm_noise_nulling_sptr tmp(
      new ofdm_noise_nulling( vlen, keep) );

    return tmp;
  }
  catch ( ... )
  {
    std::cerr << "[ERROR] Caught exception at creation of "
              << "ofdm_noise_nulling" << std::endl;
    throw;
  } // catch ( ... )
}



