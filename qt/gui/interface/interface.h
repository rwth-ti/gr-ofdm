/*
 * interface.h
 *
 *  Created on: 03.12.2008
 *      Author: harries
 */

#ifndef INTERFACE_H_
#define INTERFACE_H_

#include "IF_ident.h"
#include "types.h"

//a class that controls the behavior of the interface

class interface : public IF_ident
{
public:
	interface() : IF_ident() {};
	interface (DataType dtype, IF_Type iftype, int dev) /* : ident (IF_ident(dtype, iftype, dev)){}; */ : IF_ident(dtype, iftype, dev) {};
	interface (unique_id ID) /*: ident(ID){};*/ : IF_ident(ID) {};
	virtual ~interface() {};

	//starts receiving data
	//not implemented yet
	bool start(){return true;};

	//stops receiving data
	//not implemented yet
	bool stop(){return true;};

/*	unique_id id(){return ident.get_id();}

private:
	IF_ident ident;*/
};

#endif /* INTERFACE_H_ */
