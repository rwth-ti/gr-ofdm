#!/bin/sh

cd $(dirname $0)

if [ -d "$PWD/../build" ]; then
    . $PWD/environment_debug
else
    . $PWD/environment_release
fi

ofdm_rx_gui.py $1 &

rx.py --disable-ctf-enhancer --bandwidth=1M --subcarriers=200 --fft-length=256 --scatterplot --ber-window=50000 --freq=2.45G --lo-offset=4M $*
