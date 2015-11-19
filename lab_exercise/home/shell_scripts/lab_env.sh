if [ -f /opt/gr-ofdm/environment ]
then
    . /opt/gr-ofdm/environment
else
    . /opt/gr-ofdm/bin/environment_lab
fi
bash -c $*||{
    echo "Programm start failed."
    echo $1
    zenity --error --text "Programm start failed. Please make sure that no other USRP programm or terminal is running!"
    }            

