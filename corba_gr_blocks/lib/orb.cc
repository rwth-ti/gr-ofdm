#ifdef HAVE_CONFIG_H
#include "config.h"
#endif

#include "orb.h"

#include <tao/ORB_Core.h>
#include <tao/ORB.h>
#include <orbsvcs/Naming/Naming_Client.h>
#include <orbsvcs/CosNamingC.h>

#include <tao/PortableServer/PortableServer.h>

#include <boost/thread/mutex.hpp>
#include <boost/thread/locks.hpp>
#include <boost/thread/thread.hpp>
#include <boost/thread/barrier.hpp>

#include <iostream>

#include <stdexcept>


typedef boost::shared_ptr<orb_wrapper::detail> detail_sptr;
static boost::mutex init_mutex;
static detail_sptr the_detail;



struct orb_thread
{
  CORBA::ORB_var orb_;
  boost::shared_ptr<boost::barrier> barrier_;
  
  orb_thread( CORBA::ORB_ptr orb, boost::shared_ptr<boost::barrier> barrier ) 
    : orb_( CORBA::ORB::_duplicate( orb ) ),
      barrier_( barrier )
  {
  }
    
  orb_thread( const orb_thread& x )
    : orb_( CORBA::ORB::_duplicate( x.orb_.in() ) ),
      barrier_( x.barrier_ )
  {  
  }
  
  void operator() ()
  {
    barrier_->wait();
    std::cout << "TAO ORB has started" << std::endl;
    orb_->run();
    std::cout << "TAO ORB event loop returned" << std::endl;
  }
};


class orb_wrapper::detail
{
public:
  
  detail( std::string nameservice )
    : d_barrier( new boost::barrier( 2 ) )     
    
  {
    
    try {
      
      std::cout << "NameService URL: " << nameservice << std::endl;
      
      int argc = 0;
      
      // Retrieve the ORB.
      d_orb = CORBA::ORB_init( argc, (char**)0 , 0 );
  
      CORBA::Object_var poa_object  =
        d_orb->resolve_initial_references( "RootPOA" );
  
      PortableServer::POA_var poa =
        PortableServer::POA::_narrow( poa_object.in() );
  
      PortableServer::POAManager_var poa_manager =
        poa->the_POAManager();
  
      poa_manager->activate();
      
      // Initialization of the naming service.
      CORBA::Object_var context_obj = 
        d_orb->string_to_object( nameservice.c_str() );
      
      d_rootcontext = CosNaming::NamingContext::_narrow( context_obj.in() );
      
      if( CORBA::is_nil( d_rootcontext) ){
        std::cerr << "Error, unable to retrieve root naming context" << std::endl;
        throw obj_non_existing( "NameService" );
      }
      
      CORBA::String_var ior = d_orb->object_to_string( d_rootcontext.in() );
      d_nameservice_ior = ior.in();
      
    }
    catch( const CORBA::Exception &ex ) {
      ex._tao_print_exception( "initialize orb, get namingservice client" );
      throw std::runtime_error( "init failed" );
    }
    
    boost::thread t( orb_thread( d_orb.in(), d_barrier ) );
    d_orb_thread = t.move();
    
    // assert that the ORB has started
    d_barrier->wait();

  }
  
  ~detail()
  {
    try {
      
      std::cout << "Try to shutdown the ORB" << std::endl;
      
      d_orb->shutdown( true );
      d_orb->destroy();

      if( d_orb_thread.joinable() ) {
        
        std::cout << "Joining ORB thread" << std::endl;
        d_orb_thread.join();
        
      } else {
        
        std::cout << "ORB thread was not joinable" << std::endl;
        
      }
      
      std::cout << "ORB is destroyed" << std::endl;
      
    } 
    catch( const CORBA::BAD_INV_ORDER &ex ) {
      std::cerr << "ORB was already shutdown, bad inverse order!" << std::endl;
    } 
    catch ( ... ) {
      std::cerr << "Caught unrecognized exception at destruction of orb"
                << "wrapper detail" << std::endl;
    }
    
  }
  
  std::string
  resolve_ior( std::string corba_url )
  {
    
    CORBA::Object_var obj = d_orb->string_to_object( corba_url.c_str() );
    if( CORBA::is_nil( obj ) ){
      return "";
    }
    
    CORBA::String_var c_ior = d_orb->object_to_string( obj.in() );
    
    std::string ior = c_ior.in();
    
    return ior;
    
  }
  
  
  
  boost::thread d_orb_thread;
  boost::shared_ptr<boost::barrier> d_barrier;
  CosNaming::NamingContext_var d_rootcontext;
  std::string d_nameservice_ior;
  
  CORBA::ORB_var d_orb;
  
};


boost::shared_ptr<orb_wrapper>
orb_wrapper::create( std::string nameservice )
{
  
  boost::lock_guard<boost::mutex> l( init_mutex );
  
  if( ! the_detail ) {
    detail_sptr t( new detail( nameservice ) );
    the_detail = t;
  }
  
  // Check for identical NameService
  std::string ior = the_detail->resolve_ior( nameservice );
  if( ior != the_detail->d_nameservice_ior ){
    std::cerr << "Warning: try to initialize ORB with different NameService"
              << std::endl;
  }
  
  return boost::shared_ptr<orb_wrapper>( new orb_wrapper( the_detail ) );
  
}


orb_wrapper::orb_wrapper( detail_sptr my_detail )
  : d_detail( my_detail )
{
  
}



CORBA::ORB_ptr
orb_wrapper::get_ORB()
{
  return d_detail->d_orb.in();
}



CORBA::Object_ptr
orb_wrapper::resolve( std::string name )
{
  CORBA::Object_ptr obj;
  try {
    
    CosNaming::Name cosname (1);
    cosname.length (1);
    cosname[0].id = CORBA::string_dup( name.c_str() );
  
    obj = d_detail->d_rootcontext->resolve( cosname );
    
  } 
  catch( const CosNaming::NamingContext::NotFound &ex )
  {
    throw obj_non_existing( name );
  } 
  catch ( const CORBA::Exception &ex ) {
    ex._tao_print_exception( "RootContext resolve" );
    throw name_resolution_failed( name );
  }
  
  return obj;
  
}
