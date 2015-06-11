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

class qa_fbmc_junction_vcvc (gr_unittest.TestCase):

    def setUp (self):
        self.tb = gr.top_block ()

    def tearDown (self):
        self.tb = None

    def test_001_t (self):
        # set up fg
        src_data0 =(1,2,3,4,5,6,7,8)
        src_data1 =(1j,2j,3j,4j,5j,6j,7j,8j)
        expected_result = (1,2,3,4,1j,2j,3j,4j,5,6,7,8,5j,6j,7j,8j)
        src0 = blocks.vector_source_c(src_data0,vlen=4)
        src1 = blocks.vector_source_c(src_data1,vlen=4)
        jun = ofdm.fbmc_junction_vcvc(M=4,num_input=2)
        dst = blocks.vector_sink_c(vlen=4)

        self.tb.connect(src0,(jun,0))
        self.tb.connect(src1,(jun,1))
        self.tb.connect(jun,dst)
        self.tb.run ()
        # check data

        result_data = dst.data()
        self.assertEqual(expected_result,result_data)

    def test_002_t (self):
        # set up fg
        M=512
        num = 4096*128*4
        src_data0 = list()
        src_data1 = list()
        for i in range(num):
            src_data0.append(int(random.random()*10))
            src_data1.append(int(random.random()*10))
        expected_result = list()
        flag = True
        i0=0
        i1=0
        for i in range(num*2):
            if flag:
                expected_result.append(src_data0[i0])
                i0 = i0+1
            else:
                expected_result.append(src_data1[i1])
                i1 = i1+1

            if i%M==M-1:
                flag=not flag

        src0 = blocks.vector_source_c(src_data0,vlen=M)
        src1 = blocks.vector_source_c(src_data1,vlen=M)
        jun = ofdm.fbmc_junction_vcvc(M=M,num_input=2)
        dst = blocks.vector_sink_c(vlen=M)
        self.tb.connect(src0,(jun,0))
        self.tb.connect(src1,(jun,1))
        self.tb.connect(jun,dst)
        self.tb.run ()
        # check data

        result_data = dst.data()
        self.assertComplexTuplesAlmostEqual(tuple(result_data),tuple(expected_result),150)


if __name__ == '__main__':
    gr_unittest.run(qa_fbmc_junction_vcvc, "qa_fbmc_junction_vcvc.xml")
