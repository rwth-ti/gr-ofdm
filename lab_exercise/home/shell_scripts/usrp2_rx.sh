#!/bin/bash

killall python

if [ -f carrier ]
then
    CARRIER=`cat carrier`
else
    CARRIER=2.45G
fi
if [ -f txhostname ]
then
    TXHOSTNAME=`cat txhostname`
else
    TXHOSTNAME=TXHOSTNAME
fi
CARRIER=$(zenity --entry --title "Carrier frequency" --text "Enter transmitter's carrier frequency:" --entry-text "$CARRIER")
TXHOSTNAME=$(zenity --entry --title "Tx Hostname" --text "Enter transmitter's Hostname:" --entry-text "$TXHOSTNAME")
echo $CARRIER > carrier
echo $TXHOSTNAME > txhostname

cd /opt/gr-ofdm/apps/
./run_app.sh gui/ofdm_rx_gui.py --tx-hostname=$TXHOSTNAME &
./run_app.sh ../python/rx.py -f $CARRIER --disable-ctf-enhancer --bandwidth=1M --subcarriers=200 --fft-length=256 --scatterplot --ber-window=50000 --tx-hostname=$TXHOSTNAME

