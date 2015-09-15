if [ "`echo $USER | tr -d [0-9]`" = "ofdmlab" ] ; then
    if [ "$DISPLAY" = "" ] ; then
        echo "Reset Account to ofdmlab defaults?"
        read
    else
        xmessage -buttons Ok:0,Cancel:1 "Reset Account to ofdmlab defaults?"
    fi
    if [ $? -eq 0 ] ; then
        rsync -av --del /home/ofdmlab0/ .
    fi
fi

#Gnuradio
if [ -f /opt/gr-ofdmn/bin/environment ]; then
         . /opt/gr-ofdm/bin/environment
fi
