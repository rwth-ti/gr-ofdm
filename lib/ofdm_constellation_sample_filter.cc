
/* $Id: ofdm_constellation_sample_filter.cc 620 2008-11-13 13:34:20Z zivkovic $ */

#ifdef HAVE_CONFIG_H
#include "config.h"
#endif

#include <gr_block.h>
#include <gr_io_signature.h>
#include <ofdm_constellation_sample_filter.h>
#include <string.h>
#include <iostream>
#include <algorithm>

#define DEBUG 0


ofdm_constellation_sample_filter::ofdm_constellation_sample_filter( int arity, 
    int vlen )

  : gr_block(
      "constellation_sample_filter",
      gr_make_io_signature3( 
        3, 3,
        sizeof( gr_complex ) * vlen,        // ofdm blocks
        sizeof( char ) * vlen,              // bitmap
        sizeof( char ) ),                   // trigger
      gr_make_io_signature( 
        1, 1,
        sizeof( gr_complex ) ) ),           // filtered samples

  d_arity( arity ),
  d_vlen( vlen ),
  d_need_bitmap( 1 ),
  d_bitmap( new char[vlen] )

{
  for( int i = 0; i < vlen; ++i )
  {
    d_bitmap[i] = 0;
  }
}


void
ofdm_constellation_sample_filter::forecast( int noutput_items, 
  gr_vector_int &ninput_items_required )
{
  ninput_items_required[0] = 1;
  ninput_items_required[1] = d_need_bitmap;
  ninput_items_required[2] = 1;
}


int
ofdm_constellation_sample_filter::general_work(
  int                         noutput_items,
  gr_vector_int             & ninput_items,
  gr_vector_const_void_star & input_items,
  gr_vector_void_star       & output_items )
{
  const gr_complex *sym_in = static_cast< const gr_complex* >( input_items[0] );
  const char *map_in = static_cast< const char* >( input_items[1] );
  const char *trig = static_cast< const char* >( input_items[2] );
  gr_complex *sym_out = static_cast< gr_complex* >( output_items[0] );
  
  // reset
  set_output_multiple( 1 );
  
  // use internal state variable
  const char * map = d_bitmap.get();
  bool do_copy = false;
  
  int n_map = ninput_items[1];
  const int space_available = noutput_items;
  
  assert( noutput_items > 0 );
  
  const int vlen = d_vlen;
  const int arity = d_arity;
  
//  std::cout << "enter, vlen=" << vlen << " arity=" << arity << std::endl;
  

  int i;
  const int n_min = std::min( ninput_items[0], ninput_items[2] );
  
//  std::cout << "n_min=" << n_min << " noutput_items=" << noutput_items
//            << " n_map=" << n_map << std::endl;
  
  for( i = 0; i < n_min; ++i )
  {
//    std::cout << i << "." << std::endl;
    bool consume_map = false;
    
    if( trig[i] != 0 )
    {
      if( n_map == 0 )
      {
        d_need_bitmap = 1;
        break;
      }
      
      map = map_in;
      consume_map = true;
      
      // if we stop due to not enough output space, don't consume map
      // make sure we only consume the map if the correspondig trigger
      // is consumed 
      
    } // trig[i] != 0
    
    int nout = noutput_items;
    bool stop = false;
    for( int j = 0; j < vlen; ++j )
    {
      if( map[j] == arity )
      {
        if( nout == 0 )
        {
          stop = true;
          break;
        } // nout == 0
        
        *sym_out++ = sym_in[j];
        --nout;
        
      } // map[j] == arity
      
    } // for-loop over vector elements
    
    if( stop )
    {
//      std::cout << "stop" << std::endl;
      set_output_multiple( noutput_items + 1 );
      break;
    }
    
    if( consume_map )
    {
      // at this point, we produced all items corresponding to the current
      // trigger, hence we can consume the map.
//      std::cout << "consume map" << std::endl;
      do_copy = true;
      d_need_bitmap = 0;
      --n_map; map_in += vlen;
    }
    
//    std::cout << "nout=" << nout << std::endl;
    
    noutput_items = nout;
    sym_in += vlen;

  } // for-loop over items
  
  if( do_copy )
  {
    memcpy( d_bitmap.get(), map, sizeof(char) * vlen );
  }
  
  consume( 0, i );
  consume( 2, i );
  consume( 1, ninput_items[1] - n_map );
  
//  std::cout << "leave " << i << " " << (ninput_items[1] - n_map)
//            << " " << (space_available-noutput_items) << std::endl;

  return space_available - noutput_items;
}


ofdm_constellation_sample_filter_sptr
ofdm_make_constellation_sample_filter( int arity, int vlen )
{
  return ofdm_constellation_sample_filter::create( arity, vlen );
}


ofdm_constellation_sample_filter_sptr
ofdm_constellation_sample_filter::create( int arity, int vlen )
{
  try 
  {
    ofdm_constellation_sample_filter_sptr tmp( 
      new ofdm_constellation_sample_filter( arity, vlen ) );

    return tmp;
  } 
  catch ( ... ) 
  {
    std::cerr << "[ERROR] Caught exception at creation of"
              << "ofdm_constellation_sample_filter" << std::endl;
    throw;
  } // catch ( ... )
}



