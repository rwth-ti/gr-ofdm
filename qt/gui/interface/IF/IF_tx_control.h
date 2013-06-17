/*
 * IF_tx_control.h
 *
 *  Created on: 14.02.2012
 *      Author: schmitz
 */

#ifndef IF_TX_CONTROL_H_
#define IF_TX_CONTROL_H_

#include "../interface.h"
#include "../types.h"
#include "../unique_id.h"
#include "tao_skeleton/ofdm_tiC.h"
#include "orb.h"
#include <vector>


class IF_tx_control : public interface
{
    public:
        IF_tx_control(){};
        IF_tx_control (unique_id ID) : interface(ID) {};
        IF_tx_control (unique_id ID, boost::shared_ptr<orb_wrapper> wrapper) : interface(ID), orbwrapper(wrapper)
    {
        try
        {
            CORBA::Object_ptr transmitter = orbwrapper->resolve( "ofdm_ti.PA" );
            pa = ofdm_ti::PA_Ctrl::_narrow(transmitter);
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
    };

        bool getData(powercontrol& data)
        {
            if ((CORBA::is_nil(pa)) || (CORBA::is_nil(power_ptr))) return false;
            try
            {
                data.data_rate = pa->data_rate();
                data.power_val = *(power_ptr->get_data()->get_buffer());
                data.modulation = pa->modulation();
            }
            catch (...) {return false;}
            return true;
        };

        bool setData(const powercontrol& data)
        {
            if(CORBA::is_nil(pa))return false;
            try	{
                pa->constraint(data.constraint);
                pa->modulation(data.modulation);
                pa->freqoff(data.freqoff);
                pa->update();
            }
            catch (...)
            {
                std::cerr << "transmission error" << std::endl;
                return false;
            }
            return true;
        };

        virtual ~IF_tx_control(){};

    private:
        ofdm_ti::PA_Ctrl_var pa;
        ofdm_ti::data_buffer_var power_ptr;
        ofdm_ti::push_vector_f_var gain_ptr;
        ofdm_ti::float_sequence GainValue;
        powercontrol Data;
        boost::shared_ptr<orb_wrapper> orbwrapper;
};

#endif /* IF_TX_CONTROL_H_ */

