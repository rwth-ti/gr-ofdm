#!/bin/sh

./run_app.sh gui/ofdm_tx_gui.py &

./run_app.sh ../python/tx.py -f 2.45G --bandwidth=1M --fft-length=256 --subcarriers=200 $1 $2

