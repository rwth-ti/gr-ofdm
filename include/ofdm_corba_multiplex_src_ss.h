#ifndef INCLUDED_OFDM_CORBA_MULTIPLEX_SRC_SS_H_
#define INCLUDED_OFDM_CORBA_MULTIPLEX_SRC_SS_H_

#include <ofdm_api.h>
#include <gr_block_fwd.h> // forward declarations


#include <queue>

class ofdm_corba_multiplex_src_ss;
typedef boost::shared_ptr<ofdm_corba_multiplex_src_ss> ofdm_corba_multiplex_src_ss_sptr;
OFDM_API ofdm_corba_multiplex_src_ss_sptr ofdm_make_corba_multiplex_src_ss(std::string sevent_channel, std::string snameservice_ip, std::string snameservice_port, bool coding=false);

class corba_push_consumer;

/*!

 */
class OFDM_API ofdm_corba_multiplex_src_ss : public gr_block
{
  private:
    friend ofdm_corba_multiplex_src_ss_sptr ofdm_make_corba_multiplex_src_ss(std::string sevent_channel, std::string snameservice_ip, std::string snameservice_port, bool coding);

    ofdm_corba_multiplex_src_ss(std::string sevent_channel, std::string snameservice_ip, std::string snameservice_port, bool coding);

    std::string   d_sevent_channel;
    std::string   d_snameservice_ip;
    std::string   d_snameservice_port;
    boost::shared_ptr<corba_push_consumer> d_push_consumer;

    typedef std::queue<short> queue_type;
    queue_type d_qdata;
    
    int d_pos;

    int d_bitspermode[9];

    bool d_coding;

    void forecast(int noutput_items, gr_vector_int &ninput_items_required);


  public:
    virtual ~ofdm_corba_multiplex_src_ss();

    virtual bool start();
    virtual bool stop();
    
    virtual int noutput_forecast( gr_vector_int &ninput_items, 
        int available_space, int max_items_avail, 
        std::vector<bool> &input_done );

    int general_work(
      int noutput_items,
      gr_vector_int &ninput_items,
      gr_vector_const_void_star &input_items,
      gr_vector_void_star &output_items);
};

#endif /* INCLUDED_OFDM_CORBA_MULTIPLEX_SRC_SS_H_ */
