#include "widget_scatterplot.h"
#include <QtGui/QWidget>
#include <qwt_plot.h>
#include <qwt_plot_curve.h>
#include <qwt_plot_canvas.h>
#include <qwt_symbol.h>


    scatterplot::scatterplot(QWidget *parent)
: QWidget(parent), WidgetControl()
{
    Layout = new QHBoxLayout();
    Plot = new QwtPlot();
    Dots = new QwtPlotCurve("Scatterplot");
    Dots->attach(Plot);
    Spacer = new QSpacerItem ( 0, 0, QSizePolicy::Minimum, QSizePolicy::Minimum );
    Layout->addWidget(Plot);
    Layout->insertStretch(1,100);
    this->setLayout(Layout);

    Dots->setStyle(QwtPlotCurve::Dots);
    QPen pen( Qt::black );
    QBrush brush( Qt::black );
    Dots->setSymbol( QwtSymbol( QwtSymbol::XCross, brush, pen, QSize(3,3) ) );

    Plot->setAxisScale(QwtPlot::xBottom, -1.5,1.5);
    Plot->setAxisScale(QwtPlot::yLeft,-1.5,1.5);
    Plot->setMinimumSize(250,250);

    // Color settings
    QPalette palette;
    palette.setColor(QPalette::Background,Qt::white);
    Plot->canvas()->setPalette(palette);

    QPen gridpen = QPen(Qt::lightGray,1);
    gridpen.setStyle(Qt::DotLine);
    grid.setVisible(true);
    grid.setPen(gridpen);

    grid.attach(Plot);
    for (int i = 0; i < SCATTER_DOTS; i++)
    {
        x[i]=i/SCATTER_DOTS;
        y[i]=i/SCATTER_DOTS;
    }
    Dots->setRawData(x,y,SCATTER_DOTS);

    buffer_idx = 0;

    startTimer(10);
}

scatterplot::~scatterplot()
{
    delete Dots;
    delete Plot;
    delete Layout;
}

int scatterplot::heightForWidth(int w) const
{
    return w;
}

void scatterplot::setData(boost::shared_ptr<IF_ident> dataSource)
{
    source = dataSource;
    if (dataSource->getId().getIfType()==IF_Type(scatter))
        Plot->setTitle("Scatterplot");
}


void scatterplot::refresh()
{
    if (!source)
    {
        Plot->setTitle(QString("no Source"));
        return;
    }
    if (boost::dynamic_pointer_cast<IF_vector_complex>(source)->getData(Data))
    {
        for(size_t i=0; i < Data.size(); i++) {
            if(buffer_idx >= SCATTER_DOTS)
                buffer_idx = 0;
            x[buffer_idx] = Data[i].i;
            y[buffer_idx] = Data[i].q;
            buffer_idx++;
        }
        Plot->replot();
    }
    return;
}

void scatterplot::timerEvent(QTimerEvent *timer)
{
    this->refresh();
}
