
/* $Id: ofdm_sinr_interpolator.cc 620 2008-11-13 13:34:20Z zivkovic $ */

#ifdef HAVE_CONFIG_H
#include "config.h"
#endif
#include <gr_sync_block.h>
#include <gr_io_signature.h>
#include <ofdm_sinr_interpolator.h>
#include <string.h>
#include <iostream>

#define DEBUG 0


ofdm_sinr_interpolator::ofdm_sinr_interpolator(
  int vlen, int skip,
  const std::vector<int> &load_index )

  : gr_sync_block(
      "sinr_interpolator",
      gr_make_io_signature(
        1, 1,
        sizeof( float ) * vlen * (skip-1)/ skip ),
      gr_make_io_signature(
        1, 1,
        sizeof( float ) * ( vlen ) ) ),

  d_vlen( vlen ),
  d_skip( skip ),
  d_load_index( load_index )

{
  assert( d_vlen > 0 );
}

int ofdm_sinr_interpolator::work (
  int                         noutput_items,
  gr_vector_const_void_star & input_items,
  gr_vector_void_star       & output_items )
{
  const float *in = static_cast< const float* >( input_items[0] );
  float *out = static_cast< float* >( output_items[0] );

  const int partition_size = d_vlen/d_skip;


  for( int j = 0; j < noutput_items; ++j )
  {
	  //std::cout<<"Partition size: "<<partition_size<<std::endl;
    for( int i = 0; i < partition_size ; ++i )
    {
    	int dsubc = d_load_index[i];

    	if( dsubc == 0 )
    	{
    		//memcpy( out, in, 1*sizeof( float ) );
    		out[dsubc] = in[dsubc];
    		out += 1; //in += dsubc;
    		memcpy( out, in, (d_skip - 1) * sizeof( float ) );
    		out += d_skip-1; in += d_skip-1;
    	      }
    	else
      {
			//out[dsubc] = ((in[dsubc-i])+(in[dsubc-i-1]))/2.0;

    		//float x1 = in[dsubc-i];
    		//float x2 = in[dsubc-i-1];

    		//*(out) = (in[dsubc-i]+in[dsubc-i-1])/2.0;

    		*(out) = (*in + *(in-1))/2.0;

    		//float y0 = (*out);

    		//std::cout<<x1<<std::endl;
    		//std::cout<<x2<<std::endl;
    		//std::cout<<y0<<std::endl;

    		out += 1;
    		memcpy( out, in, (d_skip - 1) * sizeof( float ) );
    		out += d_skip-1; in += d_skip-1;
      }

    }

  }
  return noutput_items;
}


ofdm_sinr_interpolator_sptr
ofdm_make_sinr_interpolator( int vlen, int skip, const std::vector<int> &load_index )
{
  return ofdm_sinr_interpolator::create( vlen, skip, load_index );
}


ofdm_sinr_interpolator_sptr
ofdm_sinr_interpolator::create( int vlen, int skip,
  const std::vector<int> &load_index )
{
  try
  {
    ofdm_sinr_interpolator_sptr tmp(
      new ofdm_sinr_interpolator( vlen, skip, load_index ) );

    return tmp;
  }
  catch ( ... )
  {
    std::cerr << "[ERROR] Caught exception at creation of "
              << "ofdm_sinr_interpolator" << std::endl;
    throw;
  } // catch ( ... )
}



