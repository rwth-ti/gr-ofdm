/* -*- c++ -*- */
/* 
 * Copyright 2013 <+YOU OR YOUR COMPANY+>.
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
#include "corba_bitmap_src_impl.h"

#include <iostream>
#include <algorithm>
#include <gnuradio/malloc16.h>
#include <cstring>

#define DEBUG 0

namespace gr {
  namespace ofdm {

    corba_bitmap_src::sptr
    corba_bitmap_src::make(int vlen, int station_id, std::string event_channel, std::string nameservice_ip, std::string nameservice_port)
    {
      return gnuradio::get_initial_sptr
        (new corba_bitmap_src_impl(vlen, station_id, event_channel, nameservice_ip, nameservice_port));
    }

    /*
     * The private constructor
     */
    corba_bitmap_src_impl::corba_bitmap_src_impl(int vlen, int station_id, std::string event_channel, std::string nameservice_ip, std::string nameservice_port)
      : gr::sync_interpolator("corba_bitmap_src",
              gr::io_signature::make(1, 1, sizeof(short)),
              gr::io_signature::make(1, 1, sizeof(char)*vlen), 2)
    	, d_vlen(vlen)
    	, d_station_id(station_id)
    	, d_event_channel(event_channel)
    	, d_nameservice_ip(nameservice_ip)
    	, d_nameservice_port(nameservice_port)
    	, d_last_id( -2 )
    {
    	  d_push_consumer = get_corba_push_consumer_singleton(nameservice_ip,
    	        nameservice_port);

    	  d_push_consumer->set_owner("corba_bitmap_src");

    	  d_map =
    	    static_cast< achar * >( malloc16Align( sizeof( char ) * vlen ) );
    }

    /*
     * Our virtual destructor.
     */
    corba_bitmap_src_impl::~corba_bitmap_src_impl()
    {
    	  if( d_map )
    	    free16Align( static_cast< void * >( d_map ) );
    }

    void
    corba_bitmap_src_impl ::
      set_map_for_idblock( char * const map )
    {
      if( d_station_id == 0 ) // transmitter
        std::fill( map, map+d_vlen, 1 );
      else
        std::fill( map, map+d_vlen, 0 );
    }

    void
    corba_bitmap_src_impl ::
      store_map( void * cd )
    {
      ofdm_ti::tx_config_data * config_data =
        static_cast< ofdm_ti::tx_config_data * >( cd );

      if( d_station_id == 0 ) // transmitter
      {
        for( int k = 0; k < d_vlen; ++k )
          d_map[k] = config_data->mod_map[k];
      }
      else
      {
        // mask non-relevant subcarrier
        for( int k = 0; k < d_vlen; ++k )
        {
          if( config_data->assignment_map[k] == d_station_id )
            d_map[k] = config_data->mod_map[k];
          else
            d_map[k] = 0;
        } // for-loop
      } // if( d_station_id == 0 )
    }

    int
    corba_bitmap_src_impl::work(int noutput_items,
			  gr_vector_const_void_star &input_items,
			  gr_vector_void_star &output_items)
    {
    	const short *id = static_cast<const short*>(input_items[0]);
    	  char *map = static_cast<char*>(output_items[0]);

    	  int n_in = noutput_items/2;


    	  if(DEBUG)
    	    std::cout << "[corba bitmap src " << unique_id() << "] entered, state is "
    	              << "nout=" << noutput_items << " n_in=" << n_in << std::endl;

    	  int i;
    	  for( i = 0; i < n_in; ++i, map += 2*d_vlen )
    	  {
    	    if( d_last_id != id[i] )
    	    {
    	      corba_push_consumer::value_ptr config_data =
    	        d_push_consumer->get_tx_config( id[i],true ); // blocking

    	      if( ! config_data )
    	        break;

    	      store_map( static_cast< void * >( config_data.get() ) );
    	      d_last_id = id[i];
    	    }

    	//
    	//    ofdm_ti::tx_config_data* config_data =
    	//      d_push_consumer->get_tx_config( id[i], i==0 ); // blocking only on first

    	//    if( config_data == 0 ){
    	//
    	//      if(DEBUG)
    	//        std::cout << "No tx config for id " << id[i] << " available, break"
    	//                  << std::endl;
    	//
    	//      break;
    	//    }


    	    if(DEBUG)
    	      std::cout << "Output complete ID block bitmap" << std::endl;



    	    set_map_for_idblock( map );

    	    std::memcpy( map + d_vlen, d_map, sizeof( char ) * d_vlen );

    	//    // special case transmitter
    	//    if( d_station_id == 0 ){
    	////
    	////      // ID blocks' bitmap
    	////      for( int k = 0; k < d_vlen; ++k ){
    	////        map[k] = 1;
    	////      }
    	//
    	//      map += d_vlen;
    	//
    	//      if(DEBUG)
    	//        std::cout << "Output complete data block bitmap" << std::endl;
    	//
    	//
    	//      // data blocks' bitmap
    	//      for( int k = 0; k < d_vlen; ++k ){
    	//        map[k] = config_data->mod_map[k];
    	//      }
    	//
    	//    }else{
    	//
    	////      // ID blocks' bitmap
    	////      for( int k = 0; k < d_vlen; ++k ){
    	////        map[k] = 0;
    	////      }
    	//
    	//      map += d_vlen;
    	//
    	//      if(DEBUG)
    	//        std::cout << "Output masked data block bitmap" << std::endl;
    	//
    	//      // mask non-relevant subcarrier
    	//      for( int k = 0; k < d_vlen; ++k ){
    	//
    	//        if( config_data->assignment_map[k] == d_station_id ){
    	//          map[k] = config_data->mod_map[k];
    	//        }else{
    	//          map[k] = 0;
    	//        }
    	//
    	//      } // for-loop
    	//
    	//    } // d_station_id == 0
    	//
    	//    map += d_vlen;


    	  } // for-loop

    	  if(DEBUG)
    	    std::cout << "[corba bitmap src] leave process, produce " << 2*i
    	              << " items" << std::endl;

    	  return 2*i;
    }

    bool
    corba_bitmap_src_impl::start()
    {
      d_push_consumer->subscribe_event_channel( d_event_channel );
      return true;
    }

    bool
    corba_bitmap_src_impl::stop()
    {
      std::cout << "[corbabitmapsrc] interrupt push consumer" << std::endl;
      d_push_consumer->interrupt();
      return true;
    }

  } /* namespace ofdm */
} /* namespace gr */

