/*
 * widget_pa_ctrl.cpp
 *
 *  Created on: 12.02.2009
 *      Author: harries
 */

#include "widget_pa_ctrl.h"

widget_pa_ctrl::widget_pa_ctrl (QWidget *parent) : QWidget(parent), WidgetControl()
{
	ui.setupUi(this);
	connect(ui.pushButton_update, SIGNAL(clicked()), this, SLOT(send()));
	connect(ui.horizontalSlider_gain, SIGNAL(valueChanged(int)),this,SLOT(setgain(int)));

	ui.horizontalSlider_gain->setTickPosition(QSlider::TicksBelow);
	startTimer(500);
	dataRate = new QwtPlot();
	dataRate->setMinimumSize(200,100);
	dataRateCurve = new QwtPlotCurve();
	this->layout()->addWidget(dataRate);

	dataRate->enableAxis(2,FALSE);
	dataRate->setAxisTitle(0,"Datarate [Mbps]");

	dataRate->setAxisScale(0,0,8);

	for (int i = 0; i < 128; i++) {x[i]=i; y[i]=0;}

	dataRateCurve->setRawData(x,y,128);
	dataRateCurve->attach(dataRate);
	dataRateCurve->setBaseline(0);
	dataRateCurve->setBrush(QBrush(Qt::gray));

}

widget_pa_ctrl::~widget_pa_ctrl() {
	// TODO Auto-generated destructor stub
}

void widget_pa_ctrl::setData(boost::shared_ptr<IF_ident> dataSource)
{
	//source = dataSource;
	ptr = boost::dynamic_pointer_cast<IF_power_control>(dataSource);
}

void widget_pa_ctrl::send()
{
	if (!ptr) return;

	Data.constraint = ui.lineEdit_constraint_value->text().toFloat();
	Data.required_ber = ui.lineEdit_ber_value->text().toFloat();

	std::string text = ui.comboBox_mode_value->currentText().toStdString();
	if (text == "reset") Data.strategy = ofdm_ti::PA_Ctrl::reset;
	if (text == "rate adaptive") Data.strategy = ofdm_ti::PA_Ctrl::rate_adaptive;
	if (text == "margin adaptive") Data.strategy = ofdm_ti::PA_Ctrl::margin_adaptive;

	ptr->setData(Data);
}


void widget_pa_ctrl::setgain(int a)
{
	if(!ptr) return;
	ptr->setgain(a);
}

void widget_pa_ctrl::timerEvent(QTimerEvent *)
{
	if (!ptr->getData(Data))
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

