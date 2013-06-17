#include "widget_device_info.h"

device_info::device_info(QWidget *parent)
    : QWidget(parent), WidgetControl()
{
    closeAction = new QAction(tr("Close"), this);
    refreshAction = new QAction(tr("Refresh"), this);
    connect(closeAction, SIGNAL(triggered()), this, SLOT(close()));
    connect(refreshAction, SIGNAL(triggered()), this, SLOT(refresh()));

	ui.setupUi(this);

}

device_info::~device_info()
{

}

void device_info::refresh()
{
	boost::dynamic_pointer_cast<IF_transmission_data>(data)->getData(newData);

	ui.label_subcarriers_value->setText(QString::number(newData.subcarriers));

	ui.label_bandwidth_value->setText(QString::number((newData.bandwidth),'f',2) + QString(" Hz"));
	if ((newData.bandwidth / 1000) >= 1)
		ui.label_bandwidth_value->setText(QString::number((newData.bandwidth / 1000),'f',2) + QString(" kHz"));
	if ((newData.bandwidth / 1000000) >= 1)
		ui.label_bandwidth_value->setText(QString::number((newData.bandwidth / 1000000),'f',2) + QString(" MHz"));
	if ((newData.bandwidth / 1000000000) >= 1)
		ui.label_bandwidth_value->setText(QString::number((newData.bandwidth / 1000000000),'f',2) + QString(" GHz"));

	ui.label_burst_length_value->setText(QString::number(newData.burst_length));

	ui.label_carrier_freq_value->setText(QString::number(newData.carrier_freq,'f',3) + QString(" Hz"));
	if ((newData.carrier_freq / 1000) >= 1)
		ui.label_carrier_freq_value->setText(QString::number((newData.carrier_freq / 1000),'f',3) + QString(" kHz"));
	if ((newData.carrier_freq / 1000000) >= 1)
		ui.label_carrier_freq_value->setText(QString::number((newData.carrier_freq / 1000000),'f',3) + QString(" MHz"));
	if ((newData.carrier_freq / 1000000000) >= 1)
		ui.label_carrier_freq_value->setText(QString::number((newData.carrier_freq / 1000000000),'f',3) + QString(" GHz"));

	ui.label_cp_value->setText(QString::number(newData.cp_length));

	ui.label_fft_value->setText(QString::number(newData.fft_window));

	ui.label_max_datarate_value->setText(QString::number(newData.max_datarate) + QString(" bps"));
	if ((newData.max_datarate / 1000) >=1)
		ui.label_max_datarate_value->setText(QString::number(newData.max_datarate / 1000) + QString(" kbps"));
	if ((newData.max_datarate / 1000000) >=1)
			ui.label_max_datarate_value->setText(QString::number(newData.max_datarate / 1000000.) + QString(" Mbps"));

	ui.label_subc_bandwith_value->setText(QString::number(newData.subbandwidth,'f',2) + QString(" Hz"));
	if ((newData.subbandwidth / 1000) > 1)
		ui.label_subc_bandwith_value->setText(QString::number((newData.subbandwidth / 1000),'f',2) + QString(" kHz"));
	if ((newData.subbandwidth / 1000000) > 1)
		ui.label_subc_bandwith_value->setText(QString::number((newData.subbandwidth / 1000000),'f',2) + QString(" MHz"));

	ui.label_symbol_time_value->setText(QString::number(newData.symbol_time * 1000000) + QString(" us"));
}

void device_info::setData(boost::shared_ptr<IF_ident> dataSource)
{
	data = dataSource;
	refresh();
}

void device_info::mouseReleaseEvent(QMouseEvent*e)
{
	if (e->button() != Qt::RightButton) return;
    QMenu menu(this);
    menu.addAction(closeAction);
    menu.addAction(refreshAction);
    menu.exec(e->globalPos());
}
/*
void device_info::timerEvent(QTimerEvent *e)
{
	refresh();
}*/
