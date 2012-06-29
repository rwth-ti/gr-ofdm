
/* $Id: ofdm_compat_read_ber_from_imgxfer.cc 829 2009-02-25 12:30:54Z auras $ */

#ifdef HAVE_CONFIG_H
#include "config.h"
#endif

#include <gr_block.h>
#include <gr_io_signature.h>
#include <ofdm_compat_read_ber_from_imgxfer.h>

#include <iostream>

#define DEBUG 0

#include <ofdm_imgtransfer_sink.h>






ofdm_compat_read_ber_from_imgxfer ::
ofdm_compat_read_ber_from_imgxfer( ofdm_imgtransfer_sink_sptr xfersink )
  : gr_block(
      "compat_read_ber_from_imgxfer",
      gr_make_io_signature(
        1, 1,
        sizeof( char ) ),
      gr_make_io_signature(
        1, 1,
        sizeof( float ) ) )

  , d_xfersink( xfersink )

{
}


void
ofdm_compat_read_ber_from_imgxfer ::
forecast(
  int             noutput_items,
  gr_vector_int & ninput_items_required )
{
  ninput_items_required[0] = 1;
}


int
ofdm_compat_read_ber_from_imgxfer ::
general_work(
  int                         noutput_items,
  gr_vector_int             & ninput_items,
  gr_vector_const_void_star & input_items,
  gr_vector_void_star       & output_items )
{
  char const * in = static_cast< char const * >( input_items[0] );
  float * out = static_cast< float * >( output_items[0] );

  int nout = noutput_items;
  int i = 0;
  for( ; i < ninput_items[0]; ++i )
  {
    if( in[i] != 0 )
    {
      if( nout == 0 )
        break;

      float const ber = d_xfersink->get_BER_estimate();
      *out = ber;
      --nout;
      ++out;

    } // if in[i] != 0

  } // for-loop over input

  consume( 0 , i );

  return noutput_items - nout;

} // general_work


ofdm_compat_read_ber_from_imgxfer_sptr
ofdm_make_compat_read_ber_from_imgxfer( ofdm_imgtransfer_sink_sptr xfersink )
{
  return ofdm_compat_read_ber_from_imgxfer::create( xfersink );
}


ofdm_compat_read_ber_from_imgxfer_sptr
ofdm_compat_read_ber_from_imgxfer ::
create( ofdm_imgtransfer_sink_sptr xfersink )
{
  try
  {
    ofdm_compat_read_ber_from_imgxfer_sptr tmp(
      new ofdm_compat_read_ber_from_imgxfer( xfersink ) );

    return tmp;
  }
  catch ( ... )
  {
    std::cerr << "[ERROR] Caught exception at creation of "
              << "ofdm_compat_read_ber_from_imgxfer" << std::endl;
    throw;
  } // catch ( ... )
}



