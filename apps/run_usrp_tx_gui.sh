#!/bin/sh

./run_app.sh gui/ofdm_tx_gui.py &

./run_app.sh ../python/tx.py -f 2.45G --rms-amplitude=0.3 --bandwidth=1M --fft-length=256 --subcarriers=200 -a "type=usrp1" --tx-gain=20 --spec=A:0 $1 $2

