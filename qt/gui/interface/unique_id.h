/*
 * unique_id.h
 *
 *  Created on: 03.12.2008
 *      Author: harries
 */

#ifndef UNIQUE_ID_H_
#define UNIQUE_ID_H_

#include "types.h"
#include <string>

//a class that controls the specific values of an interface

class unique_id
{
public:
	unique_id(){};
	virtual ~unique_id(){};

	unique_id(DataType dtype, IF_Type if_type, int dev = 0) : dType (dtype), ifType(if_type), device(dev){};

	void setDeviceNo(int no){device=no;};
	DataType getDataType()  {return dType;};
	IF_Type getIfType()		{return ifType;};
	int getDeviceNo()		{return device;};

private:
	DataType	dType;
	IF_Type		ifType;
	int 		device;
};

#endif /* UNIQUE_ID_H_ */
