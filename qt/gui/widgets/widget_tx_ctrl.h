/*
 * widget_tx_ctrl.h
 *
 *  Created on: 12.02.2009
 *      Author: harries
 */

#ifndef WIDGET_TX_CTRL_H_
#define WIDGET_TX_CTRL_H_


#include <QtGui/QWidget>
#include <vector>
#include "../interface/broker.h"
#include "WidgetControl.h"
#include "ui_tx_ctrl.h"
#include <qwt_plot.h>
#include <qwt_plot_curve.h>
#include <QMenu>
#include <QMouseEvent>
#include "../interface/types.h"


class widget_tx_ctrl : public QWidget, public WidgetControl
{
    Q_OBJECT

    public:
        widget_tx_ctrl(QWidget *parent = 0);
        virtual ~widget_tx_ctrl();

        void setData(boost::shared_ptr<IF_ident> dataSource);
        void refresh(){};

    public slots:
        void set_slider_txampl(int ampl);
        void set_lineEdit_txampl();
        void set_slider_freqoff();
        void set_lineEdit_freqoff();
        void set_modulation();

    protected:
        virtual void timerEvent(QTimerEvent *);

    private:
        powercontrol Data;
        Ui::tx_ctrl ui;
        boost::shared_ptr<IF_tx_control> if_ptr;
        QwtPlot* dataRate;
        QwtPlotCurve* dataRateCurve;
        double x[256],y[256];
};
#endif /* WIDGET_TX_CTRL_H_ */
