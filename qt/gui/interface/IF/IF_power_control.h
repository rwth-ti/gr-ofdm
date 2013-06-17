/*
 * IF_power_control.h
 *
 *  Created on: 12.02.2009
 *      Author: harries
 */

#ifndef IF_POWER_CONTROL_H_
#define IF_POWER_CONTROL_H_

#include "../interface.h"
#include "../types.h"
#include "../unique_id.h"
#include "tao_skeleton/ofdm_tiC.h"
#include "orb.h"
#include <vector>


class IF_power_control : public interface
{
public:
	IF_power_control(){};
	IF_power_control (unique_id ID) : interface(ID) {};
	IF_power_control (unique_id ID, boost::shared_ptr<orb_wrapper> wrapper) : interface(ID), orbwrapper(wrapper)
	{
		try
		{
		CORBA::Object_ptr powerstrategy = orbwrapper->resolve( "ofdm_ti.PA" );
		pa = ofdm_ti::PA_Ctrl::_narrow(powerstrategy);
		}
		catch(std::runtime_error ex)
		{
			std::cout << "ERROR: " << ex.what() << std::endl;
		}

		try
		{
		CORBA::Object_ptr txpower = orbwrapper->resolve( "ofdm_ti.txpower_info");
		power_ptr = ofdm_ti::data_buffer::_narrow(txpower);
		}
		catch(std::runtime_error ex)
		{
			std::cout << "ERROR: " << ex.what() << std::endl;
		}

		try
		{
			CORBA::Object_ptr rxgain = orbwrapper->resolve( "ofdm_ti.rxgain");
			gain_ptr = ofdm_ti::push_vector_f::_narrow(rxgain);
		}
		catch(std::runtime_error ex)
		{
			std::cout << "ERROR: " << ex.what() << std::endl;
		}

		GainValue.length(1);

	};

	bool getData(powercontrol& data)
	{
		if ((CORBA::is_nil(pa)) || (CORBA::is_nil(power_ptr))) return false;
		try
		{
			data.data_rate = pa->data_rate();
			data.power_val = *(power_ptr->get_data()->get_buffer());
		}
		catch (...) {return false;}
		return true;
	};


	bool setgain(const float& rxgain)
	{
		if (CORBA::is_nil(gain_ptr)) return false;

		GainValue[0] = rxgain;
		try {gain_ptr->push(GainValue);}
		catch (...) {std::cerr << "transmission error set_gain()" << std::endl; return false;}
		return true;
	}

	bool setData(const powercontrol& data)
	{
		if(CORBA::is_nil(pa))return false;
		try	{
			pa->change_strategy(data.strategy);
			pa->constraint(data.constraint);
			pa->required_ber(data.required_ber);
			pa->update();
		}
		catch (...)
		{
			std::cerr << "transmission error" << std::endl;
			return false;
		}
		return true;
	};

	virtual ~IF_power_control(){};

private:
	ofdm_ti::PA_Ctrl_var pa;
	ofdm_ti::data_buffer_var power_ptr;
	ofdm_ti::push_vector_f_var gain_ptr;
	ofdm_ti::float_sequence GainValue;
	powercontrol Data;
	boost::shared_ptr<orb_wrapper> orbwrapper;
};

#endif /* IF_POWER_CONTROL_H_ */
