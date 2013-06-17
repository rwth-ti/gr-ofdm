#include "corba_push_supplier.h"
#include "corba_push_supplier_wrapper.h"
#include "tao/AnyTypeCode/Any.h"
#include "tao_skeleton/ofdm_tiC.h"

#include <iostream>

std::string nameservice_host = "localhost";

void test_supplier () {
	CORBA::Any event;
	CORBA::ULong t = 42;
	event <<= t;

	corba_push_supplier supplier ( nameservice_host, "50001" );
	supplier.set_event_channel ( "GNUradio_EventChannel" );

	// Dominik
	sleep(1);
	std::cout << "push" << std::endl;
	supplier.push(event);
	sleep(1);
	// --

//	supplier.disconnect_push_supplier();
	sleep(2);
}

void test_supplier_wrapper () {
	ofdm_ti::rx_performance_measure data;

	corba_push_supplier_wrapper wrapper ( nameservice_host, "50001" );
	wrapper.set_event_channel ( "GNUradio_EventChannel" );

	sleep ( 1 );
	std::cout << "wrapper push" << std::endl;
	wrapper.push ( data );
	sleep ( 1 );

//	wrapper.disconnect_push_supplier();
	sleep ( 2 );
}

int main(int argc, char **argv)
{
	test_supplier ();
	test_supplier_wrapper ();
	return 0;
}
