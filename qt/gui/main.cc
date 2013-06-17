#include "gnuradio_qtgui.h"

#include <QtGui>
#include <QtCore>
#include <QApplication>
#include <vector>
#include "interface/types.h"
#include <boost/program_options.hpp>
#include "gui_tx.h"
#include "gui_rx.h"
#include "gui_rxsinr.h"

namespace po = boost::program_options;

int main(int argc, char *argv[])
{
    QApplication a(argc, argv);

    parameters pp;

    pp.id = -1;
    po::options_description desc("Allowed options");
    desc.add_options()
		("help", "Produce help message")
                ("nameservice", po::value<std::string>(&(pp.nameservice))->default_value("tabur"), "Specify the namingservice")
		("port", po::value<std::string>(&(pp.port))->default_value("50001"), "Specify the port")
		("station-id", po::value<int>(&(pp.id)), "Station ID")
		("rx", "Receiver view")
		("tx", "Transmitter view")
        ("rxsinr", "Receiver view with sinr per sc instead of ctf instead of");

    po::variables_map vm;
    po::store(po::parse_command_line(argc, argv, desc), vm);
    po::notify(vm);

    if (vm.count("help")) {
        std::cout << desc << "\n";
        return 1;
    }

    if (vm.count("tx"))
    {
    	gui_tx* tx = new gui_tx(pp.nameservice, pp.port);
    	tx->show();
    }
    else if(vm.count("sinr"))
    {
    	gui_rxsinr* rxsinr = new gui_rxsinr(pp.nameservice, pp.port, pp.id);
    	rxsinr->show();
    }
    else if(vm.count("rxsinr"))
        {
        	gui_rx* rx = new gui_rx(pp.nameservice, pp.port, pp.id);
        	rx->show();
        }
    else
    {
    	gnuradio_qtgui* w = new gnuradio_qtgui(pp.nameservice, pp.port);
    	w->show();
    }

    return a.exec();
}
