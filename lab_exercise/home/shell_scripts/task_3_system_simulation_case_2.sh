#!/bin/bash

killall python

cd /opt/gr-ofdm/apps/
./run_app.sh gui/ofdm_tx_gui.py &
./run_app.sh gui/ofdm_rx_gui.py &
./run_app.sh ../python/benchmark_ofdm.py -c cfg/benchmark_standard.conf --scatterplot --ber-window=50000 --disable-ctf-enhancer --freqoff=0 --fft-length=256 --subcarriers=200 --multipath --lab-special-case

