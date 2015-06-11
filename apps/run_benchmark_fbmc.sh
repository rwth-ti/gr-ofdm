#!/bin/sh

cd $(dirname $0)

if [ -d "$PWD/../build" ]; then
    . $PWD/environment_debug
else
    . $PWD/environment_release
fi

benchmark_fbmc.py --snr=10 --scatterplot --ber-window=100000 --disable-ctf-enhancer --freqoff=0 --fft-length=256 --subcarriers=208 --disable-freq-sync $1 $2 $3
