gr-ofdm GNU Radio module
=============================
Provides blocks and Python classes to build an OFDM transmitter and receiver
for research and teaching purposes with dynamically configurable transmission
parameters. Includes Python Qt based GUI for visualization.


Build requirements
------------------
In order to build the gr-ofdm module you will need to install the following prerequisites
- ZeroMQ including the C++ and Python bindings (http://zeromq.org/)
- UHD Driver for USRP hardware
- GNU Radio (http://gnuradio.org/)
- ITPP (http://itpp.sourceforge.net/)
- python-qwt5-qt4
- python-scipy


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

    ./run_app.sh ../python/tx.py -f2.45G

And

    ./run_app.sh ../python/rx.py -f2.45G --disable-ctf-enhancer --scatterplot


to run the rf transmission.
Then to oberserve everything in th graphical user interface:

    ./run_app.sh gui/ofdm_tx_gui.py

and

    ./run_app.sh gui/ofdm_rx_gui.py --tx-hostname=<hostname>

be careful with the frequency offset of you radio frontend. It might be
necessary to apply a small manual correction of a few kHz.

Additional features:

Coding

    ./run_benchmark_gui.sh  --coding  --data-blocks=10

Adaptive OFDM

    ./run_benchmark_gui.sh --sinr-est --multipath

with USRPs and adaptive OFDM enabled

    ./run_usrp_tx_gui.sh --rx-hostname=<hostname or ip> -f 2.45G --tx-gain=<gain>
    ./run_usrp_rx_gui.sh --tx-hostname=<hostname or ip> -f 2.45G --sinr-est


Copyright information
------------------
Copyright © 2015 Institute for Theoretical Information Technology,
                 RWTH Aachen University <https://www.ti.rwth-aachen.de/>

Unless otherwise stated, all files are distributed under GPL v3 license.
