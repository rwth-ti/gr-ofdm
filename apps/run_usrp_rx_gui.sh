#!/bin/bash

cd $(dirname $0)

if [ -d "$PWD/../build" ]; then
    . $PWD/environment_debug
else
    . $PWD/environment_release
fi

# check for --tx-hostname argument
for ARG in "$@"
do
    if [[ $ARG = "--tx-hostname="* ]]
    then
        TXHOSTNAME=$ARG
    fi
done
echo $TXHOSTNAME

ofdm_rx_gui.py $TXHOSTNAME &

rx.py --disable-ctf-enhancer --bandwidth=1M --subcarriers=200 --fft-length=256 --scatterplot --ber-window=50000 --freq=2.45G $*
