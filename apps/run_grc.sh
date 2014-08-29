#!/bin/sh

cd $(dirname $0)

if [ -d "$PWD/../build" ]; then
    . $PWD/environment_debug
    # . $PWD/environment_release
else
    . $PWD/environment_release
    # . $PWD/environment_debug
fi

gnuradio-companion
