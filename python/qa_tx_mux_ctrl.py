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
from gnuradio import blocks
import ofdm_swig as ofdm

class qa_tx_mux_ctrl (gr_unittest.TestCase):

    def setUp (self):
        self.tb = gr.top_block ()

    def tearDown (self):
        self.tb = None

    def test_001_t (self):
        # set up fg
        src = blocks.vector_source_i([3,4,3,2,2,2,1],False,1)
        mux_ctrl = ofdm.tx_mux_ctrl(2)
        dst = blocks.vector_sink_b(1)
        self.tb.connect(src,mux_ctrl,dst)
        self.tb.run()
        # check data
        result = dst.data()
        print "mux stream: ", result

if __name__ == '__main__':
    gr_unittest.run(qa_tx_mux_ctrl, "qa_tx_mux_ctrl.xml")
