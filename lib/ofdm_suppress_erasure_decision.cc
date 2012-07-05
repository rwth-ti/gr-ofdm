
/* $Id$ */

#ifdef HAVE_CONFIG_H
#include "config.h"
#endif

#include <gr_block.h>
#include <gr_io_signature.h>
#include <ofdm_suppress_erasure_decision.h>

#include <iostream>
#include <algorithm>

#define DEBUG 0


ofdm_suppress_erasure_decision ::
ofdm_suppress_erasure_decision(  )
  : gr_block(
      "suppress_erasure_decision",
      gr_make_io_signature(
        1, 1,
        sizeof( short ) ),
      gr_make_io_signature(
        1, 1,
        sizeof( short ) ) )
{
}


void
ofdm_suppress_erasure_decision ::
forecast(
  int             noutput_items,
  gr_vector_int & ninput_items_required )
{
  ninput_items_required[0] = 1;
}


int
ofdm_suppress_erasure_decision ::
general_work(
  int                         noutput_items,
  gr_vector_int             & ninput_items,
  gr_vector_const_void_star & input_items,
  gr_vector_void_star       & output_items )
{
  short const * in = static_cast< short const * >( input_items[0] );
  short * out = static_cast< short * >( output_items[0] );

  int prod = 0;
  int nout = noutput_items;
  int const nin = ninput_items[0];

  int i = 0;
  while( nout > 0 && i < nin )
  {
    if( in[i] >= 0 )
    {
      out[prod++] = in[i];
      --nout;
    }
    ++i;
  }


//  std::cout << "produce " << prod << " consume " << i << std::endl;

  consume( 0, i );
  return prod;
}


ofdm_suppress_erasure_decision_sptr
ofdm_make_suppress_erasure_decision(  )
{
  return ofdm_suppress_erasure_decision::create(  );
}


ofdm_suppress_erasure_decision_sptr
ofdm_suppress_erasure_decision ::
create(  )
{
  try
  {
    ofdm_suppress_erasure_decision_sptr tmp(
      new ofdm_suppress_erasure_decision(  ) );

    return tmp;
  }
  catch ( ... )
  {
    std::cerr << "[ERROR] Caught exception at creation of "
              << "ofdm_suppress_erasure_decision" << std::endl;
    throw;
  } // catch ( ... )
}



