#!/bin/sh

./run_app.sh gui/ofdm_rx_gui.py & # --tx-hostname=amphitrite &

./run_app.sh ../python/rx.py -f 2.450020G -a "type=usrp1" --disable-ctf-enhancer --bandwidth=1M --subcarriers=200 --fft-length=256 --scatterplot --ber-window=50000 --spec=A:0 # --tx-hostname=amphitrite $1 $2 $3
