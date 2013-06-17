/*
 * IF_vector.h
 *
 *  Created on: 03.12.2008
 *      Author: harries
 */

#ifndef IF_VECTOR_FLOAT_H_
#define IF_VECTOR_FLOAT_H_

#include "../interface.h"
#include "../types.h"
#include "../unique_id.h"
#include <vector>
#include <stdlib.h>
#include "tao_skeleton/ofdm_tiC.h"
#include <boost/shared_ptr.hpp>
#include "../corba_push_consumer.h"
#include "../corba_push_consumer_rx.h"
#include "../corba_push_consumer_rxbas.h"

class IF_vector_float : public interface
{
public:
	IF_vector_float(){};
	IF_vector_float (IF_Type if_type, int device) : interface (DataType(vector_float),if_type, device){};
	IF_vector_float (unique_id ID, corba_push_consumer_sptr consumer) : interface(ID), Consumer_tx_config(consumer){};
	IF_vector_float (unique_id ID, corba_push_consumer_rx_sptr consumer) : interface(ID), Consumer_rx_performance_measure(consumer)
	{
		try
		{
			latest_id = Consumer_rx_performance_measure->get_latest_id();
			if (latest_id == -1) return;
			rx_performance_measure_ptr = Consumer_rx_performance_measure->get_rx_performance_measure(latest_id);
			//this->setDeviceNo(rx_performance_measure_ptr->rx_station);
		}
		catch (...)
		{
			std::cerr << "no rx-performance consumer" << std::endl;
		}
	};

	IF_vector_float (unique_id ID, corba_push_consumer_rxbas_sptr consumer) : interface(ID), Consumer_rx_baseband(consumer)
			{
				latest_id = Consumer_rx_baseband->get_latest_id();
				if (latest_id == -1) return;
				rx_baseband_ptr = Consumer_rx_baseband->get_rx_baseband(latest_id);
				//this->setDeviceNo(rx_baseband_ptr->rx_station);
			};


	bool getData(std::vector<float>& data)
	{
		latest_id = -1;
		switch (this->getId().getIfType())
		{
		case IF_Type(power_aloc_scheme):
			latest_id = Consumer_tx_config->get_latest_id();
			if (latest_id == -1) return false;
			tx_config_ptr = Consumer_tx_config->get_tx_config(latest_id);
			val_size = tx_config_ptr->power_map.length();
			ptr = tx_config_ptr->power_map.get_buffer();

			data.clear();

			for (counter = 0; counter < val_size; counter++ )
			{
				data.push_back(*ptr);
				ptr++;
			}
			return true;
			break;
		case IF_Type(rate_aloc_scheme):
			latest_id = Consumer_tx_config->get_latest_id();
			if (latest_id == -1) return false;
			tx_config_ptr = Consumer_tx_config->get_tx_config(latest_id);
			val_size = tx_config_ptr->mod_map.length();
			char_ptr = (char*) tx_config_ptr->mod_map.get_buffer();
			data.clear();

			for (counter = 0; counter < val_size; counter++ )
			{
				data.push_back(*char_ptr);
				char_ptr++;
			}
			return true;
			break;
		case IF_Type(CTF):
			latest_id = Consumer_rx_performance_measure->get_latest_id();
			if (latest_id == -1) return false;
			rx_performance_measure_ptr = Consumer_rx_performance_measure->get_rx_performance_measure(latest_id);
			val_size = rx_performance_measure_ptr->ctf.length();
			ptr = rx_performance_measure_ptr->ctf.get_buffer();
			data.clear();

			for (counter = 0; counter < val_size; counter++ )
			{
				data.push_back(*ptr);
				ptr++;
			}
			return true;
			break;
		case IF_Type(SINRPSC):
			latest_id = Consumer_rx_performance_measure->get_latest_id();
			if (latest_id == -1) return false;
			rx_performance_measure_ptr = Consumer_rx_performance_measure->get_rx_performance_measure(latest_id);
			val_size = rx_performance_measure_ptr->est_sinr_sc.length();
			ptr = rx_performance_measure_ptr->est_sinr_sc.get_buffer();
			data.clear();

			for (counter = 0; counter < val_size; counter++ )
			{
				data.push_back(*ptr);
				ptr++;
			}
			return true;
			break;
		case IF_Type(rx_bband):
			latest_id = Consumer_rx_baseband->get_latest_id();
			if (latest_id == -1) return false;
			rx_baseband_ptr = Consumer_rx_baseband->get_rx_baseband(latest_id);
			val_size = rx_baseband_ptr->bband.length();
			ptr = rx_baseband_ptr->bband.get_buffer();
			data.clear();

			for (counter = 0; counter < val_size; counter++ )
			{
				data.push_back(*ptr);
				ptr++;
			}
			return true;
			break;
		default:
			return false;
		}
	};

	virtual ~IF_vector_float(){};
private:
	short id;
	char* char_ptr;
	float* ptr;
	int val_size;
	int counter;
	short latest_id;

	std::vector<float> Data;
	std::vector<float> Data_char;
	corba_push_consumer_sptr Consumer_tx_config;
	corba_push_consumer_rx_sptr Consumer_rx_performance_measure;
	corba_push_consumer_rxbas_sptr Consumer_rx_baseband;

	corba_push_consumer::value_ptr tx_config_ptr;
	corba_push_consumer_rx::value_ptr rx_performance_measure_ptr;
	corba_push_consumer_rxbas::value_ptr rx_baseband_ptr;

};

#endif /* IF_VECTOR_FLOAT_H_ */
