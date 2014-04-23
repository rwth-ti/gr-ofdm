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

