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
from fbmc_remove_preamble_vcvc import fbmc_remove_preamble_vcvc
from fbmc_insert_preamble_vcvc import fbmc_insert_preamble_vcvc


import math
import random

class qa_fbmc_remove_preamble_vcvc (gr_unittest.TestCase):

    def setUp (self):
        self.tb = gr.top_block ()

    def tearDown (self):
        self.tb = None

    def test_001_t (self):
        # set up fg
        src_data=(9,9j,-9,-9j,2,2j,-2,-2j,4,4j,-4,-4j,6,6j,-6,-6j)
        preamble = (0,0,0,0,1,-1j,-1,1j,0,0,0,0)
        # expected_result=(0,0,0,0,1,-1j,-1,1j,0,0,0,0,
        # 	1,1j,-1,-1j,2,2j,-2,-2j,
        # 	0,0,0,0,1,-1j,-1,1j,0,0,0,0,
        # 	4,4j,-4,-4j,6,6j,-6,-6j)
        src = blocks.vector_source_c(src_data,vlen=4)
        ipr = fbmc_insert_preamble_vcvc(4,1,preamble)
        rpr = fbmc_remove_preamble_vcvc(4,1,len(preamble))
        dst = blocks.vector_sink_c(vlen=4)
        self.tb.connect(src,ipr,rpr,dst)
        self.tb.run ()
        # check data
        result_data=dst.data()
        # print len(preamble)
        self.assertEqual(src_data,result_data)

    def test_002_t(self):
        M=int(math.pow(2,7))
        len_frame = 10
        num_frame = int(math.pow(2,12))
        preamble = [0]*M+[1, -1j, -1, 1j]*int(M/4)+[0]*M

        src_data=list()
        for i in range(len_frame*2*num_frame*M):
            src_data.append(int(random.random()*10))

        src = blocks.vector_source_c(src_data,vlen=M)
        ipr = fbmc_insert_preamble_vcvc(M,len_frame,preamble)
        rpr = fbmc_remove_preamble_vcvc(M,len_frame,len(preamble))
        dst = blocks.vector_sink_c(vlen=M)
        self.tb.connect(src,ipr,rpr,dst)
        self.tb.run ()
        # check data
        result_data = dst.data()
        # print result_data
        self.assertComplexTuplesAlmostEqual(tuple(src_data),tuple(result_data))


if __name__ == '__main__':
    gr_unittest.run(qa_fbmc_remove_preamble_vcvc, "qa_fbmc_remove_preamble_vcvc.xml")
