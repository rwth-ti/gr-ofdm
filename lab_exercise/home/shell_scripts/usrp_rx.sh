#!/bin/bash
if [ -f /opt/gr-ofdm/environment ]
    then
    . /opt/gr-ofdm/environment
else
    . /opt/gr-ofdm/bin/environment_lab
fi

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
    TXHOSTNAME="TXHOSTNAME"
fi
CARRIER=$(zenity --entry --title "Carrier frequency" --text "Enter transmitter's carrier frequency:" --entry-text "$CARRIER")
TXHOSTNAME=$(zenity --entry --title "Tx Hostname" --text "Enter transmitter's Hostname:" --entry-text "$TXHOSTNAME")
echo $CARRIER > carrier
echo $TXHOSTNAME > txhostname

while [ "$TXHOSTNAME" == "TXHOSTNAME" ]
do

	zenity --info --text="Please enter the Hostname of the Transceiver. You find it on the sticker of the Transceiver-PC"
	TXHOSTNAME=$(zenity --entry --title "Tx Hostname" --text "Enter transmitter's Hostname:" --entry-text "$TXHOSTNAME")
echo $TXHOSTNAME > txhostname
done
if [ -f txhostname ]
then
    TXHOSTNAME=`cat txhostname`
fi

ping -q -c 1 -w 1 $TXHOSTNAME
if [ $? -ne 0 ]; 
then
	ping -q -c 1 -w 1 www
	if [ $? -ne 0 ]; 
	then
		echo "ERROR: Network not rechable!"
		zenity --error --text "Network not rechable!"
		
	else

		echo "Host" $TXHOSTNAME "unknown"
		zenity --error --text "Hostname $TXHOSTNAME not found!"

   		exit
	fi

else
	echo "Connect to Host" $TXHOSTNAME

fi

/opt/gr-ofdm/bin/run_usrp_rx_gui.sh --tx-hostname=$TXHOSTNAME -f $CARRIER --dc-null=2
