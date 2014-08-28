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
from fbmc_symbol_estimation_vcb import fbmc_symbol_estimation_vcb
from fbmc_symbol_creation_bvc import fbmc_symbol_creation_bvc

import math
import random

class qa_fbmc_fbmc_symbol_estimation_vcb (gr_unittest.TestCase):

    def setUp (self):
        self.tb = gr.top_block ()

    def tearDown (self):
        self.tb = None

    def test_001_t (self):
        # set up fg
        src_data = (0,1,3,2,3,1,0,0,2,1,2,3)
        expected_result = src_data
        src = blocks.vector_source_b(src_data)
        cre = fbmc_symbol_creation_bvc(M=4, qam_size=4)
        est = fbmc_symbol_estimation_vcb(M=4,qam_size=4)
        dst = blocks.vector_sink_b()
        self.tb.connect(src,cre,est,dst)
        self.tb.run ()
        # check data
        result_data = dst.data()
        self.assertEqual(expected_result,result_data)

    def test_002_t (self):
        M=int(math.pow(2,6))
        num_per_sc = int(math.pow(2,16))
        mapper = {0:0.7071067690849304+0.7071067690849304j,
        1:-0.7071067690849304+0.7071067690849304j,
        2:-0.7071067690849304-0.7071067690849304j,
        3:+0.7071067690849304-0.7071067690849304j}
        src_data =list()
        expected_result = list()
        for i in range(M*num_per_sc):
            randy = int(random.random()*10)%4
            src_data.append(mapper[randy])
            expected_result.append(long(randy))

        src = blocks.vector_source_c(src_data,vlen=M)
        est = fbmc_symbol_estimation_vcb(M=M,qam_size=4)
        dst = blocks.vector_sink_b()

        self.tb.connect(src,est,dst)
        self.tb.run ()
        # check data
        result_data = dst.data()
        self.assertEqual(tuple(expected_result),result_data)


if __name__ == '__main__':
    gr_unittest.run(qa_fbmc_fbmc_symbol_estimation_vcb, "qa_fbmc_fbmc_symbol_estimation_vcb.xml")
