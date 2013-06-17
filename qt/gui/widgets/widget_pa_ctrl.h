/*
 * widget_pa_ctrl.h
 *
 *  Created on: 12.02.2009
 *      Author: harries
 */

#ifndef WIDGET_PA_CTRL_H_
#define WIDGET_PA_CTRL_H_


#include <QtGui/QWidget>
#include <vector>
#include "../interface/broker.h"
#include "WidgetControl.h"
#include "ui_pa_ctrl.h"
#include <qwt_plot.h>
#include <qwt_plot_curve.h>
#include <QMenu>
#include <QMouseEvent>
#include "../interface/types.h"


class widget_pa_ctrl : public QWidget, public WidgetControl
{
	Q_OBJECT

public:
	widget_pa_ctrl(QWidget *parent = 0);
	virtual ~widget_pa_ctrl();

	void setData(boost::shared_ptr<IF_ident> dataSource);
	void refresh(){};

public slots:
	void send();
	void setgain(int a);

protected:
	 virtual void timerEvent(QTimerEvent *);

private:
	powercontrol Data;
	boost::shared_ptr<IF_ident> source;
    Ui::pa_ctrl ui;
    boost::shared_ptr<IF_power_control> ptr;
    QwtPlot* dataRate;
    QwtPlotCurve* dataRateCurve;
    double x[256],y[256];
};
#endif /* WIDGET_PA_CTRL_H_ */
