#!/bin/sh

cd $(dirname $0)

if [ -d "$PWD/../build" ]; then
    . $PWD/environment_debug
else
    . $PWD/environment_release
fi

ofdm_tx_gui.py &

tx.py -f 2.45G --bandwidth=1M --fft-length=256 --subcarriers=200 $1 $2 $3 $4 $5 $6 $7 $8 $9 $10

