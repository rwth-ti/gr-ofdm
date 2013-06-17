/*
 * widget_rx_performance.cpp
 *
 *  Created on: 06.02.2009
 *      Author: harries
 */

#include "widget_rx_performance.h"

Performance::Performance()
{
	ui.setupUi(this);
	connect(ui.pushButton_measure_avg, SIGNAL(clicked()), this, SLOT(measure_avg()));
	startTimer(100);
	syncLoss = false;

	snrPlot = new QwtPlot();
    berPlot = new QwtPlot();
	this->layout()->addWidget(snrPlot);
	this->layout()->addWidget(berPlot);
	QwtLog10ScaleEngine* myScale = new QwtLog10ScaleEngine();
	berPlot->setAxisScale(0,1e-5,0.5e-0);
	berPlot->setAxisScaleEngine(0,myScale);

	snrPlot->show();
    berPlot->show();
	snrPlot->setSizePolicy(QSizePolicy::Expanding, QSizePolicy::Expanding);
    berPlot->setSizePolicy(QSizePolicy::Expanding, QSizePolicy::Expanding);

	snr_curve = new QwtPlotCurve("snr");
	snr_curve->attach(snrPlot);
	snr_curve->setBaseline(0);
	snr_curve->setBrush(QBrush(Qt::red));

	ber_curve = new QwtPlotCurve("ber");
	ber_curve->attach(berPlot);
	ber_curve->setBaseline(0);
	ber_curve->setBrush(Qt::blue);

	//snrPlot->enableAxis(0,FALSE);

	snrPlot->setAxisTitle(0,"SNR [dB]");
	snrPlot->enableAxis(2,FALSE);
	snrPlot->setAxisScale(0,0,40,10);
	snrPlot->setAxisTitle(2,"time");

	berPlot->setAxisTitle(0,"BER");
	berPlot->enableAxis(2,FALSE);
	berPlot->setAxisTitle(2,"time");

	for (int i=0; i<255; i++) {x[i]=i; y[i]=0; ber[i]=0;}

	snr_curve->setRawData(x,y,128);
	snr_curve->setStyle(QwtPlotCurve::Lines);

	ber_curve->setRawData(x,ber,128);
    ber_curve->setStyle(QwtPlotCurve::Lines);

    for (int i = 0; i < 256; i++)
    {
        y[i]=0;
        ber[i]=0;
    }
}

Performance::~Performance() {
	// TODO Auto-generated destructor stub
}

void Performance::refresh()
{
	if(!boost::dynamic_pointer_cast<IF_rx_performance>(source)->getData(Data)) return;
	ui.label_ber_value->setText(QString::number(Data.ber,'e',2));
	ui.label_snr_value->setText(QString::number(Data.snr,'f',3));
	ui.label_freqoff_value->setText(QString::number(Data.freqoff,'f',3));

	for (int i = 0; i < 127; i++)
	{
		y[i]=y[i+1];
		ber[i]=ber[i+1];
	}
	if (Data.snr > 0)
	{
		y[127] = Data.snr;
		ber[127]= Data.ber;
		//std::cout << "snr: " << Data.snr << "\t ber: " << ber[127] << std::endl;
	}
	else
	{
		y[127] = 0;
		ber[127] = 0;
	}

	if ((y[127] == y[125]) && (y[126] == y[125]))
		{
		syncLoss = true;
		compareValue = y[125];
		}

	if ((syncLoss) && (y[127] == compareValue)) y[127] = 0;
	else syncLoss = false;

	snrPlot->replot();
    berPlot->replot();
}

void Performance::measure_avg()
{
    float avg_ber = 0;
    float avg_snr = 0;

    for (int i = 0; i < 127; i++)
    {
        y[i]=y[i+1];
        ber[i]=ber[i+1];
        avg_snr += y[i];
        avg_ber += ber[i];
    }
    avg_snr = avg_snr/127;
    avg_ber = avg_ber/127;
    ui.label_avg_ber_value->setText(QString::number(avg_ber,'e',2));
    ui.label_avg_snr_value->setText(QString::number(avg_snr,'f',3));
}

void Performance::setData(boost::shared_ptr<IF_ident> dataSource)
{
	source = dataSource;
}

void Performance::timerEvent(QTimerEvent *timer)
{
	refresh();
}
