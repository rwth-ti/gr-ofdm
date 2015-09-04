#!/bin/sh

cd $(dirname $0)

if [ -d "$PWD/../build" ]; then
    . $PWD/environment_debug
else
    . $PWD/environment_release
fi

ofdm_tx_gui.py &

tx.py --freq=2.45G --bandwidth=1M --fft-length=256 --subcarriers=200 $*

