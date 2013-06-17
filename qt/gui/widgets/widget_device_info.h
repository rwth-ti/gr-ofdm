#ifndef INCLUDED_WIDGET_DEVICE_INFO_H
#define INCLUDED_WIDGET_DEVICE_INFO_H

#include <QtGui/QWidget>
#include "ui_widget_device_info.h"
#include "WidgetControl.h"
#include "../interface/broker.h"
#include <boost/shared_ptr.hpp>
#include <QMenu>
#include <QMouseEvent>


class device_info : public QWidget, public WidgetControl
{
    Q_OBJECT

public:
    device_info(QWidget *parent = 0);
    ~device_info();
    void setData(boost::shared_ptr<IF_ident> dataSource);

protected:
	virtual void mouseReleaseEvent ( QMouseEvent *e);
	//virtual void timerEvent (QTimerEvent *e);

public slots:
	void refresh();

private:
    Ui::widget_device_infoClass ui;
    boost::shared_ptr<IF_ident> data;
    transmissionData newData;
	QAction* closeAction;
	QAction* refreshAction;
};

#endif // INCLUDED_WIDGET_DEVICE_INFO_H
