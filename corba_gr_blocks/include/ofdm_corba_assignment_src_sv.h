#ifndef INCLUDED_OFDM_CORBA_ASSIGNMENT_SRC_SV_H_
#define INCLUDED_OFDM_CORBA_ASSIGNMENT_SRC_SV_H_

#include <ofdm_api.h>
#include <gr_block_fwd.h> // forward declarations

#include <queue>

class ofdm_corba_assignment_src_sv;
typedef boost::shared_ptr<ofdm_corba_assignment_src_sv> ofdm_corba_assignment_src_sv_sptr;
OFDM_API ofdm_corba_assignment_src_sv_sptr ofdm_make_corba_assignment_src_sv(int istation_id, int isubcarriers, std::string sevent_channel, std::string snameservice_ip, std::string snameservice_port);

class corba_push_consumer;

/*!
 * \brief Subcarrier assignment source
 * 
 * Output assignment as function of ID input and station id. Either 1 if
 * subcarrier belongs to this station or 0 if not. It will output one
 * zero vector for the ID ofdm block and one vector for the data blocks
 * per frame.
 * 
 * Note: there are only two vector outputted per frame.
 */
class OFDM_API ofdm_corba_assignment_src_sv : public gr_block
{
  private:
    friend ofdm_corba_assignment_src_sv_sptr ofdm_make_corba_assignment_src_sv(int istation_id, int isubcarriers, std::string sevent_channel, std::string snameservice_ip, std::string snameservice_port);

    ofdm_corba_assignment_src_sv(int istation_id, int isubcarriers, std::string sevent_channel, std::string snameservice_ip, std::string snameservice_port);

    int   d_istation_id;
    int   d_isubcarriers;
    std::string   d_sevent_channel;
    std::string   d_snameservice_ip;
    std::string   d_snameservice_port;
    boost::shared_ptr<corba_push_consumer> d_push_consumer;

    void forecast(int noutput_items, gr_vector_int &ninput_items_required);

    typedef std::queue<char> queue_type;
    queue_type d_qdata;

  public:
    virtual ~ofdm_corba_assignment_src_sv();

    virtual bool start();
    virtual bool stop();

    int general_work(
      int noutput_items,
      gr_vector_int &ninput_items,
      gr_vector_const_void_star &input_items,
      gr_vector_void_star &output_items);
};

#endif /* INCLUDED_OFDM_CORBA_ASSIGNMENT_SRC_SV_H_ */
