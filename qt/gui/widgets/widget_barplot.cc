#include "widget_barplot.h"
#include <qwt_plot_curve.h>
#include <qwt_plot_canvas.h>
#include <QBrush>

barplot::barplot(QWidget *parent)
    : QwtPlot(parent), WidgetControl()
{
    closeAction = new QAction(tr("Close"), this);
    connect(closeAction, SIGNAL(triggered()), this, SLOT(close()));

    Steps = new QwtPlotCurve("steps");
    Steps->attach(this);

    for (int i = 0; i < MAX_VAL; i++)
    {
    	x[i]=i;y[i]=0;
    }
    no_of_values = MAX_VAL;

    QPen gridpen = QPen(Qt::lightGray,1);
    gridpen.setStyle(Qt::DotLine);

    grid.attach(this);
    grid.setVisible(true);
    grid.setPen(gridpen);

	this->setMinimumSize(600,200);
}

barplot::~barplot()
{

}


void barplot::setData(IF_vector_float dataSource)
{
	std::vector<float> Data;
	dataSource.getData(Data);
	int size = Data.size();
	for (int i = 0; i < size; i++)
	{
		x[i]=i;
		y[i]=Data[i];
	}
}

void barplot::setData(IF_vector_int dataSource)
{
	std::vector<int> Data;
	dataSource.getData(Data);
	int size = Data.size();
	for (int i = 0; i < size; i++)
	{
		x[i]=i;
		y[i]=Data[i];
	}
}

void barplot::setData(std::vector<float> data)
{
	QwtPlotCurve* test = new QwtPlotCurve("steps");
	test->attach(this);
	test->setStyle(QwtPlotCurve::Steps);
	setAxisScale(QwtPlot::yLeft, -5, 5);
	(data.size()<=1024) 	? (test->setRawData(x,y,data.size()))
							: (test->setRawData(x,y,1024));
	test->setBaseline(0);
	test->setBrush(QBrush(Qt::darkGreen));
	int size = data.size();
	for (int i = 0; i < size; i++)
	{
		y[i]=data[i];
	}
	replot();
}

void barplot::refresh()
{
	if (!source) return;

	if (boost::dynamic_pointer_cast<IF_vector_float>(source))
	{
		boost::shared_ptr<IF_vector_float> derived = boost::dynamic_pointer_cast<IF_vector_float>(source);

		if (!derived->getData(Data)) return;

		if ((Data.size() != no_of_values) && (Data.size() <= MAX_VAL))
		{
						no_of_values = Data.size();
						this->Steps->setRawData(x,y,no_of_values);
						setAxisScale(QwtPlot::xBottom, 0, no_of_values);
		}

		for (int i = 0; i < no_of_values; i++)
		{
			y[i]=Data[i];
		}
		replot();
	}
	else if (boost::dynamic_pointer_cast<IF_vector_int>(source))
	{
		boost::shared_ptr<IF_vector_int> derived = boost::dynamic_pointer_cast<IF_vector_int>(source);
		std::vector<int> Data;
		derived->getData(Data);
		for (int i = 0; i < 200; i++)
		{
			y[i]=Data[i];
		}
		replot();
	}
	else return;
}

void barplot::setData(boost::shared_ptr<IF_ident> dataSource)
{
	source = dataSource;

	Steps->setStyle(QwtPlotCurve::Steps);
	Steps->setBaseline(0);
	setAxisTitle(2, "subchannel index");

	switch (dataSource->getId().getIfType())
	{
	case IF_Type(power_aloc_scheme):
		setTitle("Power Allocation");
		Steps->setPen(QPen(Qt::darkGreen));
		Steps->setBrush(QBrush(Qt::darkGreen));
    	setAxisScale(QwtPlot::yLeft, 0, 3);
    	startTimer(500);
    	break;
	case IF_Type(rate_aloc_scheme):
		setTitle("Rate Allocation");
		Steps->setPen(QPen(Qt::blue));
		Steps->setBrush(QBrush(Qt::blue));
    	setAxisScale(QwtPlot::yLeft, 0, 8);
    	startTimer(500);
    	break;
	case IF_Type(CTF):
		setTitle("Normalized Channel State Information");
		setAxisTitle(0, "");
		Steps->setPen(QPen(Qt::blue));
		Steps->setBrush(QBrush(Qt::blue));
    	setAxisScale(QwtPlot::yLeft, 0, 3);
    	startTimer(50);
    	break;
	case IF_Type(SINRPSC):
		setTitle("SINR per subchannel");
		setAxisTitle(0, "dB");
		Steps->setPen(QPen(Qt::blue));
		Steps->setBrush(QBrush(Qt::blue));
		setAxisScale(QwtPlot::yLeft, -10, 40);
		startTimer(50);
		break;
	default:
		break;
    }

	resize(600,300);

    // Color settings
    QPalette palette;

    palette.setColor(QPalette::Background,Qt::white);
    canvas()->setPalette(palette);

    Steps->setRawData(x,y,MAX_VAL);
}

void barplot::mouseReleaseEvent(QMouseEvent*e)
{
	if (e->button() != Qt::RightButton) return;
    QMenu menu(this);
    menu.addAction(closeAction);
    menu.exec(e->globalPos());
}

void barplot::timerEvent(QTimerEvent *timer)
{
	this->refresh();
}
