#ifndef WIDGET_LINEPLOT_H
#define WIDGET_LINEPLOT_H

#include <QtGui/QWidget>
#include "qwt_plot.h"
#include "qwt_plot_grid.h"
#include "../interface/broker.h"
#include "WidgetControl.h"
#include <QMenu>
#include <QMouseEvent>

class lineplot : public QwtPlot, public WidgetControl
{
    Q_OBJECT

public:
	lineplot(QWidget *parent = 0);
    ~lineplot();

    void setData(boost::shared_ptr<IF_ident> dataSource);
    void refresh();

protected:
	virtual void mouseReleaseEvent ( QMouseEvent *e);
	virtual void timerEvent (QTimerEvent *timer);

private:
	void initCurve();

	double x[512];
	double y[512];
	QAction* closeAction;
	boost::shared_ptr<IF_ident> source;

	QwtScaleDraw* scale;
    QwtScaleMap* map;

	QwtPlotGrid grid;
};

#endif // WIDGET_LINEPLOT_H
