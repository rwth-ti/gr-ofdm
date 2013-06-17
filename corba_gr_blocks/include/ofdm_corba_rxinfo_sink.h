#ifndef INCLUDED_OFDM_CORBA_RXINFO_SINK_H_
#define INCLUDED_OFDM_CORBA_RXINFO_SINK_H_

#include <ofdm_api.h>
#include <gr_block_fwd.h> // forward declarations

#include <string>

class ofdm_corba_rxinfo_sink;
typedef boost::shared_ptr<ofdm_corba_rxinfo_sink> ofdm_corba_rxinfo_sink_sptr;
OFDM_API ofdm_corba_rxinfo_sink_sptr ofdm_make_corba_rxinfo_sink(std::string sevent_channel,
    std::string snameservice_ip, std::string snameservice_port, int vlen, int vlen_sc, int vlen_scatter,
    long station_id);

class corba_push_supplier_wrapper;

/*!
 * \brief Collect RX performance measure and push to event channel
 *
 * Inputs:
 * 1. ID
 * 2. CTF vector
 * 3. BER
 * 4. SNR
 */
class OFDM_API ofdm_corba_rxinfo_sink : public gr_sync_block
{
  private:
    friend ofdm_corba_rxinfo_sink_sptr ofdm_make_corba_rxinfo_sink(
        std::string sevent_channel, std::string snameservice_ip,
        std::string snameservice_port, int vlen, int vlen_sc, int vlen_scatter, long station_id);

    ofdm_corba_rxinfo_sink(std::string sevent_channel,
        std::string snameservice_ip, std::string snameservice_port, int vlen, int vlen_sc,
        int vlen_scatter, long station_id);

    std::string   d_sevent_channel;
    std::string   d_snameservice_ip;
    std::string   d_snameservice_port;
    int           d_vlen;
    int			  d_vlen_sc;
    int           d_vlen_scatter;
    long          d_station_id;

    boost::shared_ptr<corba_push_supplier_wrapper> d_supplier;

  public:
    virtual ~ofdm_corba_rxinfo_sink() {};

    virtual bool start();
    virtual bool stop();

    int work(
      int noutput_items,
      gr_vector_const_void_star &input_items,
      gr_vector_void_star &output_items);
};

#endif /* INCLUDED_OFDM_CORBA_RXINFO_SINK_H_ */
