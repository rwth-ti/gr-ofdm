title: gr-ofdm
brief: A complete OFDM implementation including GUI for reasearch and teaching
tags:
 - ofdm
author:
 - see AUTHORS
copyright_owner:
 - Institute for Theoretical Information Technology, RWTH Aachen University
dependencies:
- ZeroMQ including the C++ and Python bindings (http://zeromq.org/)
- UHD Driver for USRP hardware
- GNU Radio (http://gnuradio.org/) (>= 3.7.2)
- ITPP (http://itpp.sourceforge.net/)
- python-qwt5-qt4
- python-scipy
repo: https://github.com/rwth-ti/gr-ofdm
license: Unless otherwise stated, all files are distributed under GPL v3 license
website: https://www.ti.rwth-aachen.de/
stable_release: HEAD
icon: https://github.com/rwth-ti/gr-ofdm/blob/master/screenshot_rx_gui.png
---

Provides blocks and Python classes to build an OFDM transmitter and receiver
for research and teaching purposes with dynamically configurable transmission
parameters. Includes Python Qt based GUI for visualization.

![alt text](https://github.com/rwth-ti/gr-ofdm/blob/master/screenshot_rx_gui.png "Screenshot of the receiver GUI")

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

Literature
----------
**Skript for the undergraduate lab**

https://www.ti.rwth-aachen.de/teaching/laboratory/ofdm/data/SkriptWS1516.pdf

**Papers**

Zivkovic, Milan, Johannes Schmitz, and Rudolf Mathar
[**SDR in teaching: An OFDM communication primer**](https://www.ti.rwth-aachen.de/publications/abstract.php?q=db&table=proceeding&id=956)
8th Karlsruhe Workshop on Software Radios, Karlsruhe, Germany, March 2014.

Johannes Schmitz and Milan Zivkovic and Rudolf Mathar
[**Extended Cyclostationary Signatures for OFDM-Based Cognitive Radio**](https://www.ti.rwth-aachen.de/publications/abstract.php?q=db&table=proceeding&id=868)
7th Karlsruhe Workshop on Software Radios, Karlsruhe, Germany, March 2012

M. Zivkovic, R. Mathar
[**Preamble-based SNR Estimation in Frequency Selective Channels for Wireless OFDM Systems**](https://www.ti.rwth-aachen.de/publications/abstract.php?q=db&table=proceeding&id=668)
IEEE VTC Spring 2009, Barcelona, Spain, April 2009.

