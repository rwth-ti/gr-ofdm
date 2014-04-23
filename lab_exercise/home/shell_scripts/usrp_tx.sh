#!/bin/bash

killall python

if [ -f carrier ]
then
    CARRIER=`cat carrier`
else
    CARRIER=2.45G
fi
CARRIER=$(zenity --entry --title "Carrier frequency" --text "Enter transmitter's carrier frequency:" --entry-text "$CARRIER")
echo $CARRIER > carrier

cd /opt/gr-ofdm/apps/
./run_app.sh gui/ofdm_tx_gui.py &
./run_app.sh ../python/tx.py -f $CARRIER --bandwidth=1M --fft-length=256 --subcarriers=200

