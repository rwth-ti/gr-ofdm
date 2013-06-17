/*
 * broker.h
 *
 *  Created on: 03.12.2008
 *      Author: harries
 */

#ifndef BROKER_H_
#define BROKER_H_

#include <list>
#include <vector>
#include <iostream>
#include "IF_ident.h"
#include "types.h"
#include "IF/IF_scalar_complex.h"
#include "IF/IF_scalar_float.h"
#include "IF/IF_scalar_int.h"
#include "IF/IF_vector_complex.h"
#include "IF/IF_vector_float.h"
#include "IF/IF_vector_int.h"
#include "IF/IF_transmission_data.h"
#include "IF/IF_rx_performance.h"
#include "IF/IF_power_control.h"
#include "IF/IF_scatter_control.h"
#include "IF/IF_tx_control.h"
#include "boost/shared_ptr.hpp"
#include "corba_push_consumer.h"
#include "corba_push_consumer_rx.h"
#include "corba_push_consumer_rxbas.h"
#include "orb.h"


class broker
{
public:
	//broker();
	broker(std::string namingservice_id, std::string port, int id = -1);
	virtual ~broker();

	//refreshes the list of interfaces sent by CORBA
	//(not implemented yet)
	bool update(int stationID = 100);

	//returns list of data sent by a specific device
	std::list< boost::shared_ptr<IF_ident> > find(int deviceNumber);

	//returns list of data of a specific type of interface (for example "signal noise ratio")
	std::list< boost::shared_ptr<IF_ident> > find(IF_Type type);

	//returns the complete list of available data
	std::list< boost::shared_ptr<IF_ident> > getIfList();


private:
	std::list< boost::shared_ptr<IF_ident> > IF_List;

	corba_push_consumer_sptr tx_data;
	corba_push_consumer_rx_sptr rx_measure;
	corba_push_consumer_rxbas_sptr rx_bb;
	ofdm_ti::info_tx_ptr info_ptr;
	ofdm_ti::PA_Ctrl_ptr strategy_ptr;
	boost::shared_ptr<orb_wrapper> wrapper;
	int stationid;
};

#endif /* BROKER_H_ */
