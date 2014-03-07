/* -*- c++ -*- */
/* 
 * Copyright 2014 Institute for Theoretical Information Technology,
 *                RWTH Aachen University
 *                www.ti.rwth-aachen.de
 * 
 * This is free software; you can redistribute it and/or modify
 * it under the terms of the GNU General Public License as published by
 * the Free Software Foundation; either version 3, or (at your option)
 * any later version.
 * 
 * This software is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 * GNU General Public License for more details.
 * 
 * You should have received a copy of the GNU General Public License
 * along with this software; see the file COPYING.  If not, write to
 * the Free Software Foundation, Inc., 51 Franklin Street,
 * Boston, MA 02110-1301, USA.
 */

#ifdef HAVE_CONFIG_H
#include "config.h"
#endif

#include <gnuradio/io_signature.h>
#include "bit_position_dependent_ber_impl.h"

#include <iostream>
#include <fstream>
#include <sstream>
#include <iomanip>
#include <ios>

#define DEBUG 1

namespace gr {
  namespace ofdm {

    bit_position_dependent_ber::sptr
    bit_position_dependent_ber::make(std::string filename_prefix)
    {
      return gnuradio::get_initial_sptr
        (new bit_position_dependent_ber_impl(filename_prefix));
    }

    /*
     * The private constructor
     */
    bit_position_dependent_ber_impl::bit_position_dependent_ber_impl(std::string filename_prefix)
      : gr::block("bit_position_dependent_ber",
              gr::io_signature::make3(	3, 3,
            	        				sizeof( char ),
            	        				sizeof( char ),
            	        				sizeof( unsigned int )),
              gr::io_signature::make(0, 0, 0 ))
      , d_filename_prefix( filename_prefix )
      , d_index( 0 )
      , d_cntr_len( 0 )
      , d_cntr( )

      , d_file_idx( 0 )

      , d_min_reached( false )

    {}

    /*
     * Our virtual destructor.
     */
    bit_position_dependent_ber_impl::~bit_position_dependent_ber_impl()
    {
    	flush();
    }

    void
    bit_position_dependent_ber_impl::forecast (int noutput_items, gr_vector_int &ninput_items_required)
    {
    	ninput_items_required[0] = 1;
    	ninput_items_required[1] = 1;
    	ninput_items_required[2] = 1;
    }

    bool
    bit_position_dependent_ber_impl ::
    stop()
    {
      flush();
      return true;
    }

    int
    bit_position_dependent_ber_impl::general_work (int noutput_items,
                       gr_vector_int &ninput_items,
                       gr_vector_const_void_star &input_items,
                       gr_vector_void_star &output_items)
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
    }

    void
    bit_position_dependent_ber_impl :: flush()
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
    bit_position_dependent_ber_impl :: get_cntr_vec() const
    {
      std::vector< int > tmp( d_cntr_len );

      for( index_t i = 0; i < d_cntr_len; ++i )
      {
        tmp.at( i ) = d_cntr[i];
      }

      return tmp;

    }

  } /* namespace ofdm */
} /* namespace gr */

