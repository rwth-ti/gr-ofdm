
/* $Id: ofdm_pilot_subcarrier_inserter.cc 620 2008-11-13 13:34:20Z zivkovic $ */

#ifdef HAVE_CONFIG_H
#include "config.h"
#endif

#include <gr_sync_block.h>
#include <gr_io_signature.h>
#include <ofdm_pilot_subcarrier_inserter.h>
#include <string.h>
#include <iostream>

#define DEBUG 0


ofdm_pilot_subcarrier_inserter::ofdm_pilot_subcarrier_inserter(
  int vlen, const std::vector<gr_complex> &symbols,
  const std::vector<int> &subc_index )

  : gr_sync_block(
      "pilot_subcarrier_inserter",
      gr_make_io_signature(
        1, 1,
        sizeof( gr_complex ) * vlen ),
      gr_make_io_signature(
        1, 1,
        sizeof( gr_complex ) * ( vlen + symbols.size() ) ) ),

  d_vlen( vlen + symbols.size() ),
  d_symbols( symbols )

{
  assert( d_vlen > 0 );
  assert( symbols.size() > 0 );
  assert( symbols.size() == subc_index.size() );

  int last_ind = 0;
  int sum = 0;
  for( int i = 0; i < subc_index.size(); ++i)
  {
    const int subc_ind = subc_index[i] + d_vlen / 2;
    int p = subc_ind - last_ind;

    d_partition.push_back( p ); // data subcarriers
    sum += p + 1;

    last_ind = subc_ind + 1;
  } // for( int i = 0; i < subc_index.size(); ++i)

  d_partition.push_back( d_vlen - last_ind ); // data subcarriers
  sum += d_partition.back();

  assert( sum == d_vlen );
}

int
ofdm_pilot_subcarrier_inserter::work(
  int                         noutput_items,
  gr_vector_const_void_star & input_items,
  gr_vector_void_star       & output_items )
{
  const gr_complex *in = static_cast< const gr_complex* >( input_items[0] );
  gr_complex *out = static_cast< gr_complex* >( output_items[0] );

  const int partition_size = d_partition.size();

  for( int j = 0; j < noutput_items; ++j )
  {
    // copy data subcarrier partition and insert pilot subcarrier
    for( int i = 0; i < partition_size - 1; ++i )
    {
      const int dsubc = d_partition[i];

      out[dsubc] = d_symbols[i];
      if( dsubc > 0 )
      {
	memcpy( out, in, dsubc * sizeof( gr_complex ) );
	out += dsubc+1; in += dsubc;
      }

    } // for( int i = 0; i < partition_size - 1; ++i )

    // copy final data subcarrier partition
    const int dsubc = d_partition[ partition_size - 1 ];
    if( dsubc > 0 )
    {
      memcpy( out, in, dsubc * sizeof( gr_complex ) );
      out += dsubc; in += dsubc;
    }

  } // for( int j = 0; j < noutput_items; ++j )

  return noutput_items;
}


ofdm_pilot_subcarrier_inserter_sptr
ofdm_make_pilot_subcarrier_inserter( int vlen,
  const std::vector<gr_complex> &symbols, const std::vector<int> &subc_index )
{
  return ofdm_pilot_subcarrier_inserter::create( vlen, symbols, subc_index );
}


ofdm_pilot_subcarrier_inserter_sptr
ofdm_pilot_subcarrier_inserter::create( int vlen,
  const std::vector<gr_complex> &symbols, const std::vector<int> &subc_index )
{
  try
  {
    ofdm_pilot_subcarrier_inserter_sptr tmp(
      new ofdm_pilot_subcarrier_inserter( vlen, symbols, subc_index ) );

    return tmp;
  }
  catch ( ... )
  {
    std::cerr << "[ERROR] Caught exception at creation of "
              << "ofdm_pilot_subcarrier_inserter" << std::endl;
    throw;
  } // catch ( ... )
}



