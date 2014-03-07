gr-ofdm GNU Radio module
=============================
Provides blocks and Python classes to build an OFDM transmitter and receiver
for research and teaching purposes with dynamically configurable transmission
parameters. Includes QT based GUI for visualization.


Build requirements
------------------
In order to build the gr-ofdm module you will need to install the following prerequisites
- GNU Radio (http://gnuradio.org/)
- ZeroMQ including the C++ and Python bindings (http://zeromq.org/)
- gr-zmqblocks (https://github.com/iohannez/gr-zmqblocks)
- ITPP (http://itpp.sourceforge.net/)


How to build
------------
In the gr-ofdm folder do

    mkdir build
    cd build
    cmake ../
    make

optional

    make install


How to run the apps
-------------------

Assuming that the module has been compiled but not installed, in the
gr-ofdm folder do

    cd apps
    ./run_benchmark_gui.sh

to run the simulation or

    ./run_usrp_tx_gui.sh

And

    ./run_usrp_rx_gui.sh

To run the rf transmission


Copyright information
------------------
Copyright © 2014 Institute for Theoretical Information Technology,
                 RWTH Aachen University <https://www.ti.rwth-aachen.de/>

Unless otherwise stated, all files are distributed under GPL v3 license.
