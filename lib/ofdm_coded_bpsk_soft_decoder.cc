
/* $Id: ofdm_coded_bpsk_soft_decoder.cc 1053 2009-07-02 14:15:21Z auras $ */

#ifdef HAVE_CONFIG_H
#include "config.h"
#endif

#include <gr_sync_block.h>
#include <gr_io_signature.h>
#include <ofdm_coded_bpsk_soft_decoder.h>

#include <iostream>
#include <algorithm>

#define DEBUG 0


ofdm_coded_bpsk_soft_decoder::ofdm_coded_bpsk_soft_decoder(
  int vlen, int output_bits, const std::vector<int>& whitener,
  std::vector< int > const & mask )

  : gr_sync_block(
      "coded_bpsk_soft_decoder",
      gr_make_io_signature(
        1, 1,
        sizeof( gr_complex ) * vlen ),
      gr_make_io_signature2(
        1, 2,
        sizeof( short ),
        sizeof( float ) ) ),

  d_vlen( vlen ),
  d_output_bits( output_bits )

{
  d_whitener.resize( whitener.size() );
  for( unsigned int i = 0; i < d_whitener.size(); ++i )
  {
    d_whitener[i] = -2.0 * static_cast< float >( whitener[i] ) + 1.0;
    // 1 -> -1.0
  }

//  assert( whitener.size() == (unsigned)vlen );
  assert( output_bits > 0 &&
          (unsigned) output_bits < ( sizeof( short ) * 8 - 1 ) );

  d_mask.resize( vlen, true );
  if( mask.size() != 0 )
  {
    for( unsigned int i = 0; i < mask.size(); ++i )
    {
      assert( mask[i] >= 0 );
      assert( mask[i] < d_mask.size() );
      d_mask[ mask[i] ] = false;
    }
  }
}

int
ofdm_coded_bpsk_soft_decoder::work(
  int                         noutput_items,
  gr_vector_const_void_star & input_items,
  gr_vector_void_star       & output_items )
{
  const gr_complex *in = static_cast< const gr_complex* >( input_items[0] );
  short *out = static_cast< short* >( output_items[0] );

  float * llr = 0;
  if( output_items.size() > 1 )
    llr = static_cast< float * >( output_items[1] );

  std::vector<float> softbits( d_output_bits, 0.0 );
  const int vlen = d_vlen;
  const int output_bits = d_output_bits;

  for( int i = 0; i < noutput_items; ++i )
  {
    softbits.assign( output_bits, 0.0 );

    int k = 0;
    // decode
    for( int j = 0; j < vlen; ++j )
    {
      if( d_mask[j] )
      {
        const int ind = k % output_bits;
        softbits[ind] += d_whitener[k] * std::real( in[j] );
        ++k;
      }
    } // for( int j = 0; j < vlen; ++j )

    // decide
    unsigned int val = 0;
    float cur_llr = INFINITY;
    for( int j = 0; j < output_bits; ++j )
    {
      if( softbits[j] < 0.0 )
      {
      	val = val | ( 1 << j );
      }
      cur_llr = std::min( cur_llr, std::abs( softbits[j] ) );

    } // for( int j = 0; j < output_bits; ++j )

    if( llr )
    {
      llr[i] = cur_llr;
      // FIXME: make threshold parameterizable
      // HACKED: using 10.0 as in python code, mimic threshold_ff
      if( cur_llr <= 10.0 )
        std::cout << "E";

    }

    out[i] = static_cast< short >( val );
    in += vlen;

  } // for( int i = 0; i < noutput_items; ++i )

  return noutput_items;
}


ofdm_coded_bpsk_soft_decoder_sptr
ofdm_make_coded_bpsk_soft_decoder( int vlen, int output_bits,
  const std::vector<int>& whitener, std::vector< int > const mask )
{
  return ofdm_coded_bpsk_soft_decoder::create( vlen, output_bits, whitener,
    mask );
}


ofdm_coded_bpsk_soft_decoder_sptr
ofdm_coded_bpsk_soft_decoder::create( int vlen, int output_bits,
  const std::vector<int>& whitener, std::vector< int > const mask )
{
  try
  {
    ofdm_coded_bpsk_soft_decoder_sptr tmp(
      new ofdm_coded_bpsk_soft_decoder( vlen, output_bits, whitener, mask ) );

    return tmp;
  }
  catch ( ... )
  {
    std::cerr << "[ERROR] Caught exception at creation of "
              << "ofdm_coded_bpsk_soft_decoder" << std::endl;
    throw;
  } // catch ( ... )
}



