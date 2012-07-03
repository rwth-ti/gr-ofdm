
/* $Id: ofdm_reassemble_ofdm_frame.cc 923 2009-04-21 14:03:45Z auras $ */

#ifdef HAVE_CONFIG_H
#include "config.h"
#endif

#include <gr_block.h>
#include <gr_io_signature.h>
#include <ofdm_reassemble_ofdm_frame.h>

#include <iostream>

#define DEBUG 0


ofdm_reassemble_ofdm_frame ::
ofdm_reassemble_ofdm_frame( int vlen, int framelength )
  : gr_block(
      "reassemble_ofdm_frame",
      gr_make_io_signature2(
        2, 2,
        sizeof( gr_complex ) * vlen,
        sizeof( char ) ),
      gr_make_io_signature(
        1, 1,
        sizeof( gr_complex ) * vlen ) )

  , d_vlen( vlen )
  , d_framelength( framelength )

  , d_blk( 0 )

{
  set_output_multiple( framelength );
  set_history( framelength );
}


void
ofdm_reassemble_ofdm_frame ::
forecast(
  int             noutput_items,
  gr_vector_int & ninput_items_required )
{
  ninput_items_required[0] = ninput_items_required[1] = d_framelength;
}


int
ofdm_reassemble_ofdm_frame ::
general_work(
  int                         noutput_items,
  gr_vector_int             & ninput_items,
  gr_vector_const_void_star & input_items,
  gr_vector_void_star       & output_items )
{
  gr_complex const * in = static_cast< gr_complex const * >( input_items[0] );
  char const * frame_start = static_cast< char const * >( input_items[1] );
  gr_complex * out = static_cast< gr_complex * >( output_items[0] );

  int const nin = std::min( ninput_items[0], ninput_items[1] )
                  - d_framelength + 1;
  int nout = noutput_items;

  int i = 0;
  for( ; i < nin; ++i )
  {
    if( frame_start[i] != 0 )
    {
      bool complete_frame = true;
      for( int j = 1; j < d_framelength; ++j )
      {
        if( frame_start[i+j] != 0 )
        {
          complete_frame = false;
          break;
        }
      } // for( int j = 1; j < d_framelength; ++j )

      if( ! complete_frame )
      {
        std::cout << "P"; // partial frame detected
        continue;
      }

      if( nout >= d_framelength )
      {
        std::copy( in + i * d_vlen, in + ( i + d_framelength ) * d_vlen, out );
        out += d_framelength * d_vlen;
        nout -= d_framelength;
      }
      else
      {
        break;
      }

    } // if( frame_start[i] != 0 )

  } // for-loop over input

  consume( 0, i );
  consume( 1, i );

  return noutput_items - nout;

} // general_work


ofdm_reassemble_ofdm_frame_sptr
ofdm_make_reassemble_ofdm_frame( int vlen, int framelength )
{
  return ofdm_reassemble_ofdm_frame::create( vlen, framelength );
}


ofdm_reassemble_ofdm_frame_sptr
ofdm_reassemble_ofdm_frame ::
create( int vlen, int framelength )
{
  try
  {
    ofdm_reassemble_ofdm_frame_sptr tmp(
      new ofdm_reassemble_ofdm_frame( vlen, framelength ) );

    return tmp;
  }
  catch ( ... )
  {
    std::cerr << "[ERROR] Caught exception at creation of "
              << "ofdm_reassemble_ofdm_frame" << std::endl;
    throw;
  } // catch ( ... )
}



