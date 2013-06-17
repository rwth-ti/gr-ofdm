#ifdef HAVE_CONFIG_H
#include "config.h"
#endif

#include <gr_low_latency_policy.h>
#include <gr_sync_block.h>
#include <gr_io_signature.h>
#include "ofdm_corba_id_src_s.h"
#include "corba_push_consumer.h"

#include <iostream>


#define DEBUG_OUT 1



ofdm_corba_id_src_s_sptr ofdm_make_corba_id_src_s(std::string sevent_channel, std::string snameservice_ip, std::string snameservice_port)
{
  return ofdm_corba_id_src_s_sptr(new ofdm_corba_id_src_s(sevent_channel, snameservice_ip, snameservice_port));
}

ofdm_corba_id_src_s::ofdm_corba_id_src_s(std::string sevent_channel, std::string snameservice_ip, std::string snameservice_port)
  : gr_sync_block("corba_id_src",
           gr_make_io_signature (0, 0, 0),
           gr_make_io_signature (1, 1, sizeof(short))),
  d_sevent_channel(sevent_channel),
  d_snameservice_ip(snameservice_ip),
  d_snameservice_port(snameservice_port)

//  d_lastid( -1 ),
//  d_cnt( 0 )

{
  d_push_consumer = get_corba_push_consumer_singleton(d_snameservice_ip, d_snameservice_port);
  set_latency_policy( gr_make_low_latency_policy( 40, 200 ) );
  set_output_multiple( 20 );
}


int
ofdm_corba_id_src_s::work(
    int noutput_items,
    gr_vector_const_void_star &input_items,
    gr_vector_void_star &output_items)
{
  short *out = static_cast<short*>(output_items[0]);
  short ret = d_push_consumer->get_latest_id();

  if( ret != -1 )
  {
//    if( ret != d_lastid )
//    {
//      std::cout << "ID src, new ID: " << ret << " cnt = " << d_cnt << std::endl;
//      d_lastid = ret;
//      d_cnt = 0;
//    }

    for( int i = 0; i < output_multiple(); ++i ){
      out[i] = ret;
    }

//    d_cnt += output_multiple();

    return output_multiple();
  }
  else // interrupt requested, we're done
  {
    return -1;
  }
}

ofdm_corba_id_src_s::~ofdm_corba_id_src_s()
{
}

bool ofdm_corba_id_src_s::start()
{
  d_push_consumer->clear();
  d_push_consumer->subscribe_event_channel(d_sevent_channel);
  return true;
}

bool ofdm_corba_id_src_s::stop()
{
  if( DEBUG_OUT )
    std::cout << "[corbaidsrc] shutdown push consumer" << std::endl;

  d_push_consumer->shutdown();
  return true;
}


bool
ofdm_corba_id_src_s::ready()
{
  return d_push_consumer->ready();
}
