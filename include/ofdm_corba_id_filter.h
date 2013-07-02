#ifndef INCLUDED_OFDM_CORBA_ID_FILTER_H_
#define INCLUDED_OFDM_CORBA_ID_FILTER_H_

#include <ofdm_api.h>
#include <gr_block_fwd.h> // forward declarations

class ofdm_corba_id_filter;
typedef boost::shared_ptr<ofdm_corba_id_filter> ofdm_corba_id_filter_sptr;
OFDM_API ofdm_corba_id_filter_sptr ofdm_make_corba_id_filter(std::string sevent_channel, std::string snameservice_ip, std::string snameservice_port, int max_trials);

class corba_push_consumer;

/*!
 * \brief Try to filter corrupted IDs
 *
 * Connect the ID decoder to the input port. It will try to find the IDs in
 * the CORBA pushconsumer buffer. The ID is copied from input to output if it
 * is known to the CORBA subsystem. Else, there will be \param max_trials
 * trials and if it is still unknown, the ID will be replaced by the
 * latest id that is returned by the CORBA pushconsumer.
 */
class OFDM_API ofdm_corba_id_filter : public gr_sync_block
{
  private:
    friend ofdm_corba_id_filter_sptr ofdm_make_corba_id_filter(std::string sevent_channel, std::string snameservice_ip, std::string snameservice_port, int max_trials);

    ofdm_corba_id_filter(std::string sevent_channel, std::string snameservice_ip, std::string snameservice_port, int max_trials);

    std::string   d_sevent_channel;
    std::string   d_snameservice_ip;
    std::string   d_snameservice_port;
    int   d_max_trials;
    int d_trials;
//    int d_lastid;

    boost::shared_ptr<corba_push_consumer> d_push_consumer;

  public:
    virtual ~ofdm_corba_id_filter() {};

    virtual bool start();
    virtual bool stop();

    int work(
      int noutput_items,
      gr_vector_const_void_star &input_items,
      gr_vector_void_star &output_items);
};

#endif /* INCLUDED_OFDM_CORBA_ID_FILTER_H_ */
