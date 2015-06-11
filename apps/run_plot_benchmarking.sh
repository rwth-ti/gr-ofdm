#!/bin/sh

cd $(dirname $0)

if [ -d "$PWD/../build" ]; then
    . $PWD/environment_debug
else
    . $PWD/environment_release
fi

./benchmarking/plot_results_transceiver.py $1 $2 $3 $4 $5 $6 $7 $8 $9 $10

