#ifdef HAVE_CONFIG_H
#include "config.h"
#endif

#include <gr_sync_block.h>
#include <gr_io_signature.h>
#include "ofdm_corba_rxbaseband_sink.h"

#include "corba_push_supplier_wrapper.h"
#include "tao_skeleton/ofdm_tiC.h"

#include <iostream>

#define KEEPLAST

typedef boost::shared_ptr<corba_push_supplier_wrapper> cps_wrap_t;


///*! \brief Decoupled event channel access
// *
// * Push events to CORBA event channel. Events are enqueued by main
// * GNU Radio C++ block. Thread returns upon special message (type=1).
// *
// */
//class ofdm_corba_rxbaseband_sink::push_pipe : public omni_thread {
//
//private:
//
//  gr_msg_queue_sptr  d_msgq;
//  cps_wrap_t d_supplier;
//  bool d_enabled;
//
//  virtual void*
//  run_undetached( void* )
//  {
//    main_loop();
//    return 0;
//  }
//
//  void
//  main_loop()
//  {
//    gr_message_sptr msg;
//
//    fputs( "START: Threaded CORBA rxbaseband sink started\n", stdout );
//    d_enabled = true;
//
//    while(true){
//
//      msg = d_msgq->delete_head_nowait();
//
//      if(!msg){
//        yield();
//        continue;
//      }
//
//      if( msg->type() == 1 ){
//        break;
//      }
//
//
//      ofdm_ti::rx_performance_measure *r =
//        static_cast<ofdm_ti::rx_performance_measure*>(
//            static_cast<void*>( msg->msg() ) );
//
//      d_supplier->push( *r );
//
//
//    } // while true
//
//    fputs( "STOP: Threaded CORBA rxbaseband sink stopped\n", stdout );
//  }
//
//  void
//  stop()
//  {
//    if( d_enabled ){
//
//      d_enabled = false;
//
//      gr_message_sptr msg = gr_make_message( 1 , 0 , 0 , 0 );
//      d_msgq->flush();
//      d_msgq->handle( msg ); // blocking
//
//      join(0);
//
//    }
//
//  }
//
//
//public:
//
//  push_pipe( int size, cps_wrap_t sup )
//    : d_msgq( gr_make_msg_queue( size ) ),
//      d_supplier( sup ),
//      d_enabled ( false )
//    {};
//
//  /*! \brief Non-blocking enqueueing of messages */
//  void
//  enqueue( gr_message_sptr msg )
//  {
//    if( ! d_msgq->full_p() ){
//      d_msgq->handle(msg);
//    }
//  }
//
//
//
//  virtual void
//  start()
//  {
//    start_undetached();
//  }
//
//
//  class deleter;
//  friend class deleter;
//
//  class deleter {
//  public:
//    void operator()( push_pipe* p )
//    {
//      if(p)
//        p->stop();
//      // storage reclaimed automatically on join()
//    }
//  };
//
//};



ofdm_corba_rxbaseband_sink_sptr
ofdm_make_corba_rxbaseband_sink(std::string sevent_channel,
    std::string snameservice_ip, std::string snameservice_port, int vlen,
    long station_id)
{
  return ofdm_corba_rxbaseband_sink_sptr(new ofdm_corba_rxbaseband_sink(sevent_channel,
      snameservice_ip, snameservice_port, vlen, station_id));
}

ofdm_corba_rxbaseband_sink::ofdm_corba_rxbaseband_sink(std::string sevent_channel,
    std::string snameservice_ip, std::string snameservice_port, int vlen,
    long station_id)

  : gr_sync_block("corba_rxbaseband_sink",
      gr_make_io_signature(1, 1,sizeof(float)*vlen),
      gr_make_io_signature (0, 0, 0) ),

    d_sevent_channel(sevent_channel),
    d_snameservice_ip(snameservice_ip),
    d_snameservice_port(snameservice_port),
    d_vlen(vlen),
    d_station_id(station_id)

{

  cps_wrap_t t(new corba_push_supplier_wrapper(snameservice_ip,
      snameservice_port));
  d_supplier = t;


}

int
ofdm_corba_rxbaseband_sink::work(
    int noutput_items,
    gr_vector_const_void_star &input_items,
    gr_vector_void_star &output_items)
{
  //const short *id = static_cast<const short*>(input_items[0]);
  const float *bband = static_cast<const float*>(input_items[0]);
  //const float *frlos = static_cast<const float*>(input_items[2]);

  ofdm_ti::baseband_rx rxbaseband;
  ofdm_ti::float_sequence corba_bband(d_vlen);
  corba_bband.length(d_vlen);

#ifdef KEEPLAST

  bband += (noutput_items-1)*d_vlen;
  //id += (noutput_items-1);
  //frlos += (noutput_items-1);

#else

  for(int j = 0; j < noutput_items; ++j, /*++id,*/ bband+=d_vlen)
  //for(int j = 0; j < noutput_items; ++j, ++id, ++frlos, bband+=d_vlen)

#endif

  {

    for(int i = 0; i < d_vlen; ++i){
      corba_bband[i] = static_cast<CORBA::Float>(bband[i]);
    }
    //rxbaseband.rx_id = static_cast<CORBA::ULong>(*id);
    rxbaseband.bband = corba_bband;
    //rxbaseband.frlos = static_cast<CORBA::Float>(*frlos);
    rxbaseband.rx_station = static_cast<CORBA::Long>(d_station_id);

    try {
      d_supplier->push( rxbaseband );
    }
    catch( ... )
    {
      std::cerr << "Too much radiation.  failed" << std::endl;
    }

  }

  return noutput_items;
}

bool ofdm_corba_rxbaseband_sink::start()
{
  d_supplier->set_event_channel(d_sevent_channel);
  return true;
}

bool ofdm_corba_rxbaseband_sink::stop()
{
  std::cout << "[corbarxbasebandsink] supplier shutdown" << std::endl;
  d_supplier->shutdown();

  return true;
}
