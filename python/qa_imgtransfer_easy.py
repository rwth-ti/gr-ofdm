#!/usr/bin/env python

from gnuradio import gr, gr_unittest
import ofdm.ofdm_swig as ofdm
from random import random, randint

class my_top_block (gr.top_block):
    def __init__(self):
        gr.top_block.__init__(self)
        sig_src = gr.sig_source_i(200,gr.GR_CONST_WAVE,0,0,3600)
        src = ofdm.imgtransfer_src( "test.bmp" )

        UDP_PACKET_SIZE = 4096

        imgsink = ofdm.imgtransfer_sink( UDP_PACKET_SIZE,
                                         "127.0.0.1", 0, "127.0.0.1", 45454, "test.bmp" )

        self.connect(sig_src,(src,0))
        self.connect(sig_src,(imgsink,0))

        self.connect(src,(imgsink,1))

if __name__ == '__main__':
    try:
        my_top_block().run()
    except KeyboardInterrupt:
        pass

