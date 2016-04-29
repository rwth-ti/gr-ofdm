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

if   [[ $CARRIER  != *"G"* ]] && [[  $CARRIER != *"M"* ]] && [  ${#CARRIER} -le  9 ];
then
    zenity --info --text="Your choosen frequency is "$CARRIER"Hz. This seems to be too small\! \nThe frequency should be ratther 2._____Ghz"
fi

if [[ $CARRIER == *","* ]];
then
    zenity --info --text="Please use a dot as decimal mark!"
    exit
fi



$GROFDM_DIR/bin/run_usrp_tx_gui.sh -f $CARRIER
