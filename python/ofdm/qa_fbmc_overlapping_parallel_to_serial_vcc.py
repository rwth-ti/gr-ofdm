#!/usr/bin/env python
# -*- coding: utf-8 -*-
# 
# Copyright 2014 <+YOU OR YOUR COMPANY+>.
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
from fbmc_overlapping_parallel_to_serial_vcc import fbmc_overlapping_parallel_to_serial_vcc

import random
import math

class qa_fbmc_overlapping_parallel_to_serial_vcc (gr_unittest.TestCase):

    def setUp (self):
        self.tb = gr.top_block ()

    def tearDown (self):
        self.tb = None

    def test_001_t (self):
        # set up fg
        src_data0 =(1,2,3,4,5,6,7,8,0,0,0,0)
        src_data1 =(1j,2j,3j,4j,5j,6j,7j,8j)
        expected_result = (1,2,3+1j,4+2j,5+3j,6+4j,7+5j,8+6j,7j,8j)
        src0 = blocks.vector_source_c(src_data0,vlen=4)
        src1 = blocks.vector_source_c(src_data1,vlen=4)
        oas = fbmc_overlapping_parallel_to_serial_vcc(M=4)
        dst = blocks.vector_sink_c(vlen=1)
        self.tb.connect(src0,(oas,0))
        self.tb.connect(src1,(oas,1))
        self.tb.connect(oas,dst)
        self.tb.run ()
        # check data
        result = dst.data()
        self.assertEqual(expected_result,result)

    def test_002_t (self):
        # set up fg
        src_data0 =(1,2,3,4,5,6,7,8,1j,2j,3j,4j,5j,6j,7j,8j,0,0,0,0,0,0,0,0)
        src_data1 =(1j,2j,3j,4j,5j,6j,7j,8j,1,2,3,4,5,6,7,8)
        expected_result = (1,2,3,4,5+1j,6+2j,7+3j,8+4j,
            6j, 8j, 10j, 12j,1+5j, 2+6j, 3+7j, 4+8j,5,6,7,8)
        src0 = blocks.vector_source_c(src_data0,vlen=8)
        src1 = blocks.vector_source_c(src_data1,vlen=8)
        oas = fbmc_overlapping_parallel_to_serial_vcc(M=8)
        dst = blocks.vector_sink_c(vlen=1)
        self.tb.connect(src0,(oas,0))
        self.tb.connect(src1,(oas,1))
        self.tb.connect(oas,dst)
        self.tb.run ()
        # check data
        result = dst.data()
        self.assertEqual(expected_result,result)

    def test_003_t(self):
        M=int(math.pow(2,7))
        num = int(math.pow(2,14))
        src0 = list()
        src1 = list()
        for i in range(M*num):
            src0.append(int(random.random()*10))
            src1.append(int(random.random()*10)*1j)
        src0.extend([0]*M)
        expected_result = list()
        expected_result.extend(src0[0:int(M/2)])
        for i in range(len(src1)):
            expected_result.append(src1[i]+src0[int(M/2)+i])
        src0 = blocks.vector_source_c(src0,vlen=M)
        src1 = blocks.vector_source_c(src1,vlen=M)
        oas = fbmc_overlapping_parallel_to_serial_vcc(M=M)
        dst = blocks.vector_sink_c(vlen=1)
        self.tb.connect(src0,(oas,0))
        self.tb.connect(src1,(oas,1))
        self.tb.connect(oas,dst)
        self.tb.run ()
        # check data
        result = dst.data()
        self.assertComplexTuplesAlmostEqual(tuple(expected_result),tuple(result),6)



if __name__ == '__main__':
    gr_unittest.run(qa_fbmc_overlapping_parallel_to_serial_vcc, "qa_fbmc_overlapping_parallel_to_serial_vcc.xml")