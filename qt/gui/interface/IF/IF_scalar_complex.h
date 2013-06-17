/*
 * IF_scalar_complex.h
 *
 *  Created on: 03.12.2008
 *      Author: harries
 */

#ifndef IF_SCALAR_COMPLEX_H_
#define IF_SCALAR_COMPLEX_H_

#include "../interface.h"
#include "../types.h"
#include "../unique_id.h"
#include "tao_skeleton/ofdm_tiC.h"
#include <boost/shared_ptr.hpp>
#include "../corba_push_consumer_rx.h"
#include <iostream>

class IF_scalar_complex : public interface
{
    public:
        IF_scalar_complex (IF_Type if_type, int device) : interface (DataType(scalar_complex),if_type, device){};
        IF_scalar_complex (unique_id ID, corba_push_consumer_rx_sptr consumer) : interface(ID), Consumer_rx_performance_measure(consumer)
        {
            try
            {
                latest_id = Consumer_rx_performance_measure->get_latest_id();
                if (latest_id == -1) return;
                rx_performance_measure_ptr = Consumer_rx_performance_measure->get_rx_performance_measure(latest_id);
            }
            catch (...)
            {
                std::cerr << "no rx-performance consumer" << std::endl;
            }
        };

        bool getData(ofdm_ti::scatter_complex& data)
        {
            latest_id = -1;
            switch (this->getId().getIfType())
            {
                case IF_Type(scatter):
                    latest_id = Consumer_rx_performance_measure->get_latest_id();
                    if (latest_id == -1) return false;
                    rx_performance_measure_ptr = Consumer_rx_performance_measure->get_rx_performance_measure(latest_id);
                    //FIXME this file now broken
                    //data = rx_performance_measure_ptr->scatter;
                    return true;
                    break;
                default:
                    return false;
            }
        };


        virtual ~IF_scalar_complex(){};

    private:
        short latest_id;

        std::vector<ofdm_ti::scatter_complex> Data;
        std::vector<ofdm_ti::scatter_complex> Data_char;

        corba_push_consumer_rx_sptr Consumer_rx_performance_measure;
        corba_push_consumer_rx::value_ptr rx_performance_measure_ptr;

};

#endif /* IF_SCALAR_COMPLEX_H_ */
