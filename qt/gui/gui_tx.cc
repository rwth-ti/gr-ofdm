/*
 * gui_tx.cpp
 *
 *  Created on: May 12, 2009
 *      Author: harries
 */

#include <qwt_plot_curve.h>
#include "./interface/broker.h"
#include "gui_tx.h"

gui_tx::gui_tx(std::string namingservice, std::string port, QWidget *parent) : 	QWidget(parent),
																				myBroker (new broker(namingservice, port)),
																				myLayout (new QGridLayout(this))
{
	this->setWindowTitle(QString("TX View"));

	interfaces = myBroker->getIfList();

	std::list< boost::shared_ptr<IF_ident> >::iterator if_it;
	std::list< boost::shared_ptr<QWidget> >::iterator w_it;

	for (if_it = interfaces.begin(); if_it != interfaces.end(); if_it++)
	{
		WidgetList.push_back(createWidget(*if_it));
	}

	for (w_it = WidgetList.begin(); w_it != WidgetList.end(); w_it++)
	{
		if ((*w_it) != NULL) myLayout->addWidget((*w_it).get());
	}

}

boost::shared_ptr<QWidget> gui_tx::createWidget(boost::shared_ptr<IF_ident> interface)
{
	IF_Type type = interface->getId().getIfType();
	if (type == IF_Type(power_aloc_scheme))
	{
		boost::shared_ptr<barplot> newPlot (new barplot);
		newPlot->setData(interface);
		return newPlot;
	}
	if (type == IF_Type(rate_aloc_scheme))
	{
		boost::shared_ptr<barplot> newPlot (new barplot);
		newPlot->setData(interface);
		return newPlot;
	}
	if (type == IF_Type(SNR))
	{
		boost::shared_ptr<lineplot> newPlot (new lineplot);
		newPlot->setData(interface);
		return newPlot;
	}
	if (type == IF_Type(TransmissionData))
	{
		boost::shared_ptr<device_info> newPlot (new device_info);
		newPlot->setData(interface);
		return newPlot;
	}
	else return boost::shared_ptr<QWidget>();
}


gui_tx::~gui_tx()
{
	// TODO Auto-generated destructor stub
}
