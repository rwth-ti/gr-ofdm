#!/bin/sh

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

/opt/lab-ofdm/gr-ofdm/bin/run_usrp_rx_gui.sh --tx-hostname $TXHOSTNAME -f $CARRIER
