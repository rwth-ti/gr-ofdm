#ifndef INCLUDED_GNURADIO_QTGUI_H
#define INCLUDED_GNURADIO_QTGUI_H

#include <QtGui/QWidget>
#include "ui_gnuradio_qtgui.h"
#include <list>
#include <iostream>
#include <string>
#include "widgets/widget_barplot.h"
#include "widgets/widget_lineplot.h"
#include "widgets/widget_device_info.h"
#include "widgets/widget_rx_performance.h"
#include "widgets/widget_pa_ctrl.h"
#include "widgets/widget_tx_ctrl.h"
#include "widgets/widget_scatter_ctrl.h"
#include "interface/broker.h"
#include <boost/shared_ptr.hpp>
#include "widgets/WidgetControl.h"
#include "Layout.h"
#include "viewWidget.h"
#include "ListElement.h"
#include <QList>


class gnuradio_qtgui : public QWidget
{
    Q_OBJECT

public:
    gnuradio_qtgui(std::string namingservice = "tabur", std::string port = "50001", QWidget *parent = 0);
    ~gnuradio_qtgui();

	void damnit();
	void FISH();


public slots:

    //adds a widget with a specific source
    void addWidget(boost::shared_ptr<IF_ident> dataSource);

    //refreshes the list of available interfaces
    void updateInterfaceList();

    //replots all shown widgets
    void replotWidgets();

    //opens the widget that is selected in the ListWidget - not implemented yet
    void showSelected();

protected:
    virtual void timerEvent(QTimerEvent *e);
    virtual void closeEvent(QCloseEvent *e);

private:

	std::list<boost::shared_ptr<QWidget> > WidgetList;
	std::list< boost::shared_ptr<IF_ident> > interfaces;
	std::list<ListElement> elementList;
    Ui::gnuradio_qtguiClass ui;
    broker* myBroker;
    Layout* myLayout;
    viewWidget* View;

};

#endif // INCLUDED_GNURADIO_QTGUI_H
