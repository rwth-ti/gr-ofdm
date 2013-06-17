#ifdef HAVE_CONFIG_H
#include "config.h"
#endif

#include <gr_sync_interpolator.h>
#include <gr_io_signature.h>
#include "ofdm_corba_bitmap_src.h"

#include <iostream>
#include <algorithm>

#include <malloc16.h>
#include <cstring>

#include "corba_push_consumer.h"

#define DEBUG 0

ofdm_corba_bitmap_src_sptr
ofdm_make_corba_bitmap_src( int vlen, int station_id, std::string event_channel,
    std::string nameservice_ip, std::string nameservice_port )
{
  return ofdm_corba_bitmap_src_sptr( new ofdm_corba_bitmap_src( vlen,
      station_id, event_channel, nameservice_ip, nameservice_port ) );
}

ofdm_corba_bitmap_src::ofdm_corba_bitmap_src( int vlen, int station_id,
    std::string event_channel, std::string nameservice_ip,
    std::string nameservice_port )

  : gr_sync_interpolator( "corba_bitmap_src",
       gr_make_io_signature (1, 1, sizeof(short)),
       gr_make_io_signature (1, 1, sizeof(char)*vlen),
       2 ),

  d_vlen(vlen),
  d_station_id(station_id),
  d_event_channel(event_channel),
  d_nameservice_ip(nameservice_ip),
  d_nameservice_port(nameservice_port),
  d_last_id( -2 )

{

  d_push_consumer = get_corba_push_consumer_singleton(nameservice_ip,
        nameservice_port);

  d_push_consumer->set_owner("corba_bitmap_src");

  d_map =
    static_cast< achar * >( malloc16Align( sizeof( char ) * vlen ) );

}

ofdm_corba_bitmap_src ::
  ~ofdm_corba_bitmap_src()
{
  if( d_map )
    free16Align( static_cast< void * >( d_map ) );
}

void
ofdm_corba_bitmap_src ::
  set_map_for_idblock( char * const map )
{
  if( d_station_id == 0 ) // transmitter
    std::fill( map, map+d_vlen, 1 );
  else
    std::fill( map, map+d_vlen, 0 );
}

void
ofdm_corba_bitmap_src ::
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
ofdm_corba_bitmap_src::work(
    int noutput_items,
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
ofdm_corba_bitmap_src::start()
{
  d_push_consumer->subscribe_event_channel( d_event_channel );
  return true;
}

bool
ofdm_corba_bitmap_src::stop()
{
  std::cout << "[corbabitmapsrc] interrupt push consumer" << std::endl;
  d_push_consumer->interrupt();
  return true;
}

