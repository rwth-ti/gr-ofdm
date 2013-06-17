/*
 * widget_tx_ctrl.cpp
 *
 *  Created on: 12.02.2009
 *      Author: harries
 */

#include "widget_tx_ctrl.h"
#include <math.h>

widget_tx_ctrl::widget_tx_ctrl (QWidget *parent) : QWidget(parent), WidgetControl()
{
    ui.setupUi(this);
    connect(ui.pushButton_update, SIGNAL(clicked()), this, SLOT(set_modulation()));
    connect(ui.horizontalSlider_txampl, SIGNAL(valueChanged(int)),this,SLOT(set_slider_txampl(int)));
    connect(ui.lineEdit_txampl, SIGNAL(returnPressed()),this,SLOT(set_lineEdit_txampl()));
    connect(ui.horizontalSlider_freqoff, SIGNAL(valueChanged(int)),this,SLOT(set_slider_freqoff()));
    connect(ui.lineEdit_freqoff, SIGNAL(returnPressed()),this,SLOT(set_lineEdit_freqoff()));
    startTimer(500);

    dataRate = new QwtPlot();
    dataRate->setMinimumSize(200,100);
    dataRateCurve = new QwtPlotCurve();
    this->ui.horizontalLayout_3->addWidget(dataRate);

    dataRate->enableAxis(2,FALSE);
    dataRate->setAxisTitle(0,"Datarate [Mbps]");
    dataRate->setAxisTitle(2,"time");

    dataRate->setAxisScale(0,0,10);

    for (int i = 0; i < 128; i++) {x[i]=i; y[i]=0;}

    dataRateCurve->setRawData(x,y,128);
    dataRateCurve->attach(dataRate);
    dataRateCurve->setBaseline(0);
    dataRateCurve->setBrush(QBrush(Qt::gray));

    Data.constraint = 4000;
    Data.modulation = 1;
    Data.freqoff = 0;
}

widget_tx_ctrl::~widget_tx_ctrl() {
    // TODO Auto-generated destructor stub
}

void widget_tx_ctrl::setData(boost::shared_ptr<IF_ident> dataSource)
{
    if_ptr = boost::dynamic_pointer_cast<IF_tx_control>(dataSource);
}

void widget_tx_ctrl::set_modulation()
{
    if (!if_ptr) return;

    std::string text_mod = ui.comboBox_modulation->currentText().toStdString();

    if (text_mod == "BPSK") Data.modulation = 1;
    if (text_mod == "QPSK") Data.modulation = 2;
    if (text_mod == "8-PSK") Data.modulation = 3;
    if (text_mod == "16-QAM") Data.modulation = 4;
    if (text_mod == "32-QAM") Data.modulation = 5;
    if (text_mod == "64-QAM") Data.modulation = 6;
    if (text_mod == "128-QAM") Data.modulation = 7;
    if (text_mod == "256-QAM") Data.modulation = 8;

    if_ptr->setData(Data);
}

void widget_tx_ctrl::set_slider_txampl(int ampl)
{
    if(!if_ptr) return;
    Data.constraint = ampl;
    if_ptr->setData(Data);
    ui.lineEdit_txampl->setText(QString::number(ampl));
}

void widget_tx_ctrl::set_lineEdit_txampl()
{
    int ampl = ui.lineEdit_txampl->text().toInt();
    if(!if_ptr) return;
    Data.constraint = ampl;
    if_ptr->setData(Data);
    ui.horizontalSlider_txampl->setValue(ampl);
}

void widget_tx_ctrl::set_slider_freqoff()
{
    int norm_freq = ui.horizontalSlider_freqoff->value();
    if(!if_ptr) return;
    float f_norm_freq = (float)norm_freq/10000;
    Data.freqoff = f_norm_freq;
    if_ptr->setData(Data);
    ui.lineEdit_freqoff->setText(QString::number(f_norm_freq));
}

void widget_tx_ctrl::set_lineEdit_freqoff()
{
    float f_norm_freq = ui.lineEdit_freqoff->text().toFloat();
    if(!if_ptr) return;
    Data.freqoff = f_norm_freq;
    if_ptr->setData(Data);
    ui.horizontalSlider_freqoff->setValue((int)(f_norm_freq*10000));
}

void widget_tx_ctrl::timerEvent(QTimerEvent *)
{
    if (!if_ptr->getData(Data))
    {
        ui.label_datarate_value->setText(QString("---"));
        ui.label_power_value->setText(QString("---"));
        return;
    }
    for (int i = 0; i < 127; i++)
    {
        y[i] = y[i+1];
    }
    y[127] = Data.data_rate * 1e-6;
    dataRate->replot();
    ui.label_datarate_value->setText(QString::number((Data.data_rate / 1000000),'i',2) + QString(" Mbps"));
    ui.label_power_value->setText(QString::number(Data.power_val,'i',1));
}
