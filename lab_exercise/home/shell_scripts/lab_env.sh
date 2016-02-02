if [ -f $HOME/env ]
then
    . $HOME/env
else
    if [ -f /opt/gr-ofdm/environment ]
    then
        . /opt/gr-ofdm/environment
    else
        . /opt/gr-ofdm/bin/environment_lab
    fi
fi
    
bash -c "$*"||{
    echo "Programm start failed."
    echo "$*"
    zenity --error --text "Programm start failed. Please make sure that no other USRP programm or terminal is running!"
    }            

