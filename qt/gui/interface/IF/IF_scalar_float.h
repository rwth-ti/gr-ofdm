/*
 * IF_scalar_float.h
 *
 *  Created on: 03.12.2008
 *      Author: harries
 */

#ifndef IF_SCALAR_FLOAT_H_
#define IF_SCALAR_FLOAT_H_

#include "../interface.h"
#include "../types.h"
#include "../unique_id.h"

class IF_scalar_float : public interface
{
public:
	IF_scalar_float (IF_Type if_type, int device) : interface (DataType(scalar_float),if_type, device){};
	IF_scalar_float(){};
	IF_scalar_float (unique_id ID) : interface(ID) {};

	bool getData(float& data) {data = Data; return true;};

	virtual ~IF_scalar_float(){};

private:
	float Data;
};

#endif /* IF_SCALAR_FLOAT_H_ */
