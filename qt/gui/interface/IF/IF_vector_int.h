/*
 * IF_vector_int.h
 *
 *  Created on: 03.12.2008
 *      Author: harries
 */

#ifndef IF_VECTOR_INT_H_
#define IF_VECTOR_INT_H_

#include "../interface.h"
#include "../types.h"
#include "../unique_id.h"
#include <vector>

class IF_vector_int : public interface
{
public:
	IF_vector_int(){};
	IF_vector_int (IF_Type if_type, int device) : interface (DataType(vector_int),if_type, device){};
	IF_vector_int (unique_id ID) : interface(ID) {};

	bool getData(std::vector<int>& data) {data = Data; return true;};

	virtual ~IF_vector_int(){};
private:
	std::vector<int> Data;
};

#endif /* IF_VECTOR_INT_H_ */
