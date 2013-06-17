#ifndef WIDGET_BARPLOT_H
#define WIDGET_BARPLOT_H

#include <QtGui/QWidget>
#include <qwt_plot.h>
#include <qwt_plot_grid.h>
#include <qwt_plot_curve.h>
#include <vector>
#include "../interface/broker.h"
#include "WidgetControl.h"
#include <QMenu>
#include <QMouseEvent>
#include <qwt_data.h>

#define MAX_VAL 1024

class barplot : public QwtPlot, public WidgetControl
{
    Q_OBJECT

public:
    barplot(QWidget *parent = 0);
    ~barplot();

    void setData(std::vector<float> data);
    void setData(IF_vector_float dataSource);
    void setData(IF_vector_int dataSource);
    void setData(boost::shared_ptr<IF_ident> dataSource);

    void refresh();

protected:
	virtual void mouseReleaseEvent ( QMouseEvent *e);
    virtual void timerEvent(QTimerEvent *timer);

private:
	std::vector<float> Data;
	double x[MAX_VAL];
	double y[MAX_VAL];
	QwtPlotCurve* Steps;
	int no_of_values;
	QwtPlotGrid grid;

	boost::shared_ptr<IF_ident> source;
	QAction* closeAction;
};

#endif // WIDGET_BARPLOT_H
