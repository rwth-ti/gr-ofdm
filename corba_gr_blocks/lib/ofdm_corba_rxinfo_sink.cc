#ifdef HAVE_CONFIG_H
#include "config.h"
#endif

#include <gr_sync_block.h>
#include <gr_io_signature.h>
#include "ofdm_corba_rxinfo_sink.h"

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
//class ofdm_corba_rxinfo_sink::push_pipe : public omni_thread {
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
//    fputs( "START: Threaded CORBA RxInfo sink started\n", stdout );
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
//    fputs( "STOP: Threaded CORBA RxInfo sink stopped\n", stdout );
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



    ofdm_corba_rxinfo_sink_sptr
ofdm_make_corba_rxinfo_sink(std::string sevent_channel,
        std::string snameservice_ip, std::string snameservice_port, int vlen,int vlen_sc,
        int vlen_scatter, long station_id)
{
    return ofdm_corba_rxinfo_sink_sptr(new ofdm_corba_rxinfo_sink(sevent_channel,
                snameservice_ip, snameservice_port, vlen, vlen_sc, vlen_scatter, station_id));
}

ofdm_corba_rxinfo_sink::ofdm_corba_rxinfo_sink(std::string sevent_channel,
        std::string snameservice_ip, std::string snameservice_port, int vlen, int vlen_sc,
        int vlen_scatter, long station_id)

: gr_sync_block("corba_rxinfo_sink",
        gr_make_io_signature7(7, 7, sizeof(short),
            sizeof(float)*vlen,
            sizeof(float)*vlen_sc,
            sizeof(float),
            sizeof(float),
            sizeof(float),
            sizeof(gr_complex)*vlen_scatter ),
        gr_make_io_signature (0, 0, 0) ),

    d_sevent_channel(sevent_channel),
    d_snameservice_ip(snameservice_ip),
    d_snameservice_port(snameservice_port),
    d_vlen(vlen),
    d_vlen_sc(vlen_sc),
    d_vlen_scatter(vlen_scatter),
    d_station_id(station_id)
{
    cps_wrap_t t(new corba_push_supplier_wrapper(snameservice_ip,
                snameservice_port));
    d_supplier = t;
}

int
ofdm_corba_rxinfo_sink::work(
        int noutput_items,
        gr_vector_const_void_star &input_items,
        gr_vector_void_star &output_items)
{
    const short *id = static_cast<const short*>(input_items[0]);
    const float *ctf = static_cast<const float*>(input_items[1]);
    const float *sinr_sc = static_cast<const float*>(input_items[2]);
    const float *ber = static_cast<const float*>(input_items[3]);
    const float *snr = static_cast<const float*>(input_items[4]);
    const float *freqoff = static_cast<const float*>(input_items[5]);
    const gr_complex *scatter = static_cast<const gr_complex*>(input_items[6]);

    ofdm_ti::rx_performance_measure rxinfo;
    ofdm_ti::float_sequence corba_ctf(d_vlen);
    corba_ctf.length(d_vlen);
    ofdm_ti::float_sequence corba_est_sinr_sc(d_vlen_sc);
    corba_est_sinr_sc.length(d_vlen_sc);
    ofdm_ti::scatter_sequence scatter_samples(d_vlen_scatter);
    scatter_samples.length(d_vlen_scatter);

    //#ifdef KEEPLAST

    ctf += (noutput_items-1)*d_vlen;
    id += (noutput_items-1);
    ber += (noutput_items-1);
    snr += (noutput_items-1);
    sinr_sc += (noutput_items-1)*d_vlen_sc;
    freqoff += (noutput_items-1);
    scatter += (noutput_items-1)*d_vlen_scatter;

    //#else

    //for(int j = 0; j < noutput_items; ++j, ++id, ++ber, ++snr, ctf+=d_vlen)

    //#endif

    {

        for(int i = 0; i < d_vlen; ++i){
            corba_ctf[i] = static_cast<CORBA::Float>(ctf[i]);
        }
        for(int i = 0; i < d_vlen_sc; ++i){
            corba_est_sinr_sc[i] = static_cast<CORBA::Float>(sinr_sc[i]);
        }
        for(int i = 0; i < d_vlen_scatter; ++i){
            scatter_samples[i].i = static_cast<CORBA::Float>(scatter[i].real());
            scatter_samples[i].q = static_cast<CORBA::Float>(scatter[i].imag());
        }
        rxinfo.rx_id = static_cast<CORBA::ULong>(*id);
        rxinfo.ctf = corba_ctf;
        rxinfo.est_sinr_sc = corba_est_sinr_sc;
        rxinfo.ber = static_cast<CORBA::Float>(*ber);
        rxinfo.snr = static_cast<CORBA::Float>(*snr);
        rxinfo.freqoff = static_cast<CORBA::Float>(*freqoff);
        rxinfo.scatter = scatter_samples;
        rxinfo.rx_station = static_cast<CORBA::Long>(d_station_id);

        //    std::cout << "BER " << *ber << std::endl;

        try {
            d_supplier->push( rxinfo );
        }
        catch( ... )
        {
            std::cerr << "Too much radiation. Push failed" << std::endl;
        }

    }

    return noutput_items;
}

bool ofdm_corba_rxinfo_sink::start()
{
    d_supplier->set_event_channel(d_sevent_channel);
    return true;
}

bool ofdm_corba_rxinfo_sink::stop()
{
    std::cout << "[corbarxinfosink] supplier shutdown" << std::endl;
    d_supplier->shutdown();

    return true;
}
