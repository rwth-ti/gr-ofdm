
/* $Id: ofdm_sinr_interpolator.cc 620 2008-11-13 13:34:20Z zivkovic $ */

#ifdef HAVE_CONFIG_H
#include "config.h"
#endif
#include <gr_sync_block.h>
#include <gr_io_signature.h>
#include <ofdm_snr_estimator.h>
#include <string.h>
#include <iostream>

#define DEBUG 0


ofdm_snr_estimator::ofdm_snr_estimator(
  int vlen, int skip)

  : gr_sync_block(
      "snr_estimator",
      gr_make_io_signature(
        1, 1,
        sizeof(gr_complex) * vlen),
      gr_make_io_signature(
        2, 2,
        sizeof( float ) ) ),

  d_vlen( vlen ),
  d_skip( skip )

{
  assert( d_vlen > 0 );

}

int ofdm_snr_estimator::work (
  int                         noutput_items,
  gr_vector_const_void_star & input_items,
  gr_vector_void_star       & output_items )
{
  const gr_complex *in = static_cast< const gr_complex* >( input_items[0] );
  float *out = static_cast< float* >( output_items[0] );
  float *out1 = static_cast< float* >( output_items[1] );


  for( int j = 0; j < noutput_items; ++j)
  {

	float sum_load=0;
	float sum_null=0;
	float estim = 0.0;
	float estim_noise = 0.0;
	float square = 0.0;

    for( int i = 0; i < d_vlen ; ++i )
    {
    	//square = std::abs(in[i]*std::conj(in[i]));
    	square = in[i].real()*in[i].real() + in[i].imag()*in[i].imag();

    	if ( i % d_skip == 0 )
    	{
    	   sum_load+=square;
    	}
    	else
    	{
           sum_null+=square;
    	}

	}

    estim =(1./d_skip)*((d_skip-1)*sum_load/sum_null-1);
    estim_noise = sum_null*d_skip/(d_skip-1)/d_vlen;
    out[j] = static_cast<float>(estim);
    out1[j] = static_cast<float>(estim_noise);

  }
  return noutput_items;
}


ofdm_snr_estimator_sptr
ofdm_make_snr_estimator( int vlen, int skip)
{
  return ofdm_snr_estimator::create( vlen, skip);
}


ofdm_snr_estimator_sptr
ofdm_snr_estimator::create( int vlen, int skip)
{
  try
  {
    ofdm_snr_estimator_sptr tmp(
      new ofdm_snr_estimator( vlen, skip) );

    return tmp;
  }
  catch ( ... )
  {
    std::cerr << "[ERROR] Caught exception at creation of "
              << "ofdm_snr_estimator" << std::endl;
    throw;
  } // catch ( ... )
}



