#include "widget_lineplot.h"
#include "qwt_plot_curve.h"
#include <qwt_plot_canvas.h>
#include <qwt_scale_draw.h>
#include <qwt_scale_map.h>
#include <qwt_scale_widget.h>

lineplot::lineplot(QWidget *parent)
    : QwtPlot(parent), WidgetControl()
{
    closeAction = new QAction(tr("Close"), this);
    connect(closeAction, SIGNAL(triggered()), this, SLOT(close()));

    initCurve();

    scale = new QwtScaleDraw();
    map = new QwtScaleMap();

    map->setPaintXInterval(0,256);
    map->setScaleInterval(-1,1);
    scale->setTransformation(map->transformation()->copy());

    this->setAxisScaleDraw(QwtPlot::xBottom, scale );

    this->canvasMap(QwtPlot::xBottom).setPaintInterval(0,256);
    this->canvasMap(QwtPlot::xBottom).setScaleInterval(-1,1);


    this->axisWidget(QwtPlot::xBottom)->setEnabled(true);
    this->axisWidget(QwtPlot::xBottom)->setScaleDraw(scale);

    this->axisScaleDraw(QwtPlot::xBottom)->scaleMap().setPaintInterval(0,256);
    this->axisScaleDraw(QwtPlot::xBottom)->scaleMap().setScaleInterval(-1,1);
    this->axisWidget(QwtPlot::xBottom)->update();

	startTimer(50);
}

lineplot::~lineplot()
{

}


void lineplot::initCurve()
{
	resize(600,300);
	this->setMinimumSize(600,200);

    QwtPlotCurve *Lines = new QwtPlotCurve("lines");
    Lines->attach(this);
    Lines->setStyle(QwtPlotCurve::Lines);

    // Color settings
    QPalette palette;
    palette.setColor(QPalette::Background,Qt::white);
    canvas()->setPalette(palette);

    for (int i = 0; i < 256; i++)
    {
    	x[i]=float(i-128)/128;
    	y[i]=0;
    }

    Lines->setRawData(x,y,256);

    setAxisScale(QwtPlot::yLeft, -20, 60);
    setAxisScale(QwtPlot::xBottom, -1, 1);

    setAxisTitle(0, "dB");

    QPen gridpen = QPen(Qt::lightGray,1);
    gridpen.setStyle(Qt::DotLine);

    grid.attach(this);
    grid.setVisible(true);
    grid.setPen(gridpen);
}

void lineplot::setData(boost::shared_ptr<IF_ident> dataSource)
{
	source = dataSource;
	if (dataSource->getId().getIfType()==IF_Type(rx_bband))
		this->setTitle("Received baseband signal");
}

void lineplot::refresh()
{
	if (!source)
		{
		this->setTitle(QString("no Source"));
		return;
		}
	if (boost::dynamic_pointer_cast<IF_vector_float>(source))
	{
		boost::shared_ptr<IF_vector_float> derived = boost::dynamic_pointer_cast<IF_vector_float>(source);
		std::vector<float> Data;
		derived->getData(Data);
		int size = Data.size();
		for (int i = 0; i < size; i++)
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
		int size = Data.size();
		for (int i = 0; i < size; i++)
		{
			y[i]=Data[i];
		}
		replot();
	}
	else return;
}

void lineplot::mouseReleaseEvent(QMouseEvent*e)
{
	if (e->button() != Qt::RightButton) return;
    QMenu menu(this);
    menu.addAction(closeAction);
    menu.exec(e->globalPos());
}

void lineplot::timerEvent(QTimerEvent *timer)
{
	refresh();
}
