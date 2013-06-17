/*
 * IF_transmission_data.h
 *
 *  Created on: 17.01.2009
 *      Author: harries
 */

#ifndef IF_TRANSMISSION_DATA_H_
#define IF_TRANSMISSION_DATA_H_

#include "../interface.h"
#include "../types.h"
#include "../unique_id.h"
#include <vector>
#include "tao_skeleton/ofdm_tiC.h"
#include "orb.h"

class IF_transmission_data : public interface
{
public:
	IF_transmission_data(){};
	IF_transmission_data (IF_Type if_type, int device) : interface (DataType(transmission_data),if_type, device){};
	IF_transmission_data (unique_id ID) : interface(ID) {};
	IF_transmission_data (unique_id ID, boost::shared_ptr<orb_wrapper> w/*ofdm_ti::info_tx_ptr ptr*/) : interface(ID), wrapper(w)/*source(ptr)*/
	{
		try
		{
		CORBA::Object_ptr myObj = wrapper->resolve( "ofdm_ti.info_tx" );
		source = ofdm_ti::info_tx::_narrow(myObj);
		}
		catch(std::runtime_error ex)
		{
			std::cout << "ERROR: " << ex.what() << std::endl;
		}
	};

	bool getData(transmissionData& data)
	{
		if (CORBA::is_nil(source)) return false;
		try
		{
		data.subcarriers = source->subcarriers();
		data.fft_window = source->fft_window();
		data.cp_length = source->cp_length();
		data.carrier_freq = source->carrier_freq();
		data.symbol_time = source->symbol_time();
		data.bandwidth = source->bandwidth();
		data.subbandwidth = source->subbandwidth();
		data.max_datarate = source->max_datarate();
		data.burst_length = source->burst_length();
		}
		catch(...)
		{
			std::cerr << "Instance of 'CORBA::transient' thrown" << std::endl;
			return false;
		}
		return true;
	};

	virtual ~IF_transmission_data(){};

private:
	transmissionData Data;
	ofdm_ti::info_tx_var source;
	boost::shared_ptr<orb_wrapper> wrapper;
};

#endif /* IF_TRANSMISSION_DATA_H_ */
