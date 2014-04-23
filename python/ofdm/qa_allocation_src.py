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

class qa_allocation_src (gr_unittest.TestCase):

    def setUp (self):
        self.tb = gr.top_block ()

    def tearDown (self):
        self.tb = None

    def test_001_t (self):
        src = ofdm.allocation_src(6,3,"tcp://*:3333")
        src.set_allocation([2]*6,[3]*6)
        #skiphead = blocks.skiphead( gr.sizeof_float, 8 )
        limit_id = blocks.head( gr.sizeof_short, 4 )
        limit_bitcount = blocks.head( gr.sizeof_int, 4 )
        limit_bitloading = blocks.head( gr.sizeof_char*6, 4 )
        limit_power = blocks.head( gr.sizeof_gr_complex*6, 4 )
        dst_id = blocks.vector_sink_s()
        dst_bitcount = blocks.vector_sink_i()
        dst_bitloading = blocks.vector_sink_b(6)
        dst_power = blocks.vector_sink_c(6)
        self.tb.connect((src,0),limit_id,dst_id)
        self.tb.connect((src,1),limit_bitcount,dst_bitcount)
        self.tb.connect((src,2),limit_bitloading,dst_bitloading)
        self.tb.connect((src,3),limit_power,dst_power)
        # set up fg
        self.tb.run ()
        # check data
        result_id = dst_id.data()
        result_bitcount = dst_bitcount.data()
        result_bitloading = dst_bitloading.data()
        result_power = dst_power.data()
        print "id", result_id
        print "bitcount", result_bitcount
        print "bitloading", result_bitloading
        print "power", result_power

#        expected_id = [0,1]
#        self.assertFloatTuplesAlmostEqual(expected_id, result_data, 6)


if __name__ == '__main__':
    gr_unittest.run(qa_allocation_src, "qa_allocation_src.xml")
