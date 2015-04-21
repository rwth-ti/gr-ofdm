#!/bin/sh

cd $(dirname $0)

if [ -d "$PWD/../build" ]; then
    . $PWD/environment_debug
else
    . $PWD/environment_release
fi

ofdm_tx_gui.py &
ofdm_rx_gui.py  &
benchmark_fbmc.py --snr=10 --scatterplot --ber-window=50000 --disable-ctf-enhancer --freqoff=0 --fft-length=256 --subcarriers=208 --cp-length=0 $1 $2 $3 $4 $5 $6 $7 $8 $9 $10

