
#include <ofdm/corba_push_consumer.h>

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

#include <ofdm/orb.h>

#define DEBUG_OUT 0


// Base class
struct corba_push_consumer::pushconsumer_i
  :  public virtual POA_CosEventComm::PushConsumer
{
};

#include <ofdm/pushconsumer_i.hpp>


// singleton pattern for corba push consumer
// one consumer client and one table makes communication faster

static boost::mutex s_pushconsumer_singleton_mutex;
static corba_push_consumer_sptr s_pushconsumer_singleton;


corba_push_consumer_sptr
get_corba_push_consumer_singleton( std::string snameservice_ip,
    std::string snameservice_port )
{
  boost::unique_lock<boost::mutex> lock( s_pushconsumer_singleton_mutex );

  if( !s_pushconsumer_singleton ) {

    corba_push_consumer_sptr t( new corba_push_consumer( snameservice_ip,
        snameservice_port ) );

    s_pushconsumer_singleton = t;

  }

  return s_pushconsumer_singleton;
}

corba_push_consumer::corba_push_consumer( std::string snameservice_ip,
    std::string snameservice_port )

  : d_subscribed(false),
    d_subscribe_mutex( new boost::mutex() ),
    d_subscribe_cond( new boost::condition_variable() ),
    d_data_mutex( new boost::shared_mutex() ),
    d_data_cond( new boost::condition_variable_any() ),

    d_pushconsumer_client( pushconsumer_i_create(
        boost::bind( &corba_push_consumer::store_tx_config, this, _1 ),
        (ofdm_ti::tx_config_data*)0 ) ),

    d_interrupt_requested( false )

{
	d_tx_config_deque.clear();
	d_size_of_storage = 10;

	std::string nameservice_url = "corbaloc:iiop:" + snameservice_ip +
	  ":" + snameservice_port + "/NameService";

	d_orb_wrapper = orb_wrapper::create( nameservice_url );
}


bool
corba_push_consumer::subscribe_event_channel( std::string sevent_channel_name )
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
corba_push_consumer::ready()
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

void corba_push_consumer::shutdown(void)
{
  interrupt();
}

corba_push_consumer::~corba_push_consumer()
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


corba_push_consumer::tx_config_buffer_type::value_type
corba_push_consumer::get_tx_config( short id, bool block /* = false */ ) const
{

  boost::shared_lock<boost::shared_mutex> lock( *d_data_mutex );

  tx_config_buffer_type::const_iterator iter;
  if(block){ // blocking

    while( true ){
      iter = find(id);

      if( iter != d_tx_config_deque.end() )
        return *iter;

      if( DEBUG_OUT > 1 ) {
        std::cout << "[corba push consumer] blocks in "
                  << "get_tx_config(" << id << ")" << std::endl
                  << std::flush;
      }


      boost::system_time timeout =
        boost::get_system_time() + boost::posix_time::milliseconds(500);

      while( !d_data_cond->timed_wait( lock, timeout ) )
      {
        if( d_interrupt_requested )
        {
          return corba_push_consumer::tx_config_buffer_type::value_type();
        }

        timeout = boost::get_system_time() +
                  boost::posix_time::milliseconds(500);
      }

    }

  } else { //non-blocking

    iter = find(id);
    if(iter != d_tx_config_deque.end()){
      return *iter;
    }

    return corba_push_consumer::tx_config_buffer_type::value_type();

  }

}



class corba_push_consumer::id_predicate
{
public:
  id_predicate(const short id) : d_id(id) {};

  bool operator()( corba_push_consumer::tx_config_buffer_type::value_type p )
  {
    return p->tx_id == d_id;
  }

private:

  short d_id;

};


corba_push_consumer::tx_config_buffer_type::const_iterator
corba_push_consumer::find(const short id) const
{
  tx_config_buffer_type::const_iterator  iter =
     std::find_if( d_tx_config_deque.begin(), d_tx_config_deque.end(),
         id_predicate( id ) );

  return iter;
}



bool
corba_push_consumer::store_tx_config(
    const ofdm_ti::tx_config_data * const new_config_item )
{
  {

    boost::unique_lock<boost::shared_mutex> lock( *d_data_mutex );

    if(d_tx_config_deque.size() >= d_size_of_storage)
    {
      d_tx_config_deque.pop_back();
    }

    tx_config_buffer_type::value_type t( new ofdm_ti::tx_config_data(
        *new_config_item ) );

    d_tx_config_deque.push_front( t );

  }

  d_data_cond->notify_all();

  if( DEBUG_OUT > 1 ) {
    std::cout << "[corba pushconsumer] store tx config( "
              << d_tx_config_deque.front()->tx_id << " )" << std::endl;
  }

  return true;
}


short
corba_push_consumer::get_latest_id() const
{
  boost::shared_lock<boost::shared_mutex> lock( *d_data_mutex );

  while ( d_tx_config_deque.size() == 0 )
  {
    boost::system_time const timeout =
      boost::get_system_time() + boost::posix_time::milliseconds(500);

    d_data_cond->timed_wait( lock, timeout );

    if( d_interrupt_requested ){
      return -1;
    }
  }

  return d_tx_config_deque.front()->tx_id;
}

void
corba_push_consumer::clear()
{
  boost::unique_lock<boost::shared_mutex> lock( *d_data_mutex );
  d_tx_config_deque.clear();
  d_interrupt_requested = false;
}
