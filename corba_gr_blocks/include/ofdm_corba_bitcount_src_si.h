#ifndef INCLUDED_OFDM_CORBA_BITCOUNT_SRC_SI_H_
#define INCLUDED_OFDM_CORBA_BITCOUNT_SRC_SI_H_

#include <ofdm_api.h>
#include <gr_block_fwd.h> // forward declarations

class ofdm_corba_bitcount_src_si;
typedef boost::shared_ptr<ofdm_corba_bitcount_src_si> ofdm_corba_bitcount_src_si_sptr;
OFDM_API ofdm_corba_bitcount_src_si_sptr ofdm_make_corba_bitcount_src_si(int istation_id, std::string sevent_channel, std::string snameservice_ip, std::string snameservice_port);

class corba_push_consumer;

/*!

 */
class OFDM_API ofdm_corba_bitcount_src_si : public gr_sync_block
{
  private:
    friend ofdm_corba_bitcount_src_si_sptr ofdm_make_corba_bitcount_src_si(int istation_id, std::string sevent_channel, std::string snameservice_ip, std::string snameservice_port);

    ofdm_corba_bitcount_src_si(int istation_id, std::string sevent_channel, std::string snameservice_ip, std::string snameservice_port);

    int   d_istation_id;
    std::string   d_sevent_channel;
    std::string   d_snameservice_ip;
    std::string   d_snameservice_port;
    boost::shared_ptr<corba_push_consumer> d_push_consumer;

    unsigned int d_bitcount;
    short        d_last_id;

    void store_bitcount( void * cd );

  public:
    virtual ~ofdm_corba_bitcount_src_si();

    virtual bool start();
    virtual bool stop();

    int work(
      int noutput_items,
      gr_vector_const_void_star &input_items,
      gr_vector_void_star &output_items);
};

#endif /* INCLUDED_OFDM_CORBA_BITCOUNT_SRC_SI_H_ */

