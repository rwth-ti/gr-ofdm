
/* $Id: ofdm_sinr_interpolator.cc 620 2008-11-13 13:34:20Z zivkovic $ */

#ifdef HAVE_CONFIG_H
#include "config.h"
#endif
#include <gr_sync_block.h>
#include <gr_io_signature.h>
#include <ofdm_sinr_estimator2.h>
#include <string.h>
#include <iostream>

#define DEBUG 0


ofdm_sinr_estimator2::ofdm_sinr_estimator2(
  int vlen, int skip)

  : gr_sync_block(
      "sinr_estimator2",
      gr_make_io_signature(
        2, 2,
        sizeof(gr_complex) * vlen),
      gr_make_io_signature2(
        2, 2,
        sizeof( float )* vlen, sizeof( float )) ),

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

int ofdm_sinr_estimator2::work (
  int                         noutput_items,
  gr_vector_const_void_star & input_items,
  gr_vector_void_star       & output_items )
{
  const gr_complex *in = static_cast< const gr_complex* >( input_items[0] );
  const gr_complex *in1 = static_cast< const gr_complex* >( input_items[1] );
  float *out = static_cast< float* >( output_items[0] );
  float *out1 = static_cast< float* >( output_items[1] );


  for( int j = 0; j < noutput_items; ++j)
  {

	//float null_0=0;
	//float null_1=0;
	float estim = 0.0;
	float estim_av_snr = 0.0;
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

    		if ( i % d_skip == 1  )
    		        {
    		        	if (i == 1)
    		        	{
    		        		*out = (estim);
    		        		*(out+1) = (estim);
    		        		out += 2;
    		        		estim_av_snr += 2*estim;
    		        	}
    		        	else
    		        	{
    		        		*out = ((estim + *(out-1))/2.0);
    		        		*(out+1) = (estim);
    		        		out += 2;
    		        		estim_av_snr += 2*estim;
    		        	}

    		        }
    		else
    		{
    		*out = (estim);
    		out += 1;
    		estim_av_snr += estim;
    		}
    	}
	}

    /*estim =(1./d_skip)*((d_skip-1)*sum_load/sum_null-1);
    estim_noise = sum_null/d_skip*(d_skip-1);
    out[j] = static_cast<float>(estim);
    out1[j] = static_cast<float>(estim_noise);*/

    out1[j] = static_cast<float>(estim_av_snr/d_vlen);

  }
  return noutput_items;
}


ofdm_sinr_estimator2_sptr
ofdm_make_sinr_estimator2( int vlen, int skip)
{
  return ofdm_sinr_estimator2::create( vlen, skip);
}


ofdm_sinr_estimator2_sptr
ofdm_sinr_estimator2::create( int vlen, int skip)
{
  try
  {
    ofdm_sinr_estimator2_sptr tmp(
      new ofdm_sinr_estimator2( vlen, skip) );

    return tmp;
  }
  catch ( ... )
  {
    std::cerr << "[ERROR] Caught exception at creation of "
              << "ofdm_sinr_estimator2" << std::endl;
    throw;
  } // catch ( ... )
}



