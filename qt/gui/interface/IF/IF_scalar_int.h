/*
 * IF_scalar_int.h
 *
 *  Created on: 03.12.2008
 *      Author: harries
 */

#ifndef IF_SCALAR_INT_H_
#define IF_SCALAR_INT_H_

#include "../interface.h"
#include "../types.h"
#include "../unique_id.h"

class IF_scalar_int : public interface
{
public:
	IF_scalar_int(){};
	IF_scalar_int (IF_Type if_type, int device) : interface (DataType(scalar_int),if_type, device){};
	IF_scalar_int (unique_id ID) : interface(ID) {};

	bool getData(int& data) {data = Data; return true;};

	virtual ~IF_scalar_int() {};

private:
	int Data;
};


#endif /* IF_SCALAR_INT_H_ */
