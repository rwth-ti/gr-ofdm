#!/bin/sh

if [ -d "$PWD/../build" ]; then
    . $PWD/environment_debug
else
    . $PWD/environment_release
fi

ofdm_rx_gui.py --tx-hostname=tabur &

rx.py -f 2.45G --disable-ctf-enhancer --bandwidth=1M --subcarriers=200 --fft-length=256 --scatterplot --ber-window=50000 $1 $2 $3
