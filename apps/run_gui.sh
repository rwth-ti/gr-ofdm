#!/bin/sh

cd $(dirname $0)

if [ -d "$PWD/../build" ]; then
    . $PWD/environment_debug
else
    . $PWD/environment_release
fi

ofdm_tx_gui.py $1 &
ofdm_rx_gui.py $1

