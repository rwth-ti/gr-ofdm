
/* $Id: ofdm_postprocess_CTF_estimate.cc 923 2009-04-21 14:03:45Z auras $ */

#ifdef HAVE_CONFIG_H
#include "config.h"
#endif

#include <gr_sync_block.h>
#include <gr_io_signature.h>
#include <ofdm_postprocess_CTF_estimate.h>

#include <iostream>

#define DEBUG 0


ofdm_postprocess_CTF_estimate ::
ofdm_postprocess_CTF_estimate( int vlen )
  : gr_sync_block(
      "postprocess_CTF_estimate",
      gr_make_io_signature(
        1, 1,
        sizeof( gr_complex ) * vlen ),
      gr_make_io_signature2(
        2, 2,
        sizeof( gr_complex ) * vlen,
        sizeof( float ) * vlen ) )

  , d_vlen( vlen )

{
  assert( ( vlen % 2 ) == 0 ); // alignment requirement
}


int
ofdm_postprocess_CTF_estimate ::
work(
  int                         noutput_items,
  gr_vector_const_void_star & input_items,
  gr_vector_void_star       & output_items )
{
  gr_complex const * in = static_cast< gr_complex const * >( input_items[0] );
  gr_complex * inv_ctf = static_cast< gr_complex * >( output_items[0] );
  float * disp_ctf = static_cast< float * >( output_items[1] );


  for( int i = 0; i < noutput_items;
       ++i, in += d_vlen, inv_ctf += d_vlen, disp_ctf += d_vlen )
  {
    float acc = 0.0;
    gr_complex const one( 1.0, 0.0 );

    // TODO: good candidate for vectorization
    for( int j = 0; j < d_vlen; ++j )
    {
      gr_complex const val = in[j];

      float const & __x = val.real();
      float const & __y = val.imag();

      float const t = __x*__x + __y*__y;

      disp_ctf[j] = t;
      acc += t;

      // best example for strength reduction: 2x speedup
      inv_ctf[j] = std::conj( in[j] ) / t;
//      inv_ctf[j] = one / in[j]; // = conj(in[j])/|in[j]|^2
//                                // |in[j]|^2 = t
    }

    float const f = static_cast< float >( d_vlen ) / acc;
    for( int j = 0; j < d_vlen; ++j )
    {
      disp_ctf[j] *= f;
    }

  } // for-loop over input

  if( DEBUG )
    std::cout << "POST: leave, nout=" << noutput_items << std::endl;


  return noutput_items;

} // work


ofdm_postprocess_CTF_estimate_sptr
ofdm_make_postprocess_CTF_estimate( int vlen )
{
  return ofdm_postprocess_CTF_estimate::create( vlen );
}


ofdm_postprocess_CTF_estimate_sptr
ofdm_postprocess_CTF_estimate ::
create( int vlen )
{
  try
  {
    ofdm_postprocess_CTF_estimate_sptr tmp(
      new ofdm_postprocess_CTF_estimate( vlen ) );

    return tmp;
  }
  catch ( ... )
  {
    std::cerr << "[ERROR] Caught exception at creation of "
              << "ofdm_postprocess_CTF_estimate" << std::endl;
    throw;
  } // catch ( ... )
}



