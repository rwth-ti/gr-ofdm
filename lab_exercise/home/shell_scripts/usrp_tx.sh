#!/bin/bash 



if [ -f carrier ]
then
    CARRIER=`cat carrier`
else
    CARRIER=2.45G
fi
CARRIER=$(zenity --entry --title "Carrier frequency for $HOSTNAME" --text "This host is named $HOSTNAME.\nEnter transmitter's carrier frequency:" --entry-text "$CARRIER")

echo $CARRIER > carrier

echo "Hostname: $HOSTNAME"

if [[ $CARRIER == *","* ]];
then
    zenity --error --text="Please use a dot as decimal mark!"
    exit
fi

if   [[ $CARRIER  != *"G"* ]] && [[  $CARRIER != *"M"* ]] && [  ${#CARRIER} -le  9 ];
then
    zenity --warning --text="Your choosen frequency is "$CARRIER"(Hz). This seems to be very small\! \nThe frequency should rather be 2.4___G(Hz)"
    exit
fi

$GROFDM_DIR/bin/run_usrp_tx_gui.sh -f $CARRIER --lo-offset=4M
