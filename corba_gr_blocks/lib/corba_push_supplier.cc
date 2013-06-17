#include "corba_push_supplier.h"

// Copied from corba_push_consumer.h:
// -------------------------------------->

#include <iostream>
#include <sstream>
#include <algorithm>
#include <stdexcept>
// <--------------------------------------

#include "orb.h"


corba_push_supplier::corba_push_supplier( std::string snameservice_ip, 
    std::string snameservice_port )

  : d_subscribed( false ),
    d_supplier( this, false )
    
{
  
  std::string nameservice_url = "corbaloc:iiop:" + snameservice_ip +
    ":" + snameservice_port + "/NameService";
  
  d_orb_wrapper = orb_wrapper::create( nameservice_url );
}

corba_push_supplier::~corba_push_supplier() 
{

  try
  {
    // We must deactivate the servant before we leave!
    PortableServer::POA_var poa = d_supplier._default_POA();
    PortableServer::ObjectId_var id = poa->servant_to_id( &d_supplier );
    poa->deactivate_object( id.in() );
  }
  catch ( ... ) {
    std::cerr << "[corba push supplier] failed to deactivate servant"
              << std::endl;
  }
}

bool 
corba_push_supplier::set_event_channel( std::string sevent_channel_name ) 
{
  
  if(d_subscribed)
    return true;
    
  try{
    std::cout << "[corba pushsupplier] set event channel" << std::endl
              << "[corba pushsupplier] Event channel: " 
              << sevent_channel_name << std::endl;
  
    
    //Find EventService & connect to it
    CORBA::Object_var EC_Obj = d_orb_wrapper->resolve( sevent_channel_name );
    CosEventChannelAdmin::EventChannel_var EC = 
      CosEventChannelAdmin::EventChannel::_narrow( EC_Obj.in() );
    
    if( CORBA::is_nil(EC) ) {
      std::cerr << "[corba push consumer] Failed" << std::endl;
      return false;
    }
    
    // The canonical protocol to connect to the EC
    CosEventChannelAdmin::SupplierAdmin_var supplier_admin =
    	EC->for_suppliers();
    
    // ProxyConsumer
    CosEventChannelAdmin::ProxyPushConsumer_var consumer =
      supplier_admin->obtain_push_consumer();
    
    // get supplier reference and implicitly activate
    CosEventComm::PushSupplier_var supplier =
      d_supplier._this();

    // connect it
    consumer->connect_push_supplier( supplier.in() );
    
    // retain copy
    d_consumer = 
      CosEventChannelAdmin::ProxyPushConsumer::_duplicate( consumer );
    
    std::cout << "[corba pushsupplier] set event channel done" << std::endl;
  	
  	d_subscribed = true;
  	
  }
  catch( const CORBA::Exception &ex ) 
  {
    ex._tao_print_exception( "[pushsupplier]" );
    throw std::runtime_error( "[pushsupplier] subscribe event channel failed" );
  }
  catch(...)
  {
    std::cerr << "[pushsupplier subscribe event chan] unknown exception caught" << std::endl;
    throw;
  };
    
  return true;
  
}

void 
corba_push_supplier::push( const CORBA::Any &event ) 
{
  
  if( CORBA::is_nil( d_consumer.in() ) ) {
    std::cerr << "[corba pushsupplier] Disconnected!!" << std::endl;
    throw std::runtime_error( "ProxyConsumer is Nil" );
  }
  
  try {
    d_consumer->push(event);
  }
  catch( const CORBA::Exception &ex )
  {
    ex._tao_print_exception( "pushsupplier push" );
  }
}

void
corba_push_supplier::disconnect_push_supplier()
{
  // We must provide this function. But its functionality is not implemented
  
  std::cerr << "[corba pushsupplier] disconnect push supplier called, might "
            << "not be a good idea! atm not implemented" << std::endl;
  d_subscribed = false;
  d_consumer = CosEventChannelAdmin::ProxyPushConsumer::_nil ();

}

void 
corba_push_supplier::shutdown(void)
{
}

