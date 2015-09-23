### copy .profile as root
# for i in ofdmlab{1..10}; do cp /srv/home/ofdmlab-default/.profile /srv/home/$i/ ;chown $i /srv/home/$i/.profile ; ls -l /srv/home/$i/.profile ; done

if [ "`echo $USER | tr -d [0-9]`" = "ofdmlab" ] ; then
	echo "[] syncing..."
	#if [ "$DISPLAY" = "" ] ; then
	#	echo "Reset to OFDM-Lab defaults?"
	#	read
	#else
	zenity --question --text="Reset to OFDM-Lab defaults?"
	#xmessage -buttons Ok:0,Cancel:1 -default Ok  -center -timeout 8 "Reset Account to defaults?"
	#fi
	if [ $? -eq 0 ] ; then
                	rsync -av --delete-after --exclude .Xauthority --exclude .local/share/keyrings /home/ofdmlab-default/ ~
		#	#gconftool-2 -s /apps/gnome-screensaver/idle_activation_enabled --type=bool false
		#	#gconftool-2 -s /desktop/gnome/peripherals/mouse/motion_acceleration --type=float 0.8
		cinnamon-screensaver-command -d
		gsettings set org.gnome.desktop.screensaver lock-enabled false
		gsettings set org.gnome.desktop.screensaver logout-enabled false
		gsettings set org.gnome.desktop.screensaver user-switch-enabled false
		gsettings set org.cinnamon.desktop.background picture-uri file:///home/$USER/.ti_wallpaper.jpg
		gsettings set org.cinnamon.desktop.lockdown disable-lock-screen true
		gsettings set org.cinnamon.desktop.lockdown disable-user-switching true
	fi
fi
###Set environment variables
[ -r /opt/gr-ofdm/environment ] && . /opt/gr-ofdm/environment




