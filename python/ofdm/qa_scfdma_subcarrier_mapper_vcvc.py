#!/usr/bin/env python
# -*- coding: utf-8 -*-
# 
# Copyright 2015 <+YOU OR YOUR COMPANY+>.
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

class qa_scfdma_subcarrier_mapper_vcvc (gr_unittest.TestCase):

    def setUp (self):
        self.tb = gr.top_block ()

    def tearDown (self):
        self.tb = None

    def test_001_t (self):
        # set up fg
        M=256	
        N=12
        num_syms = 2**13
        start = 0
        indices = range(start,M-1,M/N)
        mode = 1 # test dfdma
        src_data = list()
        expected_result = list()
        expected_result.extend([0]*M*num_syms)

        for i in range(N*num_syms):
        	data = int(random.random()*10)+1+(int(random.random()*10)+1)*1j
        	src_data.append(data)
        	expected_result[indices[i%N]+(i/N)*M] = data

    	# print('exp:')
    	# print(expected_result)
    	# print('--a--a--a--a--a--')
    	# print(src_data)

        src = blocks.vector_source_c(src_data,vlen=N)
        mapper = ofdm.scfdma_subcarrier_mapper_vcvc(N,M,start,mode)
        dst = blocks.vector_sink_c(vlen=M)
        self.tb.connect(src,mapper,dst)

        self.tb.run ()
        # check data
        # print('res:')
        result_data = dst.data()
        # print(result_data)
        self.assertComplexTuplesAlmostEqual(expected_result,result_data,7)

    def test_002_t (self):
    	# set up fg
        M=512	
        N=12
        num_syms = 2**13
        start = 0
        indices = range(start,start+N)
        mode = 0 # test lfdma
        src_data = list()
        expected_result = list()
        expected_result.extend([0]*M*num_syms)

        for i in range(N*num_syms):
        	data = int(random.random()*10)+1+(int(random.random()*10)+1)*1j
        	src_data.append(data)
        	expected_result[indices[i%N]+(i/N)*M] = data

    	# print('exp:')
    	# print(expected_result)
    	# print('--a--a--a--a--a--')
    	# print(src_data)

        src = blocks.vector_source_c(src_data,vlen=N)
        mapper = ofdm.scfdma_subcarrier_mapper_vcvc(N,M,start,mode)
        dst = blocks.vector_sink_c(vlen=M)
        self.tb.connect(src,mapper,dst)

        self.tb.run ()
        # check data
        # print('res:')
        result_data = dst.data()
        # print(result_data)
        self.assertComplexTuplesAlmostEqual(expected_result,result_data,7)


if __name__ == '__main__':
    gr_unittest.run(qa_scfdma_subcarrier_mapper_vcvc, "qa_scfdma_subcarrier_mapper_vcvc.xml")
