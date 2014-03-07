#!/usr/bin/env python
# 
# Copyright 2014 Institute for Theoretical Information Technology,
#                RWTH Aachen University
#                www.ti.rwth-aachen.de
# 
# This is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 3, or (at your option)
# any later version.
# 
# This software is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
# 
# You should have received a copy of the GNU General Public License
# along with this software; see the file COPYING.  If not, write to
# the Free Software Foundation, Inc., 51 Franklin Street,
# Boston, MA 02110-1301, USA.
#

from gnuradio import gr, gr_unittest
import ofdm as ofdm
from random import random, randint

class my_top_block (gr.top_block):
    def __init__(self):
        gr.top_block.__init__(self)
        #sig_src = gr.sig_source_i(512,gr.GR_SIN_WAVE,0.1,1000,3600)
        sig_src = gr.sig_source_i(200,gr.GR_CONST_WAVE,0,0,3600)
        #sig_src = gr.noise_source_i(gr.GR_UNIFORM, 1000)
        src_file = "test.bmp"
        src = ofdm.imgtransfer_src( src_file )
        err_src = ofdm.bernoulli_bit_src( 0.01 )
        test_channel = ofdm.imgtransfer_testkanal()

        sequenz = [0]*256
        for i in range(256):
          sample = random()
          if sample<0.1:
            sequenz[i]=randint(-100,100)*3

        print sequenz

        vector_src = gr.vector_source_i(sequenz,True)
        add_block = gr.add_ii()

        self.connect(vector_src,(add_block,0))
        self.connect(sig_src,(add_block,1))

        xor = gr.xor_bb()

        UDP_PACKET_SIZE = 4096

        imgsink = ofdm.imgtransfer_sink( UDP_PACKET_SIZE, "127.0.0.1", 0, "127.0.0.1", 45454, src_file )

        self.connect(sig_src,(src,0))
        self.connect(sig_src,(test_channel,0))
        self.connect(add_block,(imgsink,0))

        self.connect(src,(test_channel,1))
        self.connect(vector_src,(test_channel,2))

        self.connect(test_channel,(xor,0))
        self.connect(err_src,(xor,1))

        self.connect(xor,(imgsink,1))

        #self.connect(imgsink,null_sink)


if __name__ == '__main__':
    try:
        my_top_block().run()
    except KeyboardInterrupt:
        pass

