#!/usr/bin/env python
# -*- coding: utf-8 -*-
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

class qa_multiply_frame_fc (gr_unittest.TestCase):

    def setUp (self):
        self.tb = gr.top_block ()

    def tearDown (self):
        self.tb = None


    def test_multiply_frame(self):
        src1_data = (1+1j,  2+2j, 3+3j, 4+4j, 5+5j, 1,1,1,1,1,1,1,1,1,1,1)
        src2_data = (8, -3, 4, 8, 2, 1,1,1,1,1,1,1,1,1,1,1)
        expected_result = (8+8j, -6-6j, 12+12j, 32+32j, 10+10j, 1,1,1,1,1,1,1,1,1,1,1)

        src3_data =(1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1)
        src4_data =(1,2,3,4)
        expected_result2 =(1,1,1,1,2,2,2,2,3,3,3,3,4,4,4,4)


        op = ofdm.multiply_frame_fc(4,2)


        src1 = blocks.vector_source_c(src3_data,False,2)
        src2 = blocks.vector_source_f(src4_data,False,2)
        self.tb.connect(src1, (op, 1))
        self.tb.connect(src2, (op, 0))

        dst = blocks.vector_sink_c(2)
        self.tb.connect(op, dst)
        self.tb.run()
        result_data = dst.data()
        self.assertComplexTuplesAlmostEqual(expected_result2, result_data, 5)






if __name__ == '__main__':
    gr_unittest.run(qa_multiply_frame_fc, "qa_multiply_frame_fc.xml")
