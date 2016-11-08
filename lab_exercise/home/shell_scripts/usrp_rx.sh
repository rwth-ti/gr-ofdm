#!/bin/bash
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
echo $CARRIER > carrier

if [[ $CARRIER == *","* ]];
then
    zenity --error --text="Please use a dot as decimal mark!"
    exit
fi

if [[ $CARRIER  != *"G"* ]] && [[  $CARRIER != *"M"* ]] && [  ${#CARRIER} -le  9 ];
then
    zenity --warning --text="Your choosen frequency is "$CARRIER"(Hz). This seems to be very small\! \nThe frequency should rather be 2.4___G(Hz)"
    exit
fi

TXHOSTNAME=$(zenity --entry --title "tx hostname" --text "Enter transmitter's hostname:" --entry-text "$TXHOSTNAME")
echo $TXHOSTNAME > txhostname
while [ "$TXHOSTNAME" == "TXHOSTNAME" ] || [ "$TXHOSTNAME" == "" ]
do
	zenity --error --text="Please enter the hostname of the TRANSMITTER. You find it on the sticker or in the command line of the Tx PC"
	TXHOSTNAME=$(zenity --entry --title "tx hostname" --text "Enter transmitter's hostname:" --entry-text "$TXHOSTNAME")
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

$GROFDM_DIR/bin/run_usrp_rx_gui.sh --tx-hostname=$TXHOSTNAME -f $CARRIER --gui-frame-rate=950 --lo-offset=4M
