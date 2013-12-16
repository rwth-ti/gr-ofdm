#!/bin/sh

./run_app.sh gui/ofdm_tx_gui.py &
./run_app.sh gui/ofdm_rx_gui.py &
./run_app.sh ../python/benchmark_ofdm.py -c cfg/benchmark_standard.conf --debug --scatterplot --ber-window=50000 --disable-ctf-enhancer --freqoff=0 #--itu-channel --multipath

