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
import ofdm_swig as ofdm

import random

class qa_fbmc_separate_vcvc (gr_unittest.TestCase):

    def setUp (self):
        self.tb = gr.top_block ()

    def tearDown (self):
        self.tb = None

    def test_001_t (self):
        # set up fg
        src_data = (1,2,3,4,1j,2j,3j,4j,5,6,7,8,5j,6j,7j,8j)
        expected_result0 = (1,2,3,4,5,6,7,8)
        expected_result1 = (1j,2j,3j,4j,5j,6j,7j,8j)
        src = blocks.vector_source_c(src_data,vlen=4)
        sep = ofdm.fbmc_separate_vcvc(M=4,num_output=2)
        dst0 = blocks.vector_sink_c(vlen=4)
        dst1 = blocks.vector_sink_c(vlen=4)
        self.tb.connect(src,sep)
        self.tb.connect((sep,0),dst0)
        self.tb.connect((sep,1),dst1)
        self.tb.run ()
        # check data
        result0 = dst0.data()
        result1 = dst1.data()
        self.assertEqual(result1,expected_result1)
        self.assertEqual(result0,expected_result0)

    def test_002_t(self):
        # set up fg
        M=512
        flag = True
        src_data = list()
        expected_result0 = list()
        expected_result1 = list()
        for i in range(8192*8):
            src_data.append(int(random.random()*10))
            if flag:
                expected_result0.append(src_data[i])
            else:
                expected_result1.append(src_data[i])

            if i%M == M-1:
                flag = not flag
        
        src = blocks.vector_source_c(src_data,vlen=M)
        sep = ofdm.fbmc_separate_vcvc(M=M,num_output=2)
        dst0 = blocks.vector_sink_c(vlen=M)
        dst1 = blocks.vector_sink_c(vlen=M)
        self.tb.connect(src,sep)
        self.tb.connect((sep,0),dst0)
        self.tb.connect((sep,1),dst1)
        self.tb.run ()
        # check data
        result0 = dst0.data()
        result1 = dst1.data()
        self.assertComplexTuplesAlmostEqual(tuple(result1),tuple(expected_result1),150)
        self.assertComplexTuplesAlmostEqual(tuple(result0),tuple(expected_result0),150)


if __name__ == '__main__':
    gr_unittest.run(qa_fbmc_separate_vcvc, "qa_fbmc_separate_vcvc.xml")
