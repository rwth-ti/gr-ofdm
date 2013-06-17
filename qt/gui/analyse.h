/*
 * analyse.h
 *
 *  Created on: 18.01.2009
 *      Author: harries
 */

#ifndef ANALYSE_H_
#define ANALYSE_H_

#include <QString>
#include "interface/broker.h"

namespace analyse
{
QString analyseId(unique_id id)
{
	QString result;
	result = "Data: ";
	switch (id.getDataType())
	{
	case DataType(power_strategy):
		result += "power strategy";
		break;
	case DataType(scatter_ctrl_data):
	    result += "scatter control";
	    break;
	case DataType(vector_float):
		result += "vector(float)";
		break;
	case DataType(vector_int):
		result += "vector(integer)";
		break;
	case DataType(vector_complex):
		result += "vector(complex)";
		break;
	case DataType(scalar_int):
		result += "scalar(int)";
		break;
	case DataType(scalar_float):
		result += "scalar(float)";
		break;
	case DataType(scalar_complex):
		result += "scalar(complex)";
		break;
	case DataType(transmission_data):
		result += "transmission data";
		break;
	case DataType(rx_performance_values):
		result += "Performance Values";
		break;
	case DataType(unspecified):
		result += "unknown";
		break;
	default:
		result += "unknown";
		break;
	}

	result += "\tType: ";

	switch (id.getIfType())
	{
	case IF_Type(SNR):
		result += "Signal-Noise";
		break;
	case IF_Type(power_control):
		result += "Power Control";
		break;
	case IF_Type(tx_control):
		result += "TX Control";
		break;
	case IF_Type(CTF):
		result += "Transfer Function";
		break;
	case IF_Type(SINRPSC):
		result += "SINR per subcarrier";
		break;
	case IF_Type(rx_bband):
		result += "Rx baseband";
		break;
	case IF_Type(scatter):
		result += "Scatterplot";
		break;
	case IF_Type(scatter_control):
	    result += "Scatterplot control";
	    break;
	case IF_Type(TransmissionData):
		result += "Transmission Data";
		break;
	case IF_Type(power_aloc_scheme):
		result += "Power Allocation Scheme";
		break;
	case IF_Type(rate_aloc_scheme):
		result += "Rate Allocation Scheme";
		break;
	case IF_Type(rx_performance):
		result += "Performance";
		break;
	default:
		result += "unknown";
		break;
	}

	result += "\tDevice Id: ";
	result += QString::number(id.getDeviceNo(),10);

	return result;
}

}
#endif /* ANALYSE_H_ */
