// $Id:corba_push_consumer.h 512 2008-06-25 13:42:31Z auras $


#ifndef CORBA_PUSH_CONSUMER_RX_H_
#define CORBA_PUSH_CONSUMER_RX_H_

#include <boost/shared_ptr.hpp>

#include <list>
#include <string>

#include "tao_skeleton/ofdm_tiC.h" // For DataTypes


class orb_wrapper;
typedef boost::shared_ptr<orb_wrapper> orb_wrapper_sptr;

class corba_push_consumer_rx;
typedef boost::shared_ptr<corba_push_consumer_rx> corba_push_consumer_rx_sptr;

namespace boost {
class mutex;
class shared_mutex;
class condition_variable;
class condition_variable_any;
};

class pushconsumer_i;

class corba_push_consumer_rx
{
public:

  typedef boost::shared_ptr<ofdm_ti::rx_performance_measure> value_ptr;

  /** Block until ready/configured. Return false if failed. */
  bool ready();

  bool subscribe_event_channel(std::string sevent_channel_name);

  value_ptr get_rx_performance_measure( short id, bool block = false ) const;

  bool store_rx_performance_measure( const ofdm_ti::rx_performance_measure * const new_config_item);

  short get_latest_id() const;

  //void set_owner(const std::string &name) {};

  void shutdown(void);

  bool subscribed() const { return d_subscribed; }

  void interrupt() { d_interrupt_requested = true; }

  void clear();

  virtual ~corba_push_consumer_rx();

private:

  corba_push_consumer_rx(std::string snameservice_ip, std::string snameservice_port, int station_id);

  friend corba_push_consumer_rx_sptr get_corba_push_consumer_rx_singleton(std::string,std::string, int);

  // note: std::list, since it does not invalidate iterators
  // except for erased items
  typedef std::list<value_ptr> rx_performance_measure_buffer_type;

  class id_predicate;

  bool d_subscribed;
  boost::shared_ptr<boost::mutex> d_subscribe_mutex;
  boost::shared_ptr<boost::condition_variable> d_subscribe_cond;
  boost::shared_ptr<boost::shared_mutex> d_data_mutex;
  boost::shared_ptr<boost::condition_variable_any> d_data_cond;


  orb_wrapper_sptr d_orb_wrapper;

  boost::shared_ptr< pushconsumer_i > d_pushconsumer_client;

  rx_performance_measure_buffer_type d_rx_performance_measure_deque;
  unsigned short d_size_of_storage;
  bool d_interrupt_requested;
  int d_station;

  rx_performance_measure_buffer_type::const_iterator find(const short id) const;
};

corba_push_consumer_rx_sptr
get_corba_push_consumer_rx_singleton(std::string snameservice_ip, std::string snameservice_port, int station_id = -1);

#endif /*CORBA_PUSH_CONSUMER_RX_H_*/
