
/* $Id: ofdm_int_skip.cc 620 2008-11-13 13:34:20Z zivkovic $ */

#ifdef HAVE_CONFIG_H
#include "config.h"
#endif
#include <gr_sync_block.h>
#include <gr_io_signature.h>
#include "ofdm_int_skip.h"
#include <string.h>
#include <iostream>

#define DEBUG 0


ofdm_int_skip::ofdm_int_skip(
  int vlen, int skip, int start)

  : gr_sync_block(
      "int_skip",
      gr_make_io_signature(
        1, 1,
        sizeof(gr_complex) * vlen),
      gr_make_io_signature(
        1, 1,
        sizeof(gr_complex)*vlen/skip ) ),
  d_vlen( vlen ),
  d_skip( skip ),
  d_start( start )

{
  assert( d_vlen > 0 );

}

int ofdm_int_skip::work (
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


    	if ( i % d_skip == 0 )
    	{
    		*out = in[i+d_start];
    		 out += 1;
    	}


	}

  }
  return noutput_items;
}


ofdm_int_skip_sptr
ofdm_make_int_skip( int vlen, int skip, int start)
{
  return ofdm_int_skip::create( vlen, skip, start);
}


ofdm_int_skip_sptr
ofdm_int_skip::create( int vlen, int skip, int start)
{
  try
  {
    ofdm_int_skip_sptr tmp(
      new ofdm_int_skip( vlen, skip, start) );

    return tmp;
  }
  catch ( ... )
  {
    std::cerr << "[ERROR] Caught exception at creation of "
              << "ofdm_int_skip" << std::endl;
    throw;
  } // catch ( ... )
}



