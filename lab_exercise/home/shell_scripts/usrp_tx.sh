#!/bin/bash -l
. /opt/gr-ofdm/environment

if [ -f carrier ]
then
    CARRIER=`cat carrier`
else
    CARRIER=2.45G
fi
CARRIER=$(zenity --entry --title "Carrier frequency" --text "Enter transmitter's carrier frequency:" --entry-text "$CARRIER")
echo $CARRIER > carrier

/opt/gr-ofdm/bin/run_usrp_tx_gui.sh -f $CARRIER --spec=A:0 --args="type=usrp1"
