#!/bin/sh

cd $(dirname $0)

if [ -d "$PWD/../build" ]; then
    . $PWD/environment_debug
else
    . $PWD/environment_release
fi

../python/ofdm/qa_fbmc_subchannel_processing_mu_vcvc.py
