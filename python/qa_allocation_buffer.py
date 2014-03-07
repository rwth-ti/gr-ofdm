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

class qa_allocation_buffer (gr_unittest.TestCase):

    def setUp (self):
        self.tb = gr.top_block ()

    def tearDown (self):
        self.tb = None

    def test_001_t (self):
        alloc = ofdm.allocation_buffer(8,4,"tcp://localhost:3333")
        #skiphead = blocks.skiphead( gr.sizeof_float, 8 )
        limit_id = blocks.head( gr.sizeof_short, 10 )
        limit_bitcount = blocks.head( gr.sizeof_int, 10 )
        limit_bitloading = blocks.head( gr.sizeof_char*8, 10 )
        limit_power = blocks.head( gr.sizeof_gr_complex*8, 10 )
        src_id = blocks.vector_source_s([1],False,1)
        dst_bitcount = blocks.vector_sink_i()
        dst_bitloading = blocks.vector_sink_b(8)
        dst_power = blocks.vector_sink_c(8)
        self.tb.connect(src_id,limit_id,alloc)
        self.tb.connect((alloc,0),limit_bitcount,dst_bitcount)
        self.tb.connect((alloc,1),limit_bitloading,dst_bitloading)
        self.tb.connect((alloc,2),limit_power,dst_power)
        # set up fg
        self.tb.run ()
        # check data
        result_bitcount = dst_bitcount.data()
        result_bitloading = dst_bitloading.data()
        result_power = dst_power.data()
        print "bitcount", result_bitcount
        print "bitloading", result_bitloading
        print "power", result_power

if __name__ == '__main__':
    gr_unittest.run(qa_allocation_buffer, "qa_allocation_buffer.xml")
