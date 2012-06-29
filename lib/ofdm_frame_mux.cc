
/* $Id$ */

#ifdef HAVE_CONFIG_H
#include "config.h"
#endif

#include <gr_block.h>
#include <gr_io_signature.h>
#include <ofdm_frame_mux.h>

#include <iostream>

#include <malloc16.h>
#include <cstring>

#define DEBUG 0

typedef float v4sf __attribute__ ((vector_size(16)));
typedef v4sf * v4sf_ptr __attribute__ ((aligned(16)));
typedef v4sf const * v4sfc_ptr __attribute__ ((aligned(16)));



ofdm_frame_mux ::
ofdm_frame_mux( int vlen, int frame_len )
  : gr_block(
      "frame_mux",
      gr_make_io_signature(
        1, 1,
        sizeof( gr_complex ) * vlen ),
      gr_make_io_signature(
        1, 1,
        sizeof( gr_complex ) * vlen ) )

  , d_vlen( vlen )
  , d_frame_len( frame_len )
  , d_preambles( 0 )
  , d_data_blocks( frame_len )
  , d_frame_head( 0 )
  , d_head_size( 0 )

{
  update();

  assert( ( vlen % 2 ) == 0 ); // -> 16 bytes
}

ofdm_frame_mux ::
~ofdm_frame_mux()
{
  if( d_head_size > 0 )
  {
    free16Align( d_frame_head );
  }
}

void
ofdm_frame_mux ::
add_preamble( std::vector< gr_complex > const & vec )
{
  assert( vec.size() == d_vlen );

  std::cout << "add preamble" << std::endl;
  std::cout << "head size is " << d_head_size << std::endl;

  size_type const new_head_size = d_head_size + d_vlen * sizeof( gr_complex );

  std::cout << "new head size is " << new_head_size << std::endl;

  cache_ptr new_head =
    static_cast< cache_ptr >( malloc16Align( new_head_size ) );

  if( d_head_size > 0 )
  {
    memcpy( new_head, d_frame_head, d_head_size );
    free16Align( d_frame_head );
    std::cout << "copy old head to new head" << std::endl;
  }

  memcpy( new_head + d_head_size / sizeof( float ),
          vec.data(), d_vlen * sizeof( gr_complex ) );

  d_head_size = new_head_size;
  d_frame_head = new_head;

  ++d_preambles;
  d_data_blocks = d_frame_len - d_preambles;

  std::cout << "preambles " << d_preambles << " data blocks " << d_data_blocks
            << " framelen " << d_frame_len << std::endl;

  update();
}

void
ofdm_frame_mux ::
update()
{
  set_output_multiple( d_frame_len );
  set_relative_rate( static_cast< double >( d_frame_len ) /
                     static_cast< double >( d_data_blocks ) );
  d_data_size = d_vlen * sizeof( gr_complex ) * d_data_blocks;
}


void
ofdm_frame_mux ::
forecast(
  int             noutput_items,
  gr_vector_int & ninput_items_required )
{
  ninput_items_required[ 0 ] = noutput_items / d_frame_len * d_data_blocks;
}


int
ofdm_frame_mux ::
general_work(
  int                         noutput_items,
  gr_vector_int             & ninput_items,
  gr_vector_const_void_star & input_items,
  gr_vector_void_star       & output_items )
{
  v4sfc_ptr __restrict in = static_cast< v4sfc_ptr >( input_items[0] );
  v4sf_ptr __restrict out = static_cast< v4sf_ptr >( output_items[0] );
  v4sfc_ptr __restrict fh = reinterpret_cast< v4sfc_ptr >( d_frame_head );

//  assert( ( (int)in & 15 ) == 0 );
//  assert( ( (int)out & 15 ) == 0 );
//  assert( ( (int)fh & 15 ) == 0 );


  size_type const nframes = noutput_items / d_frame_len;
  size_type const head_size = d_head_size / 16; // because d_vlen % 2 == 0
  size_type const data_size = d_data_size / 16;

  for( size_type i = 0; i < nframes; ++i )
  {
    for( size_type j = 0; j < head_size; ++j )
    {
      out[ j ] = fh[ j ];
    }
    out += head_size;

    for( size_type j = 0; j < data_size; ++j )
    {
      out[ j ] = in[ j ];
    }
    out += data_size;
    in += data_size;
  }

  consume( 0, nframes * d_data_blocks );

  return nframes * d_frame_len;
}


ofdm_frame_mux_sptr
ofdm_make_frame_mux( int vlen, int frame_len )
{
  return ofdm_frame_mux::create( vlen, frame_len );
}


ofdm_frame_mux_sptr
ofdm_frame_mux ::
create( int vlen, int frame_len )
{
  try
  {
    ofdm_frame_mux_sptr tmp(
      new ofdm_frame_mux( vlen, frame_len ) );

    return tmp;
  }
  catch ( ... )
  {
    std::cerr << "[ERROR] Caught exception at creation of "
              << "ofdm_frame_mux" << std::endl;
    throw;
  } // catch ( ... )
}



