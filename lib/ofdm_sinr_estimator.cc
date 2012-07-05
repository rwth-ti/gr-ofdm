
/* $Id: ofdm_sinr_interpolator.cc 620 2008-11-13 13:34:20Z zivkovic $ */

#ifdef HAVE_CONFIG_H
#include "config.h"
#endif
#include <gr_sync_block.h>
#include <gr_io_signature.h>
#include <ofdm_sinr_estimator.h>
#include <string.h>
#include <iostream>

#define DEBUG 0


ofdm_sinr_estimator::ofdm_sinr_estimator(
  int vlen, int skip)

  : gr_sync_block(
      "sinr_estimator",
      gr_make_io_signature(
        2, 2,
        sizeof(gr_complex) * vlen),
      gr_make_io_signature(
        1, 1,
        sizeof( float )*vlen*(skip-1)/ skip) ),

  d_vlen( vlen ),
  d_skip( skip )

{
  assert( d_vlen > 0 );
  d_taps.reset(new float[vlen]);
  d_taps1.reset(new float[vlen]);
   for(int i = 0; i < vlen; ++i){
     d_taps[i] = 1.0;
     d_taps1[i] = 1.0;
   }

}

int ofdm_sinr_estimator::work (
  int                         noutput_items,
  gr_vector_const_void_star & input_items,
  gr_vector_void_star       & output_items )
{
  const gr_complex *in = static_cast< const gr_complex* >( input_items[0] );
  const gr_complex *in1 = static_cast< const gr_complex* >( input_items[1] );
  float *out = static_cast< float* >( output_items[0] );


  for( int j = 0; j < noutput_items; ++j)
  {

	//float null_0=0;
	//float null_1=0;
	float estim = 0.0;
	//float square = 0.0;

    for( int i = 0; i < d_vlen ; ++i )
    {


    	if ( i % d_skip != 0 )
    	{
    		/*null_0 = in[i].real()*in[i].real() + in[i].imag()*in[i].imag();
    		null_1 = in1[i].real()*in1[i].real() + in1[i].imag()*in1[i].imag();
    		estim = null_1/null_0 - 1;
    		*out = static_cast<float>(estim);
    		out += 1;*/

    		d_taps[i] = 0.01*(in[i].real()*in[i].real() + in[i].imag()*in[i].imag()) + 0.99*d_taps[i];
    		d_taps1[i] = 0.01*(in1[i].real()*in1[i].real() + in1[i].imag()*in1[i].imag()) + 0.99*d_taps1[i];
    		estim = d_taps1[i]/d_taps[i] - 1;

    		*out = (estim);
    		 out += 1;
    	}
	}

  }
  return noutput_items;
}


ofdm_sinr_estimator_sptr
ofdm_make_sinr_estimator( int vlen, int skip)
{
  return ofdm_sinr_estimator::create( vlen, skip);
}


ofdm_sinr_estimator_sptr
ofdm_sinr_estimator::create( int vlen, int skip)
{
  try
  {
    ofdm_sinr_estimator_sptr tmp(
      new ofdm_sinr_estimator( vlen, skip) );

    return tmp;
  }
  catch ( ... )
  {
    std::cerr << "[ERROR] Caught exception at creation of "
              << "ofdm_sinr_estimator" << std::endl;
    throw;
  } // catch ( ... )
}



