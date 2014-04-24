#!/bin/sh

cd $(dirname $0)

if [ -d "$PWD/../build" ]; then
    . $PWD/environment_debug
else
    . $PWD/environment_release
fi

benchmark_ofdm.py --snr=10 --scatterplot --ber-window=50000 --disable-ctf-enhancer --freqoff=0 --fft-length=256 --subcarriers=200 $1 $2 $3
