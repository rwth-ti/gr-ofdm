#include "corba_push_supplier_wrapper.h"
#include "corba_push_supplier.h"
#include "tao/AnyTypeCode/Any.h"

corba_push_supplier_wrapper::corba_push_supplier_wrapper ( std::string snameservice_ip, std::string snameservice_port ) {
	m_pPushSupplier = new corba_push_supplier ( snameservice_ip, snameservice_port );

}

corba_push_supplier_wrapper::~corba_push_supplier_wrapper() {
	if ( m_pPushSupplier != NULL ) {
		delete m_pPushSupplier;
		m_pPushSupplier = NULL;
	}
}

template <class T> void
__push ( corba_push_supplier* pPushSupplier,
    const T& data )
{
	CORBA::Any event;
	event <<= data;
	pPushSupplier -> push ( event );
}

void corba_push_supplier_wrapper::push (ofdm_ti::rx_performance_measure& data) {
	__push ( m_pPushSupplier, data );
}

void corba_push_supplier_wrapper::push (ofdm_ti::baseband_rx& data) {
	__push ( m_pPushSupplier, data );
}

bool corba_push_supplier_wrapper::set_event_channel ( std::string sevent_channel_name ) {
	return m_pPushSupplier -> set_event_channel ( sevent_channel_name );

}

void corba_push_supplier_wrapper::disconnect_push_supplier () {
	m_pPushSupplier -> disconnect_push_supplier ();

}

void corba_push_supplier_wrapper::shutdown()
{
  m_pPushSupplier->shutdown();

}
