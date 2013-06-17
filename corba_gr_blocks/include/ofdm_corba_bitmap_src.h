#ifndef INCLUDED_OFDM_CORBA_BITMAP_SRC_H_
#define INCLUDED_OFDM_CORBA_BITMAP_SRC_H_

#include <ofdm_api.h>
#include <gr_block_fwd.h> // forward declarations

class ofdm_corba_bitmap_src;
typedef boost::shared_ptr<ofdm_corba_bitmap_src> ofdm_corba_bitmap_src_sptr;

OFDM_API ofdm_corba_bitmap_src_sptr
ofdm_make_corba_bitmap_src( int vlen, int station_id, std::string event_channel,
    std::string nameservice_ip, std::string nameservice_port );

class corba_push_consumer;
typedef boost::shared_ptr<corba_push_consumer> corba_push_consumer_sptr;


/*!
 *
 * station_id == 0 - output entire bit map
 * else output masked bitmap, subcarrier with id != station_id set to 0
 *
 */
class OFDM_API ofdm_corba_bitmap_src : public gr_sync_interpolator
{
  private:
    friend ofdm_corba_bitmap_src_sptr ofdm_make_corba_bitmap_src( int vlen,
        int station_id, std::string event_channel, std::string nameservice_ip,
        std::string nameservice_port );

    ofdm_corba_bitmap_src( int vlen, int station_id, std::string event_channel,
        std::string nameservice_ip, std::string nameservice_port );

    int             d_vlen;
    int             d_station_id;
    std::string     d_event_channel;
    std::string     d_nameservice_ip;
    std::string     d_nameservice_port;

    short           d_last_id;

    corba_push_consumer_sptr d_push_consumer;

    void set_map_for_idblock( char * const map );
    void store_map( void * config_data );

    typedef char achar __attribute__ ((__aligned__(16)));
    achar * d_map;


  public:

    virtual ~ofdm_corba_bitmap_src();

    virtual bool start();
    virtual bool stop();


    int work(
      int noutput_items,
      gr_vector_const_void_star &input_items,
      gr_vector_void_star &output_items );

};

#endif /* INCLUDED_OFDM_CORBA_BITMAP_SRC_H_ */
