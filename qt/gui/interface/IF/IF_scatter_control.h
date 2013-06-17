/*
 * IF_scatter_control.h
 *
 *  Created on: 12.02.2009
 *      Author: harries
 */

#ifndef IF_SCATTER_CONTROL_H_
#define IF_SCATTER_CONTROL_H_

#include "../interface.h"
#include "../types.h"
#include "../unique_id.h"
#include "tao_skeleton/ofdm_tiC.h"
#include "orb.h"
#include <vector>


class IF_scatter_control : public interface
{
public:
    IF_scatter_control(){};
    IF_scatter_control (unique_id ID) : interface(ID) {};
    IF_scatter_control (unique_id ID, boost::shared_ptr<orb_wrapper> wrapper) : interface(ID), orbwrapper(wrapper)
	{
		try {
            CORBA::Object_ptr scatter_ctrl = orbwrapper->resolve( "ofdm_ti.scatter_ctrl");
            scatter_ctrl_ptr = ofdm_ti::push_vector_f::_narrow(scatter_ctrl);
        }
        catch(std::runtime_error ex) {
            std::cout << "ERROR: " << ex.what() << std::endl;
        }
        subc_value.length(1);
	};

    bool set_subc(const float& subc)
    {
        if (CORBA::is_nil(scatter_ctrl_ptr)) return false;
        subc_value[0] = subc;
        try {scatter_ctrl_ptr->push(subc_value);}
        catch (...) {std::cerr << "transmission error set_subc()" << std::endl; return false;}
        return true;
    }

    virtual ~IF_scatter_control(){};

private:
    ofdm_ti::push_vector_f_var scatter_ctrl_ptr;
    ofdm_ti::float_sequence subc_value;
    scattercontrol Data;
	boost::shared_ptr<orb_wrapper> orbwrapper;
};

#endif /* IF_SCATTER_CONTROL_H_ */
