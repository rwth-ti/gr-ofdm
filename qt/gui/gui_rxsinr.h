/*
 * gui_rx.h
 *
 *  Created on: May 12, 2009
 *      Author: harries
 */

#ifndef GUI_RXSINR_H_
#define GUI_RXSINR_H_

#include <QtGui/QWidget>
#include <QtGui/QLayout>
#include <list>
#include <iostream>
#include <string>
#include "widgets/widget_barplot.h"
#include "widgets/widget_lineplot.h"
#include "widgets/widget_device_info.h"
#include "widgets/widget_rx_performance.h"
#include "widgets/widget_pa_ctrl.h"
#include "interface/broker.h"
#include <boost/shared_ptr.hpp>
#include "widgets/WidgetControl.h"
#include "Layout.h"
#include "viewWidget.h"
#include "ListElement.h"
#include <QList>
#include <QPixmap>
#include <QMenu>
#include <QMouseEvent>

class gui_rxsinr : public QWidget
{
	Q_OBJECT

public:
	gui_rxsinr(std::string namingservice = "tabur", std::string port = "50001", int id = -1, QWidget *parent = 0);
	virtual ~gui_rxsinr();

public slots:

	void makeScreenshot();

protected:
	virtual void mouseReleaseEvent ( QMouseEvent *e);

private:

	boost::shared_ptr<QWidget> createWidget(boost::shared_ptr<IF_ident> interface);

	std::list<boost::shared_ptr<QWidget> > WidgetList;
	std::list< boost::shared_ptr<IF_ident> > interfaces;
    broker* myBroker;
    QGridLayout* myLayout;
    QAction* Action_Screenshot;
};

#endif /* GUI_RXSINR_H_ */
