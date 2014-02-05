#!/bin/sh

./run_app.sh gui/ofdm_tx_gui.py &
./run_app.sh gui/ofdm_rx_gui.py &
./run_app.sh ../python/benchmark_ofdm.py -c cfg/benchmark_standard.conf --multipath --scatterplot --ber-window=50000 --disable-ctf-enhancer --freqoff=0 --fft-length=256 --subcarriers=200 $1 $2 $3

