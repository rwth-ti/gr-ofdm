#!/bin/sh

./run_app.sh gui/ofdm_rx_gui.py --tx-hostname=tabur &

./run_app.sh ../python/rx.py -f 2.450020G -a "type=usrp2" --disable-ctf-enhancer --bandwidth=1M --subcarriers=200 --fft-length=256 --scatterplot --ber-window=50000 --spec=A:0 --tx-hostname=tabur $1 $2 $3
