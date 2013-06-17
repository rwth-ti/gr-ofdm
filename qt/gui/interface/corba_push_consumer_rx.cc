
#include "corba_push_consumer_rx.h"

#include <orbsvcs/CosEventCommS.h>
#include <orbsvcs/CosEventChannelAdminS.h>

#include <iostream>
#include <sstream>
#include <algorithm>
#include <list>
#include <stdexcept>


#include <boost/thread/mutex.hpp>
#include <boost/thread/shared_mutex.hpp>
#include <boost/thread/locks.hpp>
#include <boost/thread/condition_variable.hpp>
#include <boost/bind.hpp>
#include <boost/thread/thread_time.hpp>

#include "orb.h"

#define DEBUG_OUT 0


// Base class
/*struct corba_push_consumer_rx::pushconsumer_i
  :  public virtual POA_CosEventComm::PushConsumer
{
};*/

#include "pushconsumer_i.hpp"


// singleton pattern for corba push consumer
// one consumer client and one table makes communication faster

static boost::mutex s_pushconsumer_singleton_mutex;
static corba_push_consumer_rx_sptr s_pushconsumer_rx_singleton;


corba_push_consumer_rx_sptr
get_corba_push_consumer_rx_singleton( std::string snameservice_ip,
    std::string snameservice_port, int station_id /* = -1 */)
{
  boost::unique_lock<boost::mutex> lock( s_pushconsumer_singleton_mutex );

  if( !s_pushconsumer_rx_singleton ) {

    corba_push_consumer_rx_sptr t( new corba_push_consumer_rx( snameservice_ip,
        snameservice_port, station_id ) );

    s_pushconsumer_rx_singleton = t;

  }

  return s_pushconsumer_rx_singleton;
}

corba_push_consumer_rx::corba_push_consumer_rx( std::string snameservice_ip,
    std::string snameservice_port, int station_id )

  : d_subscribed(false),
    d_subscribe_mutex( new boost::mutex() ),
    d_subscribe_cond( new boost::condition_variable() ),
    d_data_mutex( new boost::shared_mutex() ),
    d_data_cond( new boost::condition_variable_any() ),
    d_pushconsumer_client( pushconsumer_i_create(boost::bind( &corba_push_consumer_rx::store_rx_performance_measure, this, _1 ),(ofdm_ti::rx_performance_measure*)0 ) ),
    d_interrupt_requested( false ),
    d_station ( station_id )

{
	d_rx_performance_measure_deque.clear();
	d_size_of_storage = 10;

	std::string nameservice_url = "corbaloc:iiop:" + snameservice_ip +
	  ":" + snameservice_port + "/NameService";

	d_orb_wrapper = orb_wrapper::create( nameservice_url );
	std::cout << "consumer for station " << d_station << std::endl;
}


bool
corba_push_consumer_rx::subscribe_event_channel( std::string sevent_channel_name )
{
  {
    boost::unique_lock<boost::mutex> l( *d_subscribe_mutex );

    if(d_subscribed)
      return true;

    try{

      if( DEBUG_OUT > 0 ) {
        std::cout << "[corba push consumer] subscribe event channel"
                  << std::endl;
      }


       //Find EventService & connect to it
      CORBA::Object_var EC_Obj = d_orb_wrapper->resolve( sevent_channel_name );
      CosEventChannelAdmin::EventChannel_var EC =
        CosEventChannelAdmin::EventChannel::_narrow( EC_Obj.in() );

      if( CORBA::is_nil(EC) ) {
        std::cerr << "[corba push consumer] Failed" << std::endl;
        return false;
      }


      // The canonical protocol to connect to the EC
      CosEventChannelAdmin::ConsumerAdmin_var consumer_admin =
      	EC->for_consumers();

      CosEventChannelAdmin::ProxyPushSupplier_var supplier =
      	consumer_admin->obtain_push_supplier();

      // get consumer and activate it
      CosEventComm::PushConsumer_var consumer =
        d_pushconsumer_client->_this ();

      // connect it
      supplier->connect_push_consumer( consumer.in() );

      if( DEBUG_OUT > 0 ) {
        std::cout << "[corba push consumer] subscribe event channel done"
        << std::endl;
      }


    }
    catch ( const CORBA::Exception &ex ){
      ex._tao_print_exception( "pushconsumer subscribe event channel" );
      throw std::runtime_error("[pushconsumer subscribe event chan] Event channel not registered at NamingContext");
    }
    catch(...){
      std::cerr << "[pushconsumer subscribe event chan] unknown exception caught" << std::endl;
        throw;
    };

    d_subscribed = true;

  } // mutex lock scope

  d_subscribe_cond->notify_all();

  return true;
}

bool
corba_push_consumer_rx::ready()
{
  boost::unique_lock<boost::mutex> lock( *d_subscribe_mutex );

  while( !d_subscribed )
  {
    boost::system_time const timeout =
      boost::get_system_time() + boost::posix_time::milliseconds(500);

    d_subscribe_cond->timed_wait( lock, timeout );

    if( d_interrupt_requested ){
      return false;
    }
  }

  return true;
}

void corba_push_consumer_rx::shutdown(void)
{
  interrupt();
}

corba_push_consumer_rx::~corba_push_consumer_rx()
{
  if( DEBUG_OUT > 0 ) {
    std::cout << "Shutdown corba pushconsumer" << std::endl << std::flush;
  }

  try
  {
    // We must deactivate the servant before we leave!
    PortableServer::POA_var poa = d_pushconsumer_client->_default_POA();
    PortableServer::ObjectId_var id =
      poa->servant_to_id( d_pushconsumer_client.get() );
    poa->deactivate_object( id.in() );
  }
  catch( ... )
  {
    std::cerr << "[corba push consumer] Couldn't deactivate servant"
              << std::endl;
  }
}


corba_push_consumer_rx::rx_performance_measure_buffer_type::value_type
corba_push_consumer_rx::get_rx_performance_measure( short id, bool block /* = false */ ) const
{
  boost::shared_lock<boost::shared_mutex> lock( *d_data_mutex );

  rx_performance_measure_buffer_type::const_iterator iter;
  if(block){ // blocking

    while( true ){
      iter = find(id);

      if( iter != d_rx_performance_measure_deque.end() )
        return *iter;

      if( DEBUG_OUT > 1 ) {
        std::cout << "[corba push consumer] blocks in "
                  << "get_rx_performance_measure(" << id << ")" << std::endl
                  << std::flush;
      }


      boost::system_time timeout =
        boost::get_system_time() + boost::posix_time::milliseconds(500);

      while( !d_data_cond->timed_wait( lock, timeout ) )
      {
        if( d_interrupt_requested )
        {
          return corba_push_consumer_rx::rx_performance_measure_buffer_type::value_type();
        }

        timeout = boost::get_system_time() +
                  boost::posix_time::milliseconds(500);
      }

    }

  } else { //non-blocking

    iter = find(id);
    if(iter != d_rx_performance_measure_deque.end()){
      return *iter;
    }

    return corba_push_consumer_rx::rx_performance_measure_buffer_type::value_type();

  }

}



class corba_push_consumer_rx::id_predicate
{
public:
  id_predicate(const short id) : d_id(id) {};

  bool operator()( corba_push_consumer_rx::rx_performance_measure_buffer_type::value_type p )
  {
    return p->rx_id == d_id;
  }

private:
  short d_id;

};


corba_push_consumer_rx::rx_performance_measure_buffer_type::const_iterator
corba_push_consumer_rx::find(const short id) const
{
	rx_performance_measure_buffer_type::const_iterator  iter =
		std::find_if( d_rx_performance_measure_deque.begin(), d_rx_performance_measure_deque.end(), id_predicate( id ) );

  return iter;
}



bool
corba_push_consumer_rx::store_rx_performance_measure(
    const ofdm_ti::rx_performance_measure * const new_config_item )
{
  {

    boost::unique_lock<boost::shared_mutex> lock( *d_data_mutex );

    if( (d_station != -1) && (new_config_item->rx_station != d_station)) return false;

    if(d_rx_performance_measure_deque.size() >= d_size_of_storage)
    {
      d_rx_performance_measure_deque.pop_back();
    }

    rx_performance_measure_buffer_type::value_type t( new ofdm_ti::rx_performance_measure(
        *new_config_item ) );

    //std::cout << "rx_id " << new_config_item->rx_id << " from " << new_config_item->rx_station << " added" << std::endl;

    d_rx_performance_measure_deque.push_front( t );

  }

  d_data_cond->notify_all();

  if( DEBUG_OUT > 1 ) {
    std::cout << "[corba pushconsumer] store rx performance measure( "
              << d_rx_performance_measure_deque.front()->rx_id << " )" << std::endl;
  }

  return true;
}


short corba_push_consumer_rx::get_latest_id() const
{
  boost::shared_lock<boost::shared_mutex> lock( *d_data_mutex );

  if (d_rx_performance_measure_deque.size() == 0) return -1;

  /*
  while ( d_rx_performance_measure_deque.size() == 0 )
  {
    boost::system_time const timeout = boost::get_system_time() + boost::posix_time::milliseconds(500);

    d_data_cond->timed_wait( lock, timeout );

    if( d_interrupt_requested ){
      return -1;
    }
  }*/

  return d_rx_performance_measure_deque.front()->rx_id;
}

void
corba_push_consumer_rx::clear()
{
  boost::unique_lock<boost::shared_mutex> lock( *d_data_mutex );
  d_rx_performance_measure_deque.clear();
  d_interrupt_requested = false;
}
