#!/usr/bin/env python
# 
# Copyright 2013 <+YOU OR YOUR COMPANY+>.
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
        src_id = blocks.vector_source_s([0,1,2,3],False,1)
        src_bitcount = blocks.vector_source_i([2,3,3,1],False,1)
        ref_data = ofdm.reference_data_source_02_ib([1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12])
        dst = blocks.vector_sink_b(1)
        self.tb.connect(src_id,(ref_data,0))
        self.tb.connect(src_bitcount,(ref_data,1))
        self.tb.connect(ref_data,dst)
        self.tb.run()
        # check data
        result = dst.data()
        print "reference data stream: ", result

if __name__ == '__main__':
    gr_unittest.run(qa_tx_mux_ctrl, "qa_tx_mux_ctrl.xml")
