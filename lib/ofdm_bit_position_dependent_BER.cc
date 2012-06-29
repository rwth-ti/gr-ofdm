
/* $Id: ofdm_bit_position_dependent_BER.cc 1106 2009-08-15 15:07:55Z auras $ */

#ifdef HAVE_CONFIG_H
#include "config.h"
#endif

#include <gr_block.h>
#include <gr_io_signature.h>
#include <ofdm_bit_position_dependent_BER.h>

#include <iostream>
#include <fstream>
#include <sstream>
#include <iomanip>
#include <ios>

#define DEBUG 1


ofdm_bit_position_dependent_BER ::
ofdm_bit_position_dependent_BER( std::string filename_prefix )
  : gr_block(
      "bit_position_dependent_BER",
      gr_make_io_signature3(
        3, 3,
        sizeof( char ),
        sizeof( char ),
        sizeof( unsigned int ) ),
      gr_make_io_signature( 0, 0, 0 ) )

  , d_filename_prefix( filename_prefix )

  , d_index( 0 )
  , d_cntr_len( 0 )
  , d_cntr( )

  , d_file_idx( 0 )

  , d_min_reached( false )

{
}


void
ofdm_bit_position_dependent_BER ::
forecast(
  int             noutput_items,
  gr_vector_int & ninput_items_required )
{
  ninput_items_required[0] = 1;
  ninput_items_required[1] = 1;
  ninput_items_required[2] = 1;
}

bool
ofdm_bit_position_dependent_BER ::
stop()
{
  flush();
  return true;
}


int
ofdm_bit_position_dependent_BER ::
general_work(
  int                         noutput_items,
  gr_vector_int             & ninput_items,
  gr_vector_const_void_star & input_items,
  gr_vector_void_star       & output_items )
{
  char const * data = static_cast< char const * >( input_items[0] );
  char const * ref  = static_cast< char const * >( input_items[1] );
  unsigned int const * bitcount =
    static_cast< unsigned int const * >( input_items[2] );

  unsigned int nin = std::min( ninput_items[0], ninput_items[1] );
  int n_bc = ninput_items[2];
  int consumed = 0;

  while( n_bc > 0 )
  {
    if( *bitcount != d_cntr_len )
    {
      flush();

//      std::cout << "new snr vec" << std::endl;
      //std::cout << std::endl << "###### BER ###### flush, file index = " << d_file_idx << std::endl;
      cntr_vec_t tmp( new cntr_t[*bitcount] );
      std::fill( tmp.get(), tmp.get() + *bitcount, (cntr_t)0 );
      d_cntr_len = *bitcount;
      d_index = 0;
      d_cntr = tmp;
    }

    int const N = std::min( *bitcount - d_index,  nin );
    for( int i = 0; i < N; ++i )
    {
      d_cntr[ d_index + i ] += ( data[i] != ref[i] ) ? 1 : 0;
    }
    d_index += N;

    consumed += N; data += N; ref += N;
    nin -= N;
    if( nin == 0 )
      break;

    if( d_index == *bitcount )
    {
      if( ! d_min_reached && * std::min_element( d_cntr.get(), d_cntr.get()+*bitcount ) >= 100 )
      {
        std::cout << "##### MIN 100 reached ####" << std::endl;
        d_min_reached = true;
      }
      ++bitcount; --n_bc;
      d_index = 0;

//      std::cout << "wrap around" << std::endl;
    }

  } // while( n_bc > 0 )

  consume( 0, consumed );
  consume( 1, consumed );
  consume( 2, ninput_items[2] - n_bc );

  return 0;

} // general_work

void
ofdm_bit_position_dependent_BER ::
flush()
{
  if( d_cntr_len >  0 )
  {
    std::stringstream filename;
    filename << d_filename_prefix << "_" << std::setw(3) << std::setfill('0')
             << d_file_idx << ".uint";

    std::ofstream file;
    file.open( filename.str().c_str(),
      std::ios_base::out | std::ios_base::binary );

    file.write( reinterpret_cast< char* >( d_cntr.get() ),
      sizeof( cntr_t ) * d_cntr_len );

    ++d_file_idx;
    d_min_reached = false;

    std::cout << std::endl << "###### BER ###### flush filename was " << filename.str() << std::endl;
  }
} // flush


std::vector< int >
ofdm_bit_position_dependent_BER ::
get_cntr_vec() const
{
  std::vector< int > tmp( d_cntr_len );

  for( index_t i = 0; i < d_cntr_len; ++i )
  {
    tmp.at( i ) = d_cntr[i];
  }

  return tmp;

} // get_cntr_vec


ofdm_bit_position_dependent_BER_sptr
ofdm_make_bit_position_dependent_BER( std::string filename_prefix )
{
  return ofdm_bit_position_dependent_BER::create( filename_prefix );
}


ofdm_bit_position_dependent_BER_sptr
ofdm_bit_position_dependent_BER ::
create( std::string filename_prefix )
{
  try
  {
    ofdm_bit_position_dependent_BER_sptr tmp(
      new ofdm_bit_position_dependent_BER( filename_prefix ) );

    return tmp;
  }
  catch ( ... )
  {
    std::cerr << "[ERROR] Caught exception at creation of "
              << "ofdm_bit_position_dependent_BER" << std::endl;
    throw;
  } // catch ( ... )
}



