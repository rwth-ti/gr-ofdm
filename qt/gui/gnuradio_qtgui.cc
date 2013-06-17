#include "gnuradio_qtgui.h"
#include <qwt_plot_curve.h>
#include "./interface/broker.h"
#include "analyse.h"
#include "./interface/types.h"

gnuradio_qtgui::gnuradio_qtgui(std::string namingservice, std::string port, QWidget *parent) : 	QWidget(parent),
																								myBroker(new broker(namingservice,port)),
																								View(new viewWidget())
{
	ui.setupUi(this);
	connect(ui.pushButton_refresh, SIGNAL(clicked()), this, SLOT(updateInterfaceList()));
	connect(ui.pushButton_show,SIGNAL(clicked()), this, SLOT(showSelected()));

	myLayout = new Layout(View);
	updateInterfaceList();
}

gnuradio_qtgui::~gnuradio_qtgui()
{
}


void gnuradio_qtgui::addWidget(boost::shared_ptr<IF_ident> dataSource)
{
	std::cout << WidgetList.size() << std::endl;
	IF_Type type = dataSource->getId().getIfType();
	if (type == IF_Type(power_control))
	{
		boost::shared_ptr<widget_pa_ctrl> newPlot (new widget_pa_ctrl);
		newPlot->setData(dataSource);
		WidgetList.push_back(newPlot);
		myLayout->add((boost::dynamic_pointer_cast<QWidget>(newPlot)).get());
		newPlot->show();
	}
	if (type == IF_Type(tx_control))
	{
		boost::shared_ptr<widget_tx_ctrl> newPlot (new widget_tx_ctrl);
		newPlot->setData(dataSource);
		WidgetList.push_back(newPlot);
		myLayout->add((boost::dynamic_pointer_cast<QWidget>(newPlot)).get());
		newPlot->show();
	}
	if (type == IF_Type(rx_performance))
	{
		boost::shared_ptr<Performance> newPlot (new Performance);
		newPlot->setData(dataSource);
		WidgetList.push_back(newPlot);
		myLayout->add((boost::dynamic_pointer_cast<QWidget>(newPlot)).get());
		newPlot->show();
	}
	if (type == IF_Type(CTF))
	{
		boost::shared_ptr<barplot> newPlot (new barplot);
		newPlot->setData(dataSource);
		WidgetList.push_back(newPlot);
		myLayout->add((boost::dynamic_pointer_cast<QWidget>(newPlot)).get());
		newPlot->show();
	}
	if (type == IF_Type(SINRPSC))
		{
			boost::shared_ptr<barplot> newPlot (new barplot);
			newPlot->setData(dataSource);
			WidgetList.push_back(newPlot);
			myLayout->add((boost::dynamic_pointer_cast<QWidget>(newPlot)).get());
			newPlot->show();
		}
	if (dataSource->getId().getIfType() == IF_Type(rx_bband))
		{
			boost::shared_ptr<lineplot> newPlot (new lineplot);
			newPlot->setData(dataSource);
			WidgetList.push_back(newPlot);
			myLayout->add((boost::dynamic_pointer_cast<QWidget>(newPlot)).get());
			newPlot->show();
		}
	if (type == IF_Type(power_aloc_scheme))
	{
		boost::shared_ptr<barplot> newPlot (new barplot);
		newPlot->setData(dataSource);
		WidgetList.push_back(newPlot);
		myLayout->add((boost::dynamic_pointer_cast<QWidget>(newPlot)).get());
		newPlot->show();
	}
	if (type == IF_Type(rate_aloc_scheme))
	{
		boost::shared_ptr<barplot> newPlot (new barplot);
		newPlot->setData(dataSource);
		WidgetList.push_back(newPlot);
		myLayout->add((boost::dynamic_pointer_cast<QWidget>(newPlot)).get());
		newPlot->show();
	}
	if (type == IF_Type(scatter))
	{
		boost::shared_ptr<widget_scatter_ctrl> newPlot (new widget_scatter_ctrl);
		newPlot->setData(dataSource);
		WidgetList.push_back(newPlot);
		newPlot->show();
		myLayout->add((boost::dynamic_pointer_cast<QWidget>(newPlot)).get());
	}
	if (type == IF_Type(SNR))
	{
		boost::shared_ptr<lineplot> newPlot (new lineplot);
		newPlot->setData(dataSource);
		WidgetList.push_back(newPlot);
		newPlot->show();
		myLayout->add((boost::dynamic_pointer_cast<QWidget>(newPlot)).get());
	}
	if (type == IF_Type(TransmissionData))
	{
		boost::shared_ptr<device_info> newPlot (new device_info);
		newPlot->setData(dataSource);
		WidgetList.push_back(newPlot);
		newPlot->show();
		myLayout->add((boost::dynamic_pointer_cast<QWidget>(newPlot)).get());
	}
	if (!(myLayout->isEmpty())) View->show();
}

void gnuradio_qtgui::updateInterfaceList()
{

	ui.listWidget->clear();

	interfaces = myBroker->getIfList();
	std::list< boost::shared_ptr<IF_ident> >::iterator it;

	for (it = interfaces.begin(); it != interfaces.end(); it++)
	{
		QString title = analyse::analyseId((*it).get()->getId());

		ListElement* newElement = new ListElement(*it);
		newElement->setText(title);
		ui.listWidget->addItem(newElement);
	}
}

void gnuradio_qtgui::replotWidgets()
{
	if (WidgetList.size() == 0) return;
	std::list< boost::shared_ptr<QWidget> >::iterator it;
	for (it = WidgetList.begin(); it != WidgetList.end(); it++)
	{
		boost::shared_ptr<WidgetControl> pointer = boost::dynamic_pointer_cast<WidgetControl>(*it);
		pointer->refresh();
	}
}

void gnuradio_qtgui::timerEvent(QTimerEvent *)
{
	//replotWidgets();
}

void gnuradio_qtgui::damnit()
{
	std::list<IF_Type> txgui;
	txgui.push_back(IF_Type(TransmissionData));
	txgui.push_back(IF_Type(rate_aloc_scheme));
	txgui.push_back(IF_Type(power_aloc_scheme));

	updateInterfaceList();

	for( std::list<IF_Type>::iterator current = txgui.begin(); current != txgui.end(); ++current)
	{
	        std::list< boost::shared_ptr<IF_ident> >::iterator it;
        	for (it = interfaces.begin(); it != interfaces.end(); it++)
	        {
        	        if ((*it)->getId().getIfType() == *current)
                	        addWidget(*it);
	        }
	}
}

void gnuradio_qtgui::FISH()
{
        std::list<IF_Type> txgui;
        txgui.push_back(IF_Type(rx_bband));
        txgui.push_back(IF_Type(CTF));
        txgui.push_back(IF_Type(power_control));
	txgui.push_back(IF_Type(rx_performance));

        updateInterfaceList();


        for( std::list<IF_Type>::iterator current = txgui.begin(); current != txgui.end(); ++current )
        {
                std::list< boost::shared_ptr<IF_ident> >::iterator it;
                for (it = interfaces.begin(); it != interfaces.end(); it++)
                {
                        if ((*it)->getId().getIfType() == *current)
			{
	                                addWidget(*it);
			}
                }
        }
}

void gnuradio_qtgui::showSelected()
{
	if (!ui.listWidget->currentItem()) return;
	QString current = (ui.listWidget->currentItem())->text();

	std::list< boost::shared_ptr<IF_ident> >::iterator it;
	for (it = interfaces.begin(); it != interfaces.end(); it++)
	{
		if (analyse::analyseId((*it).get()->getId()) == current)
			addWidget(*it);
	}
}

void gnuradio_qtgui::closeEvent(QCloseEvent *)
{
	std::list<boost::shared_ptr<QWidget> >::iterator it;
	for (it = WidgetList.begin(); it != WidgetList.end(); it++)
		(*it->get()).close();
	View->close();
}


