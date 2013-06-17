#ifndef INCLUDED_OFDM_CORBA_ID_SRC_S_H_
#define INCLUDED_OFDM_CORBA_ID_SRC_S_H_

#include <ofdm_api.h>
#include <gr_block_fwd.h> // forward declarations
class corba_push_consumer;

class ofdm_corba_id_src_s;
typedef boost::shared_ptr<ofdm_corba_id_src_s> ofdm_corba_id_src_s_sptr;
OFDM_API ofdm_corba_id_src_s_sptr ofdm_make_corba_id_src_s(std::string sevent_channel, std::string snameservice_ip, std::string snameservice_port);

/*!

 */
class OFDM_API ofdm_corba_id_src_s : public gr_sync_block
{
  private:
    friend ofdm_corba_id_src_s_sptr ofdm_make_corba_id_src_s(std::string sevent_channel, std::string snameservice_ip, std::string snameservice_port);

    ofdm_corba_id_src_s(std::string sevent_channel, std::string snameservice_ip, std::string snameservice_port);

    std::string   d_sevent_channel;
    std::string   d_snameservice_ip;
    std::string   d_snameservice_port;
    boost::shared_ptr<corba_push_consumer> d_push_consumer;

//    int d_lastid;
//    long long d_cnt;

  public:
    virtual ~ofdm_corba_id_src_s();

    virtual bool start();
    virtual bool stop();

    // For tests. Blocks until ready or interrupted.
    // Return true if ready, else false
    bool ready();

    int work(
      int noutput_items,
      gr_vector_const_void_star &input_items,
      gr_vector_void_star &output_items);
};

#endif /* INCLUDED_OFDM_CORBA_ID_SRC_S_H_ */
