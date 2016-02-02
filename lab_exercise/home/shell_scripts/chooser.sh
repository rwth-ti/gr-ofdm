#!/bin/bash

echo "Choose your gr-ofdm-Version"
ans=$(zenity --list --title="Choose GR-OFDM Version" --column="Version" "default" 2015 2016)
echo "Choose $ans"

if [ -f $HOME/env ]
then
    rm ~/env
fi

case $ans in
    "default")
    echo "export GNURADIO_DIR=/opt/gnuradio-3.7.7" >>~/env
    GNURADIO_DIR=/opt/gnuradio-3.7.7
    echo "export GROFDM_DIR=/opt/gr-ofdm" >>~/env
    GROFDM_DIR=/opt/gr-ofdm
    ;;

    2015)
    echo "export GNURADIO_DIR=/opt/gnuradio-3.7.7" >>~/env
    GNURADIO_DIR=/opt/gnuradio-3.7.7
    echo "export GROFDM_DIR=/opt/gr-ofdm" >>~/env
    GROFDM_DIR=/opt/gr-ofdm/beta
    ;;

    2016)
    echo "export GNURADIO_DIR=/opt/gnuradio-3.7.7" >>~/env
    GNURADIO_DIR=/opt/gnuradio-3.7.7
    echo "export GROFDM_DIR=/opt/gr-ofdm/beta" >>~/env
    GROFDM_DIR=/opt/gr-ofdm
    ;;
    *)
    echo "Nothing changed."
esac


. $HOME/env
if [ -f /opt/gr-ofdm/environment ]
then
        tail -n +5 /opt/gr-ofdm/environment >> $HOME/env
else
        tail -n +5 /opt/gr-ofdm/bin/environment_lab >> $HOME/env
fi

. ~/env

echo "Changing completed"

echo "as a result:" 

head  $HOME/env

