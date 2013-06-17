/*
 * rx_performance.h
 *
 *  Created on: 06.02.2009
 *      Author: harries
 */

#ifndef RX_PERFORMANCE_H_
#define RX_PERFORMANCE_H_

#include <QtGui/QWidget>
#include <qwt_plot.h>
#include <qwt_plot_curve.h>
#include <qwt_data.h>
#include <vector>
#include "../interface/broker.h"
#include "WidgetControl.h"
#include "ui_rx_performance.h"
#include <QMenu>
#include <QMouseEvent>
#include <qwt_scale_engine.h>

class Performance : public QWidget, public WidgetControl
{
	Q_OBJECT

public:
	Performance();
	virtual ~Performance();

	void setData(boost::shared_ptr<IF_ident> dataSource);
	void refresh();

public slots:
    void measure_avg();

protected:
	virtual void timerEvent(QTimerEvent *timer);
private:
	rx_performance_struct Data;
	boost::shared_ptr<IF_ident> source;
	std::list<float> snr_value_list;
	QwtPlotCurve* snr_curve;
	QwtPlotCurve* ber_curve;
	QwtPlot* snrPlot;
	QwtPlot* berPlot;
	double x[256],y[256],ber[256];
	double compareValue;
	bool syncLoss;
    Ui::Form ui;
};

#endif /* RX_PERFORMANCE_H_ */
