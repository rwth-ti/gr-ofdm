#include <qwt_painter.h>
#include <qwt_plot_canvas.h>
#include <qwt_plot_marker.h>
#include <qwt_plot_curve.h>
#include <qwt_scale_widget.h>
#include <qwt_legend.h>
#include <qwt_scale_draw.h>
#include <qwt_math.h>
#include "widget_complexplot.h"


//
//  Initialize main window
//
ComplexPlot::ComplexPlot(QWidget *parent): QwtPlot(parent), WidgetControl(), d_interval(0), d_timerId(-1)
{
    closeAction = new QAction(tr("Close"), this);
    connect(closeAction, SIGNAL(triggered()), this, SLOT(close()));
    init();
    startTimer(100);
}

ComplexPlot::ComplexPlot(boost::shared_ptr<IF_ident> dataSource, QWidget* parent): 	QwtPlot(parent),
																					WidgetControl(),
																					d_interval(0),
																					d_timerId(-1),
																					source(dataSource)
{
    closeAction = new QAction(tr("Close"), this);
    connect(closeAction, SIGNAL(triggered()), this, SLOT(close()));
    init();
    startTimer(100);
}

void ComplexPlot::init()
{
    // Disable polygon clipping
    QwtPainter::setDeviceClipping(false);
    resize(300,300);
    this->setMinimumSize(300,300);
    this->setFixedSize(300,300);

    canvas()->setPaintAttribute(QwtPlotCanvas::PaintCached, false);
    canvas()->setPaintAttribute(QwtPlotCanvas::PaintPacked, false);

    // Color settings
    QPalette palette;
    palette.setColor(QPalette::Background,Qt::white);
    canvas()->setPalette(palette);

    alignScales();

    //  Initialize data
    for (int i = 0; i< 10000; i++)
    {
        d_x[i] = 0;     // time axis
        d_y[i] = 0;
    }

    QwtPlotCurve *values = new QwtPlotCurve("data");
    values->attach(this);
    values->setAxis(1,2);

    // Set curve styles
    values->setPen(QPen(Qt::blue, 2));
    values->setStyle(QwtPlotCurve::Dots);

    values->setRawData(d_x, d_y, 10000);

    QwtPlotMarker *mY = new QwtPlotMarker();
    mY->setLabelAlignment(Qt::AlignRight|Qt::AlignTop);
    mY->setLineStyle(QwtPlotMarker::HLine);
    mY->setYValue(0.0);
    mY->attach(this);

    QwtPlotMarker *mX = new QwtPlotMarker();
    mX->setLabelAlignment(Qt::AlignRight|Qt::AlignTop);
    mX->setLineStyle(QwtPlotMarker::VLine);
    mX->setXValue(0.0);
    mX->attach(this);

    // Axis
    setAxisScale(QwtPlot::xBottom, -1.5, 1.5);
    setAxisScale(QwtPlot::yLeft, -1.5, 1.5);

    QPen gridpen = QPen(Qt::lightGray,1);
    gridpen.setStyle(Qt::DotLine);

    grid.attach(this);
    grid.setVisible(true);
    grid.setPen(gridpen);
}


//
//  Set a plain canvas frame and align the scales to it
//
void ComplexPlot::alignScales()
{
    // The code below shows how to align the scales to
    // the canvas frame, but is also a good example demonstrating
    // why the spreaded API needs polishing.

    canvas()->setFrameStyle(QFrame::Box | QFrame::Plain );
    canvas()->setLineWidth(0);

    for ( int i = 0; i < QwtPlot::axisCnt; i++ )
    {
        QwtScaleWidget *scaleWidget = (QwtScaleWidget *)axisWidget(i);
        if ( scaleWidget )
            scaleWidget->setMargin(0);

        QwtScaleDraw *scaleDraw = (QwtScaleDraw *)axisScaleDraw(i);
        if ( scaleDraw )
            scaleDraw->enableComponent(QwtAbstractScaleDraw::Backbone, false);
    }
}


//  Generate new values
void ComplexPlot::timerEvent(QTimerEvent *)
{
	refresh();
}

void ComplexPlot::setData(std::vector<complexFloat> newData)
{
	if (newData.size() != 0)
	{
		for (int i = 0; newData[i] != *newData.end(); i++)
		{
			d_x[i] = newData[i].real();
			d_y[i] = newData[i].imag();
		}
	}
	replot();
}


void ComplexPlot::setData(boost::shared_ptr<IF_ident> dataSource)
{
	source = dataSource;
	ptr = boost::dynamic_pointer_cast<IF_vector_complex>(source);
}

void ComplexPlot::refresh()
{
	if (!source)
		{
		this->setTitle(QString("No Source"));
		return;
		}
	if (!ptr) return;
	if(!ptr->getData(Data)) return;
	int size = Data.size();
	for (int i = 0; i < size; i++)
	{
		d_x[i] = Data[i].real();
		d_y[i] = Data[i].imag();
	}
	replot();
}

void ComplexPlot::mouseReleaseEvent(QMouseEvent*e)
{
	if (e->button() != Qt::RightButton) return;
    QMenu menu(this);
    menu.addAction(closeAction);
    menu.exec(e->globalPos());
}
