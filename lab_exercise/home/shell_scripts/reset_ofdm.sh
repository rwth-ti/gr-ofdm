cd


if [[ $USER == *"ofdmlab"* ]];
then
    zenity --question --text="Reset to OFDM-Lab defaults?"
    if [ $? -eq 0 ] ; then
     rsync -av --force --delete-after --exclude .Xauthority --exclude .local/share/keyrings /home/ofdmlab-default/ ~
else
    zenity --error --text="No ofdmlab-account! Abort reset!"
    echo "ERROR:No ofdmlab-account! Abort reset."
fi

