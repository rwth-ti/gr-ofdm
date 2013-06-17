/* IF_rx_performance.h
 *
 *  Created on: 17.01.2009
 *      Author: harries
 */

#ifndef IF_RX_PERFORMANCE_H_
#define IF_RX_PERFORMANCE_H_

#include "../interface.h"
#include "../types.h"
#include "../unique_id.h"
#include <vector>
#include "../corba_push_consumer_rx.h"

class IF_rx_performance : public interface
{
public:
	IF_rx_performance(){};
	//IF_rx_performance (IF_Type if_type, int device) : interface (DataType(rx_performance_values),if_type, device){};
	IF_rx_performance (unique_id ID, corba_push_consumer_rx_sptr consumer) : interface(ID), Consumer_rx_performance(consumer)
	{
		try
		{
			latest_id = Consumer_rx_performance->get_latest_id();
			if (latest_id == -1) return;

			rx_performance_ptr = Consumer_rx_performance->get_rx_performance_measure(latest_id);

			if (this->getId().getDeviceNo() == -1) this->setDeviceNo(rx_performance_ptr->rx_station);
		}
		catch (...){std::cerr << "no rx_performance object" << std::endl;}
	};

	bool getData(rx_performance_struct& data)
	{
		latest_id = Consumer_rx_performance->get_latest_id();
		if (latest_id != -1)
			{
			rx_performance_ptr = Consumer_rx_performance->get_rx_performance_measure(latest_id);
			data.ber = rx_performance_ptr->ber;
			data.snr = rx_performance_ptr->snr;
			data.freqoff = rx_performance_ptr->freqoff;
			data.station_id = rx_performance_ptr->rx_station;
			return true;
			}
		else return false;
	};

	virtual ~IF_rx_performance(){};

private:
	rx_performance_struct Data;

	corba_push_consumer_rx_sptr Consumer_rx_performance;

	corba_push_consumer_rx::value_ptr rx_performance_ptr;

	short latest_id;
};

#endif /* IF_RX_PERFORMANCE_H_ */
