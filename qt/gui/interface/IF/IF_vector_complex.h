/*
 * IF_vector.h
 *
 *  Created on: 30.01.2012
 *      Author: schmitz
 */

#ifndef IF_VECTOR_COMPLEX_H_
#define IF_VECTOR_COMPLEX_H_

#include "../interface.h"
#include "../types.h"
#include "../unique_id.h"
#include <vector>
#include <stdlib.h>
#include "tao_skeleton/ofdm_tiC.h"
#include <boost/shared_ptr.hpp>
#include "../corba_push_consumer.h"
#include "../corba_push_consumer_rx.h"

class IF_vector_complex : public interface
{
    public:
        IF_vector_complex(){};
        IF_vector_complex (IF_Type if_type, int device) : interface (DataType(vector_float),if_type, device){};
        IF_vector_complex (unique_id ID, corba_push_consumer_rx_sptr consumer) : interface(ID), Consumer_rx_performance_measure(consumer)
        {
            latest_id = Consumer_rx_performance_measure->get_latest_id();
            if (latest_id == -1) return;
                rx_performance_measure_ptr = Consumer_rx_performance_measure->get_rx_performance_measure(latest_id);
        };


        bool getData(std::vector<ofdm_ti::scatter_complex>& data)
        {
            latest_id = -1;
            switch (this->getId().getIfType())
            {
                case IF_Type(scatter):
                    latest_id = Consumer_rx_performance_measure->get_latest_id();
                    if (latest_id == -1) return false;
                    rx_performance_measure_ptr = Consumer_rx_performance_measure->get_rx_performance_measure(latest_id);
                    val_size = rx_performance_measure_ptr->scatter.length();
                    ptr = rx_performance_measure_ptr->scatter.get_buffer();
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

        virtual ~IF_vector_complex(){};
    private:
        short id;
        char* char_ptr;
        ofdm_ti::scatter_complex* ptr;
        int val_size;
        int counter;
        short latest_id;

        std::vector<ofdm_ti::scatter_complex> Data;
        std::vector<ofdm_ti::scatter_complex> Data_char;

        corba_push_consumer_rx_sptr Consumer_rx_performance_measure;
        corba_push_consumer_rx::value_ptr rx_performance_measure_ptr;
};

#endif /* IF_VECTOR_COMPLEX_H_ */




///*
// * IF_vector_complex.h
// *
// *  Created on: 03.12.2008
// *      Author: harries
// */
//
//#ifndef IF_VECTOR_COMPLEX_H_
//#define IF_VECTOR_COMPLEX_H_
//
//#include "../interface.h"
//#include "../types.h"
//#include "../unique_id.h"
//#include <vector>
//#include <complex>
//#include "QtCore/QFile"
//#include "qdatastream.h"
//
//class IF_vector_complex : public interface
//{
//public:
//	IF_vector_complex(){};
//	IF_vector_complex (IF_Type if_type, int device) : interface (DataType(vector_complex),if_type, device){};
//	IF_vector_complex (unique_id ID, QString filename) : interface(ID)
//	{
//		pipe.setFileName(filename);
//		if (pipe.exists()) std::cout << "file found" << std::endl;
//		try {pipe.open( QIODevice::ReadOnly );}
//		catch(...){std::cerr << "could not open file "<<"filename" << std::endl; return;};
//		stream.setDevice(&pipe);
//		stream.setByteOrder(QDataStream::LittleEndian);
//	};
//
//	bool getData(std::vector<complexFloat>& data)
//	{
//		data.clear();
//		for (int i = 0; i < 5000; i++)
//		{
//			stream >> real >> imag;
//			data.push_back(std::complex<float>(real,imag));
//		}
//		return true;
//	};
//
///*	bool getData(double(&x)[10000], double(&y)[10000])
//	{
//		for (int i = 0; i < 500 ; i++)
//		{
//			stream >> x[i] >> y[i];
//			return true;
//		}
//	}*/
//
//	virtual ~IF_vector_complex(){};
//
//private:
//	std::vector<complexFloat> Data;
//	QDataStream* filestream;
//	QFile pipe;
//	QDataStream stream;
//	float real,imag;
//};
//
//#endif /* IF_VECTOR_COMPLEX_H_ */
