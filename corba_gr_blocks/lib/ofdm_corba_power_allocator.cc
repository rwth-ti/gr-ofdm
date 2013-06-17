#ifdef HAVE_CONFIG_H
#include "config.h"
#endif

#include <gr_block.h>
#include <gr_io_signature.h>
#include "ofdm_corba_power_allocator.h"
#include <malloc16.h>

#include <algorithm>
#include <cmath>
#include <stdexcept>
#include <iostream>




#include "corba_push_consumer.h"

#define DEBUG 0

ofdm_corba_power_allocator_sptr
ofdm_make_corba_power_allocator( int vlen, std::string event_channel,
    std::string nameservice_ip, std::string nameservice_port, bool allocate )
{
  return ofdm_corba_power_allocator_sptr( new ofdm_corba_power_allocator(
      vlen, event_channel, nameservice_ip, nameservice_port, allocate ) );
}


void
ofdm_corba_power_allocator::forecast(int noutput_items,
    gr_vector_int &ninput_items_required)
{

  ninput_items_required[0] = noutput_items; // blocks
  ninput_items_required[2] = noutput_items; // trigger
  ninput_items_required[1] = d_need_id;

}


ofdm_corba_power_allocator::ofdm_corba_power_allocator( int vlen,
    std::string event_channel, std::string nameservice_ip,
    std::string nameservice_port, bool allocate )

  : gr_block("corba_power_allocator",
           gr_make_io_signature3(3, 3, sizeof(gr_complex)*vlen,   // blocks
                                       sizeof(short),             // IDs
                                       sizeof(char) ),            // trig
           gr_make_io_signature (1, 1, sizeof(gr_complex)*vlen)), // blocks

  d_vlen( vlen ),
  d_event_channel( event_channel ),
  d_nameservice_ip( nameservice_ip ),
  d_nameservice_port( nameservice_port ),
  d_allocate( allocate ),
  d_need_id( 1 ),
  d_last_id( -1 )

{
  d_last_powermap =
    static_cast< afloat * >( malloc16Align( sizeof( float ) * vlen ) );

  d_push_consumer = get_corba_push_consumer_singleton(nameservice_ip,
        nameservice_port);

  d_push_consumer->set_owner("corba_power_allocator");

}

ofdm_corba_power_allocator::~ofdm_corba_power_allocator()
{
  if( d_last_powermap )
    free16Align( static_cast< void * >( d_last_powermap ) );
}

void
ofdm_corba_power_allocator::get_power_map( short id )
{
  corba_push_consumer::value_ptr config_data =
    d_push_consumer->get_tx_config( id, true );

//  ofdm_ti::tx_config_data* config_data =
//      d_push_consumer->get_tx_config( id, true ); // blocking


  if( config_data->power_map.length() != (unsigned)d_vlen )
  {
    throw std::runtime_error("[PowerAlloc] Error: received power map"\
                             " vector has different length than expected");
  }


  for( int i = 0; i < d_vlen; ++i )
  {
    float tmp = std::sqrt( config_data->power_map[i] );
    if( tmp < 10e-6 )
      tmp = 1.0; // for deallocate, limit

    if( d_allocate )
    {
      d_last_powermap[i] = tmp;
      //d_last_powermap[2*i+1] = tmp;
    }
    else
    {
      d_last_powermap[i] = 1.0/tmp;
      //d_last_powermap[2*i+1] = 1.0/tmp;
    }
  } // for( int i = 0; i < d_vlen; ++i )

}

int
ofdm_corba_power_allocator::general_work(
    int noutput_items,
    gr_vector_int &ninput_items,
    gr_vector_const_void_star &input_items,
    gr_vector_void_star &output_items )
{

  const gr_complex *blk = static_cast<const gr_complex*>(input_items[0]);
  const short *id = static_cast<const short*>(input_items[1]);
  const char *trig = static_cast<const char*>(input_items[2]);

  gr_complex *out = static_cast<gr_complex*>(output_items[0]);


  int n_blk = ninput_items[0];
  int n_id = ninput_items[1];
  int n_trig = ninput_items[2];
  int nout = noutput_items;

  int n_min = std::min( nout, std::min( n_blk, n_trig ) );

  memcpy( out, blk, n_min * sizeof(gr_complex) * d_vlen );

  for( int n = 0; n < n_min; ++n, out += d_vlen, --nout )
  {
    if( trig[n] == 1 )
    {
      if( n_id > 0 )
      {
        if( *id != d_last_id )
          get_power_map( *id );
        d_last_id = *id;
        ++id;
        --n_id;
      }
      else
      {
        d_need_id = 1;
        break;
      } // n_id > 0

      // handle ID block here, power map = [1]*vlen
      // TODO: more than one ID block?
      continue;

    } // trig[n] == 1

    // data block

    int const i_max = d_vlen;
    for( int i = 0; i < i_max; ++i ) // AUTO VECTORIZED!!
    {
      out[i] *= d_last_powermap[i];
    }

  } // for-loop

  consume( 1, ninput_items[1] - n_id );

  int p = noutput_items - nout;
  consume( 0, p );
  consume( 2, p );

  return p;
}



bool
ofdm_corba_power_allocator::start()
{
  d_push_consumer->subscribe_event_channel(d_event_channel);
  return true;
}

bool
ofdm_corba_power_allocator::stop()
{
  std::cout << "[corbapowerallocator] shutdown consumer" << std::endl;
  d_push_consumer->shutdown();
  return true;
}


int
ofdm_corba_power_allocator::noutput_forecast( gr_vector_int &ninput_items,
    int available_space, int max_items_avail, std::vector<bool> &input_done )
{

  if( ninput_items[1] < d_need_id ){
    if( input_done[1] )
      return -1;

    return 0;
  }

  int nout = std::min( available_space,
             std::min( ninput_items[0], ninput_items[2] ) );

  if( nout == 0 && ( input_done[0] || input_done[2] ) )
    return -1;

  return nout;

}
