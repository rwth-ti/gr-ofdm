/*
 * ListElement.h
 *
 *  Created on: 20.01.2009
 *      Author: harries
 */

#ifndef LISTELEMENT_H_
#define LISTELEMENT_H_

#include <boost/shared_ptr.hpp>
#include <QString>
#include <QListWidgetItem>
#include "interface/broker.h"

class ListElement : public QListWidgetItem
{
public:
	ListElement(boost::shared_ptr<IF_ident> IF) : QListWidgetItem(), interface(IF)	{};
	virtual ~ListElement(){};

	boost::shared_ptr<IF_ident> getInterface() {return interface;};

private:
	boost::shared_ptr<IF_ident> interface;
};
#endif /* LISTELEMENT_H_ */
