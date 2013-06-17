#ifdef HAVE_CONFIG_H
#include "config.h"
#endif

#include <gr_block.h>
#include <gr_io_signature.h>
#include "ofdm_corba_multiplex_src_ss.h"

#include "corba_push_consumer.h"


#include <algorithm>
#include <iostream>
#include <cstring>
#include <vector>

ofdm_corba_multiplex_src_ss_sptr ofdm_make_corba_multiplex_src_ss(std::string sevent_channel, std::string snameservice_ip, std::string snameservice_port)
{
  return ofdm_corba_multiplex_src_ss_sptr(new ofdm_corba_multiplex_src_ss(sevent_channel, snameservice_ip, snameservice_port));
}


void ofdm_corba_multiplex_src_ss::forecast(int noutput_items, gr_vector_int &ninput_items_required)
{
  if(d_qdata.empty())
    ninput_items_required[0] = 1;
  else
    ninput_items_required[0] = 0;
}


ofdm_corba_multiplex_src_ss::ofdm_corba_multiplex_src_ss(std::string sevent_channel, std::string snameservice_ip, std::string snameservice_port)
  : gr_block(
      "corba_multiplex_src_ss",
      gr_make_io_signature(
        1, 1,
         sizeof(short) ),
      gr_make_io_signature(
        1, 1,
        sizeof(short) ) )

  , d_sevent_channel(sevent_channel)
  , d_snameservice_ip(snameservice_ip)
  , d_snameservice_port(snameservice_port)
  , d_pos( 0 )
{
  d_push_consumer =
    get_corba_push_consumer_singleton(d_snameservice_ip, d_snameservice_port);
}

int ofdm_corba_multiplex_src_ss::general_work(
    int noutput_items,
    gr_vector_int &ninput_items,
    gr_vector_const_void_star &input_items,
    gr_vector_void_star &output_items)
{
  const short * __restrict in = static_cast< const short* >( input_items[0] );
  short * __restrict out = static_cast< short* >( output_items[0] );

  bool stop = false;
  int o = 0;
  int consumed = 0;

  short last_id = -1;

  corba_push_consumer::value_ptr config_data;
  int vlen = 0;
  int nzeros = 0;
  int pos_max = 0;

  int bits_per_block = 0;
  std::vector<int> unrolled_assignment_map;

  for( int i = 0; i < ninput_items[0] && !stop && o < noutput_items; ++i )
  {
    if( in[i] != last_id )
    {
      config_data = d_push_consumer->get_tx_config( in[i], i == 0 );

      if( ! config_data )
        break;

      vlen = config_data->mod_map.length();
      nzeros = config_data->id_blocks * vlen;
      pos_max = config_data->data_blocks * vlen + nzeros;

      bits_per_block = 0;
      for( int subc = 0; subc < vlen; ++subc )
      {
        bits_per_block += config_data->mod_map[subc];
      }
      unrolled_assignment_map.resize( bits_per_block );

      for( int subc = 0, k = 0; subc < vlen; ++subc )
      {
        int const rep = config_data->mod_map[subc];
        short const id = config_data->assignment_map[subc];
        for( int x = 0; x < rep; ++x, ++k )
        {
          unrolled_assignment_map[ k ] = id;
        }
      }
      set_output_multiple( bits_per_block );
    } // if( in[i] != last_id )

    const int n = std::min( noutput_items - o, std::max( 0, nzeros-d_pos ) );

    if( n > 0 )
    {
      for( int j = 0; j < n; ++j, ++o )
      {
	out[o] = 0;
      }
      d_pos += n;
    } // n > 0

    if( noutput_items == o )
      break;


    int pos = d_pos;

    for(; pos < pos_max; pos += vlen )
    {
      if( ( o + bits_per_block ) > noutput_items )
      {
        stop = true;
        break;
      }

      for( int x = 0; x < bits_per_block; ++x )
      {
        out[o++] = unrolled_assignment_map[x];
      }
    } // for(; pos < pos_max; pos += vlen )

/*
    int subc = pos % vlen;

    for( ; pos < pos_max; ++pos )
    {
      const short id = config_data->assignment_map[subc];

      if( id != 0 )
      {
        const int rep = config_data->mod_map[subc];
        const int next_o = o + rep;

        if( next_o <= noutput_items )
        {
          for( int j = 0; j < rep; ++j, ++o )
          {
            out[o] = id;
          }
        }
        else
        {
          stop = true;
          break;

        } // ( o + rep ) <= noutput_items
      } // id != 0

      ++subc;
      if( subc == vlen ) subc = 0;
      //subc %= vlen;

    } // for-loop
*/

    d_pos = pos;
    if( pos == pos_max )
    {
      d_pos = 0;
      ++consumed;
    }

  } // for-loop

  consume( 0, consumed );

  return o;
}


ofdm_corba_multiplex_src_ss::~ofdm_corba_multiplex_src_ss()
{
}

bool ofdm_corba_multiplex_src_ss::start()
{
  d_push_consumer->subscribe_event_channel(d_sevent_channel);
  return true;
}

bool ofdm_corba_multiplex_src_ss::stop()
{
  std::cout << "[corbamuxsrc] shutdown consumer" << std::endl;
  d_push_consumer->shutdown();
  return true;
}

int
ofdm_corba_multiplex_src_ss::noutput_forecast( gr_vector_int &ninput_items,
    int available_space, int max_items_avail, std::vector<bool> &input_done )
{

  // if our queue is empty, check if we are done because our upstream block
  // is done. if the queue is empty and we have no input items available,
  // signal that we can't produce anything.

  if( d_qdata.empty() ){

    if( input_done[0] ){
      return -1;
    }

    if( ninput_items[0] == 0 ){
      return 0;
    }
  }

  return available_space;
}

