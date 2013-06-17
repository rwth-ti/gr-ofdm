/*
 * if_ident.h
 *
 *  Created on: 03.12.2008
 *      Author: harries
 */

#ifndef IF_IDENT_H_
#define IF_IDENT_H_

#include "unique_id.h"
#include "types.h"

//a class that owns a unique identification number for the interface

class IF_ident {
public:
	IF_ident(){};
	IF_ident(DataType dtype, IF_Type iftype, int dev) : privateId(unique_id(dtype,iftype,dev)){};
	IF_ident(unique_id ID) : privateId(ID) {};
	virtual ~IF_ident() {};

	unique_id getId(){return privateId;};
	void setDeviceNo(int no){privateId.setDeviceNo(no);};

protected:
	unique_id privateId;
};


#endif /* IF_IDENT_H_ */
