
/* $Id: ofdm_extract_block_from_frame.cc 923 2009-04-21 14:03:45Z auras $ */

#ifdef HAVE_CONFIG_H
#include "config.h"
#endif

#include <gr_block.h>
#include <gr_io_signature.h>
#include <ofdm_extract_block_from_frame.h>

#include <iostream>
#include <algorithm>

#define DEBUG 0


ofdm_extract_block_from_frame ::
ofdm_extract_block_from_frame( int vlen, int block_no )
  : gr_block(
      "extract_block_from_frame",
      gr_make_io_signature2(
        2, 2,
        sizeof( gr_complex ) * vlen,
        sizeof( char ) ),
      gr_make_io_signature(
        1, 1,
        sizeof( gr_complex ) * vlen ) )

  , d_vlen( vlen )
  , d_block_no( block_no )

  , d_ctr( block_no + 1 )
{
}


void
ofdm_extract_block_from_frame ::
forecast(
  int             noutput_items,
  gr_vector_int & ninput_items_required )
{
  ninput_items_required[0] = ninput_items_required[1] = 1;
}


int
ofdm_extract_block_from_frame ::
general_work(
  int                         noutput_items,
  gr_vector_int             & ninput_items,
  gr_vector_const_void_star & input_items,
  gr_vector_void_star       & output_items )
{
  gr_complex const * in = static_cast< gr_complex const * >( input_items[0] );
  char const * frame_start = static_cast< char const * >( input_items[1] );
  gr_complex * out = static_cast< gr_complex * >( output_items[0] );

  int produced = 0;

  int const nin = std::min( ninput_items[0], ninput_items[1] );

  int i = 0;
  for( ; i < nin; ++i )
  {
    if( frame_start[i] != 0 )
    {
      d_ctr == 0;
    }

    if( d_ctr < d_block_no )
    {
      ++d_ctr;
    }
    else if( d_ctr == d_block_no )
    {
      std::copy( in + i * d_vlen, in + ( i + 1 ) * d_vlen,
        out + produced * d_vlen );

      ++d_ctr;
      ++produced;

    } // if d_ctr < d_block_no

  } // for-loop over input

  consume( 0, i );
  consume( 1, i );

  return produced;

} // general_work


ofdm_extract_block_from_frame_sptr
ofdm_make_extract_block_from_frame( int vlen, int block_no )
{
  return ofdm_extract_block_from_frame::create( vlen, block_no );
}


ofdm_extract_block_from_frame_sptr
ofdm_extract_block_from_frame ::
create( int vlen, int block_no )
{
  try
  {
    ofdm_extract_block_from_frame_sptr tmp(
      new ofdm_extract_block_from_frame( vlen, block_no ) );

    return tmp;
  }
  catch ( ... )
  {
    std::cerr << "[ERROR] Caught exception at creation of "
              << "ofdm_extract_block_from_frame" << std::endl;
    throw;
  } // catch ( ... )
}



