#ifndef CORBA_PUSH_SUPPLIER_H_
#define CORBA_PUSH_SUPPLIER_H_


#include "tao_skeleton/ofdm_tiC.h" // For DataTypes

#include <string>

#include <boost/shared_ptr.hpp>

#include <orbsvcs/CosEventCommS.h>
#include <orbsvcs/CosEventChannelAdminC.h>


class orb_wrapper;
typedef boost::shared_ptr<orb_wrapper> orb_wrapper_sptr;

class corba_push_supplier 
{
private:
  
  bool d_subscribed;

  orb_wrapper_sptr d_orb_wrapper;

  CosEventChannelAdmin::ProxyPushConsumer_var d_consumer;
  POA_CosEventComm::PushSupplier_tie < corba_push_supplier > d_supplier;

public:
  
  corba_push_supplier( std::string snameservice_ip, 
      std::string snameservice_port );
  
  virtual ~corba_push_supplier();
  
  void disconnect_push_supplier();
  
  bool set_event_channel( std::string sevent_channel_name );
  void push( const CORBA::Any &event );
  
  
  void shutdown(void);

};



#endif /* CORBA_PUSH_SUPPLIER_H_ */
