#!/bin/sh

./run_app.sh gui/ofdm_tx_gui.py &

./usrp_tx -f 2.45G --rms-amplitude=0.3 --bandwidth=1M --fft-length=256 --subcarriers=200 -a "type=usrp2" --tx-gain=20 $1 $2
