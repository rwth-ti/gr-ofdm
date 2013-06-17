#ifndef INCLUDED_OFDM_CORBA_MAP_SRC_SV_H_
#define INCLUDED_OFDM_CORBA_MAP_SRC_SV_H_

#include <ofdm_api.h>
#include <gr_block_fwd.h> // forward declarations

#include <queue>

class ofdm_corba_map_src_sv;
typedef boost::shared_ptr<ofdm_corba_map_src_sv> ofdm_corba_map_src_sv_sptr;
OFDM_API ofdm_corba_map_src_sv_sptr ofdm_make_corba_map_src_sv(int isubcarriers, std::string sevent_channel, std::string snameservice_ip, std::string snameservice_port);

class corba_push_consumer;

/*!

 */
class OFDM_API ofdm_corba_map_src_sv : public gr_block
{
  private:
    friend ofdm_corba_map_src_sv_sptr ofdm_make_corba_map_src_sv(int isubcarriers, std::string sevent_channel, std::string snameservice_ip, std::string snameservice_port);

    ofdm_corba_map_src_sv(int isubcarriers, std::string sevent_channel, std::string snameservice_ip, std::string snameservice_port);

    int   d_isubcarriers;
    std::string   d_sevent_channel;
    std::string   d_snameservice_ip;
    std::string   d_snameservice_port;
    boost::shared_ptr<corba_push_consumer> d_push_consumer;

    void forecast(int noutput_items, gr_vector_int &ninput_items_required);

    typedef std::queue<char> queue_type;
    typedef std::queue<int> count_queue_type;
    queue_type d_qdata;
    count_queue_type d_cqdata;

  public:
    virtual ~ofdm_corba_map_src_sv();

    virtual bool start();
    virtual bool stop();

    int general_work(
      int noutput_items,
      gr_vector_int &ninput_items,
      gr_vector_const_void_star &input_items,
      gr_vector_void_star &output_items);
};

#endif /* INCLUDED_OFDM_CORBA_MAP_SRC_SV_H_ */
