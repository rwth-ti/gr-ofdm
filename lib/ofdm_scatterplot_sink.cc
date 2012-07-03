/* $Id$ */

#ifdef HAVE_CONFIG_H
#include "config.h"
#endif

#include <gr_block.h>
#include <gr_io_signature.h>
#include <ofdm_scatterplot_sink.h>

#include <iostream>

#define DEBUG 0

ofdm_scatterplot_sink::ofdm_scatterplot_sink( int vlen, std::string shm_id ) :
  gr_block( "scatterplot_sink",
    gr_make_io_signature3( 3, 3, sizeof(gr_complex)
      * vlen, sizeof(char) * vlen, sizeof(char) ),
      gr_make_io_signature( 0, 0, 0 ) )
  , d_vlen( vlen )
{
  if( DEBUG > 0 )
    std::cout << "SCATTERPLOT_SINK initializes IPC\n";
  d_shm = c_interprocess::create( d_vlen, 64, shm_id ); //64 Buffers of length d_vlen
  temp_buffer = new c_point[d_vlen];
  std::cout << "finished init\n";
}

void ofdm_scatterplot_sink::forecast( int noutput_items,
  gr_vector_int & ninput_items_required )
{
  ninput_items_required[0] = 1;
  ninput_items_required[1] = 1;
  ninput_items_required[2] = 1;
}

int ofdm_scatterplot_sink::general_work( int noutput_items,
  gr_vector_int & ninput_items, gr_vector_const_void_star & input_items,
  gr_vector_void_star & output_items )
{
  const gr_complex * sym_in =
      static_cast< const gr_complex* > ( input_items[0] );
  const char * cv_in = static_cast< const char* > ( input_items[1] );
  const char * trig = static_cast< const char* > ( input_items[2] );

  int n_min = std::min( ninput_items[0], ninput_items[2] );
  int n_cv = ninput_items[1];

  int cv_counter = 0;

  if( DEBUG > 0 )
    std::cout << "SCATTERPLOT_SINK works... n_min=" << n_min << "\n";

  int k;
  for( k = 0; k < n_min; ++k )
  {
    if( trig[k] == 0 ) //use old cv
    {
      for( int i = 0; i < d_vlen; ++i )
      {
        temp_buffer[i].x = sym_in->real();
        temp_buffer[i].y = sym_in->imag();
        if( DEBUG > 0 )
          std::cout << "(" << temp_buffer[i].x << "," << temp_buffer[i].y
              << ")";
        sym_in++ ;
      }
      d_shm->add_points( temp_buffer, NULL );
    }
    else //use new cv
    {
      if( n_cv > 0 ) // there is a cv vector left
      {
        for( int i = 0; i < d_vlen; ++i )
        {
          temp_buffer[i].x = sym_in->real();
          temp_buffer[i].y = sym_in->imag();
          if( DEBUG > 0 )
            std::cout << "(" << temp_buffer[i].x << "," << temp_buffer[i].y
                << ")";
          sym_in++ ;
        }
        d_shm->add_points( temp_buffer, &cv_in[cv_counter * d_vlen] );
        ++cv_counter;
        --n_cv;
      }
      else // there is no cv_vector left
      {
        break;
      }
    }
  }

  if( DEBUG > 0 )
    std::cout << "\n";

  consume( 0, k );
  consume( 1, cv_counter );
  consume( 2, k );

  return 0;
}

ofdm_scatterplot_sink_sptr ofdm_make_scatterplot_sink( int vlen,
  std::string shm_id )
{
  return ofdm_scatterplot_sink::create( vlen, shm_id );
}

ofdm_scatterplot_sink_sptr ofdm_scatterplot_sink::create( int vlen,
  std::string shm_id )
{
  try
  {
    ofdm_scatterplot_sink_sptr tmp( new ofdm_scatterplot_sink( vlen, shm_id ) );

    return tmp;
  }
  catch( ... )
  {
    std::cerr << "[ERROR] Caught exception at creation of "
        << "ofdm_scatterplot_sink" << std::endl;
    throw ;
  } // catch ( ... )
}

