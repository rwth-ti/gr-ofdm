#ifndef CORBA_PUSH_SUPPLIER_WRAPPER_H_
#define CORBA_PUSH_SUPPLIER_WRAPPER_H_

#include <string>
#include "tao_skeleton/ofdm_tiC.h"
class corba_push_supplier;

class corba_push_supplier_wrapper
{
private:
	corba_push_supplier* m_pPushSupplier;

public:
	corba_push_supplier_wrapper ( std::string snameservice_ip, std::string snameservice_port );
	virtual ~corba_push_supplier_wrapper ();

	void push (ofdm_ti::rx_performance_measure& data);
	void push (ofdm_ti::baseband_rx& data);


	bool set_event_channel(std::string sevent_channel_name);
	void disconnect_push_supplier();

	void shutdown();

};

#endif /*CORBA_PUSH_SUPPLIER_WRAPPER_H_*/
