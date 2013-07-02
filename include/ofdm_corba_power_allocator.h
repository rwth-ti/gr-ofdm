#ifndef INCLUDED_OFDM_CORBA_POWER_ALLOCATOR_H_
#define INCLUDED_OFDM_CORBA_POWER_ALLOCATOR_H_

#include <ofdm_api.h>
#include <gr_block_fwd.h> // forward declarations

class ofdm_corba_power_allocator;
typedef boost::shared_ptr<ofdm_corba_power_allocator>
  ofdm_corba_power_allocator_sptr;

OFDM_API ofdm_corba_power_allocator_sptr ofdm_make_corba_power_allocator(int vlen,
    std::string event_channel, std::string nameservice_ip,
    std::string nameservice_port, bool allocate = true);

class corba_push_consumer;

/*! \brief Power De-/Allocator with CORBA control event channel interface
 *
 * \param allocate  If true allocate power, else deallocate
 *
 */
class OFDM_API ofdm_corba_power_allocator : public gr_block
{
  private:
    friend ofdm_corba_power_allocator_sptr
    ofdm_make_corba_power_allocator(int vlen, std::string event_channel,
        std::string nameservice_ip, std::string nameservice_port,
        bool allocate);

    ofdm_corba_power_allocator(int vlen, std::string event_channel,
        std::string nameservice_ip, std::string nameservice_port,
        bool allocate);

    int             d_vlen;
    std::string     d_event_channel;
    std::string     d_nameservice_ip;
    std::string     d_nameservice_port;
    bool            d_allocate;



    boost::shared_ptr<corba_push_consumer> d_push_consumer;

    int             d_need_id;

    short           d_last_id;

    typedef float afloat __attribute__ ((__aligned__(16)));
    afloat * d_last_powermap;

    void forecast(int noutput_items, gr_vector_int &ninput_items_required);

    void get_power_map( short id );


  public:
    virtual ~ofdm_corba_power_allocator();

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

#endif /* INCLUDED_OFDM_CORBA_POWER_ALLOCATOR_H_ */
