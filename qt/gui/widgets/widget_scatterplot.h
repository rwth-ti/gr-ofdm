#ifndef WIDGET_SCATTERPLOT_H
#define WIDGET_SCATTERPLOT_H

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
#include <QHBoxLayout>

#define SCATTER_DOTS 768

class scatterplot : public QWidget, public WidgetControl
{
    Q_OBJECT

public:
    scatterplot(QWidget *parent = 0);
    ~scatterplot();

    void setData(IF_vector_complex dataSource);
    void setData(boost::shared_ptr<IF_ident> dataSource);
    int heightForWidth(int w) const;

    void refresh();

protected:
    virtual void timerEvent(QTimerEvent *timer);

private:
    std::vector<ofdm_ti::scatter_complex> Data;
    boost::shared_ptr<IF_ident> source;
    double x[SCATTER_DOTS];
    double y[SCATTER_DOTS];
    int buffer_idx;
    QHBoxLayout* Layout;
    QSpacerItem *Spacer;
    QwtPlot* Plot;
    QwtPlotCurve* Dots;
    QwtPlotGrid grid;

    QAction* closeAction;
};

#endif
