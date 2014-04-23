if [ "`echo $USER | tr -d [0-9]`" = "mme" ] ; then
	if [ -f "$HOME/resetaccount" ] ; then
		if [ "$DISPLAY" = "" ] ; then
			echo "Reset Account to mme defaults?"
			read
		else
			xmessage -buttons Ok:0,Cancel:1 "Reset Account to mme defaults?"
		fi
		if [ $? -eq 0 ] ; then
			rsync -av --del /home/mme0/ .
			gconftool-2 -s /apps/gnome-screensaver/idle_activation_enabled --type=bool false
			gconftool-2 -s /desktop/gnome/peripherals/mouse/motion_acceleration --type=float 0.8
		fi
	fi
fi
if [ -r "/opt/gnuradio/bin/environment" ]; then
	. /opt/gnuradio/bin/environment
fi

PATH="$PATH:/opt/sources/ofdm_ti_praktikum/ofdm_ti_praktikum_2010/src/lab_exercise/lab_ofdm_sdr/shell_scripts"
