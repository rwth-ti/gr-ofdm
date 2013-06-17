/*
 * gui_rx.cpp
 *
 *  Created on: May 12, 2009
 *      Author: harries
 */

#include "gui_rx.h"
#include <qwt_plot_curve.h>
#include "./interface/broker.h"


gui_rx::gui_rx(std::string namingservice, std::string port, int id, QWidget *parent) : 	QWidget(parent),
    myBroker (new broker(namingservice, port, id)),
    myLayout (new QGridLayout(this))
{

    Action_Screenshot = new QAction(tr("Make Screenshot"), this);
    connect(Action_Screenshot, SIGNAL(triggered()), this, SLOT(makeScreenshot()));

    this->setWindowTitle(QString("RX View"));

    interfaces = myBroker->getIfList();

    WidgetList.clear();
    std::list< boost::shared_ptr<IF_ident> >::iterator if_it;
    std::list< boost::shared_ptr<QWidget> >::iterator w_it;

    for (if_it = interfaces.begin(); if_it != interfaces.end(); if_it++)
    {
        WidgetList.push_back(createWidget(*if_it));
        std::cout << "widget created..." << std::endl;
    }

    std::cout << "list size: "<< WidgetList.size() << std::endl;
    for (w_it = WidgetList.begin(); w_it != WidgetList.end(); w_it++)
    {
        if ((*w_it) != NULL) myLayout->addWidget((*w_it).get());
        std::cout << "widget added..." << std::endl;
    }
}

void gui_rx::makeScreenshot()
{
    QPixmap newMap = QPixmap::grabWindow(this->winId());

    QString format = "png";
    QString initialPath = QDir::currentPath() + tr("/untitled.") + format;

    QString fileName = QFileDialog::getSaveFileName(this, tr("Save As"),
            initialPath,
            tr("%1 Files (*.%2);;All Files (*)")
            .arg(format.toUpper())
            .arg(format));

    if (!fileName.isEmpty())
        std::cout << "screenshot: " << newMap.save(fileName,format.toAscii()) << std::endl;
}

boost::shared_ptr<QWidget> gui_rx::createWidget(boost::shared_ptr<IF_ident> interface)
{
    IF_Type type = interface->getId().getIfType();
    std::cout << "type: " << type << std::endl;
    if (type == IF_Type(tx_control))
    {
        boost::shared_ptr<widget_tx_ctrl> newPlot (new widget_tx_ctrl);
        newPlot->setData(interface);
        return newPlot;
    }
    if (type == IF_Type(rx_performance))
    {
        boost::shared_ptr<Performance> newPlot (new Performance);
        newPlot->setData(interface);
        return newPlot;
    }
    if (type == IF_Type(CTF))
    {
        boost::shared_ptr<barplot> newPlot (new barplot);
        newPlot->setData(interface);
        return newPlot;
    }
//    if (type == IF_Type(rx_bband))
//    {
//        boost::shared_ptr<lineplot> newPlot (new lineplot);
//        newPlot->setData(interface);
//        return newPlot;
//    }
    if (type == IF_Type(scatter))
    {
        boost::shared_ptr<scatterplot> newPlot (new scatterplot);
        newPlot->setData(interface);
        return newPlot;
    }
    if (type == IF_Type(scatter_control))
    {
        boost::shared_ptr<widget_scatter_ctrl> newPlot (new widget_scatter_ctrl);
        newPlot->setData(interface);
        return newPlot;
    }
    else return boost::shared_ptr<QWidget>();
}

void gui_rx::mouseReleaseEvent(QMouseEvent*e)
{
    if (e->button() != Qt::RightButton) return;
    QMenu menu(this);
    menu.addAction(Action_Screenshot);
    menu.exec(e->globalPos());
}

gui_rx::~gui_rx() {
    // TODO Auto-generated destructor stub
}
