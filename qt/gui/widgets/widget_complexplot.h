#ifndef _COMPLEXPLOT_H
#define _COMPLEXPLOT_H 1

#include <qwt_plot.h>
#include <qwt_plot_grid.h>
#include <vector>
#include "../interface/broker.h"
#include "boost/shared_ptr.hpp"
#include "WidgetControl.h"
#include <QMenu>
#include <QMouseEvent>

class ComplexPlot : public QwtPlot, public WidgetControl
{
    Q_OBJECT

public:
	ComplexPlot(QWidget* = NULL);
	ComplexPlot(boost::shared_ptr<IF_ident> dataSource, QWidget* = NULL);

	void setData(std::vector<complexFloat> newData);
    void setData(boost::shared_ptr<IF_ident> dataSource);
    void refresh();



protected:
    virtual void timerEvent(QTimerEvent *e);
	virtual void mouseReleaseEvent ( QMouseEvent *e);

private:
    void init();
    void alignScales();
    boost::shared_ptr<IF_ident> source;
	std::vector<complexFloat> Data;
	boost::shared_ptr<IF_vector_complex> ptr;

    double d_x[10000];
    double d_y[10000];

    int d_interval; // timer in ms
    int d_timerId;
	QAction* closeAction;
	QwtPlotGrid grid;
};

#endif
