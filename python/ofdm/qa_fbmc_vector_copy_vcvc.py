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

class qa_fbmc_vector_copy_vcvc (gr_unittest.TestCase):

    def setUp (self):
        self.tb = gr.top_block ()

    def tearDown (self):
        self.tb = None

    def test_001_t (self):
    	M= 2**10
        interpolation = 2
        num_vectors = 2**8
        src_data = list()
        expected_result = list()
        for i in range(M*num_vectors):
        	src_data.append(int(random.random()*10))
        	if (i%M)==(M-1):
        		for k in range(interpolation):
        			expected_result.extend(src_data[i+1-M:i+1])

    	# print expected_result
    	src = blocks.vector_source_c(src_data,vlen=M)
    	vcp = ofdm.fbmc_vector_copy_vcvc(M,interpolation)
    	dst = blocks.vector_sink_c(vlen=M)

    	self.tb.connect(src,vcp,dst)
    	self.tb.run()

    	result_data = dst.data()
    	# print result_data

    	self.assertComplexTuplesAlmostEqual(tuple(expected_result),result_data)


if __name__ == '__main__':
    gr_unittest.run(qa_fbmc_vector_copy_vcvc, "qa_fbmc_vector_copy_vcvc.xml")
