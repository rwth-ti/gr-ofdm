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
from fbmc_vector_reshape_vcvc import fbmc_vector_reshape_vcvc

import random

class qa_fbmc_vector_reshape_vcvc (gr_unittest.TestCase):

    def setUp (self):
        self.tb = gr.top_block ()

    def tearDown (self):
        self.tb = None

    def test_001_t (self):
        # set up fg
        src_data=list()
        for i in range(55000):
        	src_data.append(int(random.random()*10))
        src = blocks.vector_source_c(src_data,vlen=200)
        dst = blocks.vector_sink_c(vlen=40)
        vr = fbmc_vector_reshape_vcvc(200,40)

        self.tb.connect(src,vr,dst)
        self.tb.run()

        result_data = dst.data()
        self.assertComplexTuplesAlmostEqual(tuple(src_data),tuple(result_data),100)

    def test_002_t (self):
        # set up fg
        src_data=list()
        for i in range(25000):
        	src_data.append(int(random.random()*10))
        src = blocks.vector_source_c(src_data,vlen=25)
        dst = blocks.vector_sink_c(vlen=100)
        vr = fbmc_vector_reshape_vcvc(25,100)

        self.tb.connect(src,vr,dst)
        self.tb.run()

        result_data = dst.data()
        self.assertComplexTuplesAlmostEqual(tuple(src_data),tuple(result_data),100)


if __name__ == '__main__':
    gr_unittest.run(qa_fbmc_vector_reshape_vcvc, "qa_fbmc_vector_reshape_vcvc.xml")
