#ifndef PUSHCONSUMER_I_HPP_
#define PUSHCONSUMER_I_HPP_

#include <orbsvcs/CosEventCommS.h>
#include <tao/AnyTypeCode/Any.h>

#include <boost/shared_ptr.hpp>


// Specific implementation. Hide details
template <typename event_type, typename data_handler>
class pushconsumer_i_
  : public virtual corba_push_consumer::pushconsumer_i
{
private:

  typedef boost::shared_ptr<data_handler> data_handler_sptr;

  data_handler d_data_handler;

public:
  pushconsumer_i_( data_handler & c )
    : d_data_handler( c ),
      disconnected( false )
  {
  }

  bool disconnected;

  void
  push( const CORBA::Any &event )
    //ACE_THROW_SPEC ((CORBA::SystemException))
  {
    // IDL declaration: void push (in any event)
    // make copy of event if we want to keep it!
    // if event_type is a pointer type, we any cast won't make a copy

    if( DEBUG_OUT > 1 )
      std::cout << "[pushconsumer_i_] Got Event" << std::endl;

    event_type data;
    if( event >>= data ) {
      d_data_handler( data );
    }
  }

  void
  disconnect_push_consumer(ACE_ENV_SINGLE_ARG_DECL_NOT_USED)
    //ACE_THROW_SPEC ((CORBA::SystemException))
  {
    disconnected = true;
  }

};

// Convenience function. Template parameters automatically determined
template<typename et, typename data_handler>
pushconsumer_i_<et,data_handler> *
pushconsumer_i_create( data_handler c, et dummy)
{
  return new pushconsumer_i_<et,data_handler>( c );
}


#endif /*PUSHCONSUMER_I_HPP_*/
