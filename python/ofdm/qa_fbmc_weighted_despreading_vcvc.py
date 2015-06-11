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

import math
import random

class qa_fbmc_weighted_despreading_vcvc (gr_unittest.TestCase):

    def setUp (self):
        self.tb = gr.top_block ()

    def tearDown (self):
        self.tb = None

    def test_001_t (self):
        # set up fg
        src_data =[1,2j,3,4j]
        expected_result = src_data
        src = blocks.vector_source_c(src_data, vlen=4)
        ws = ofdm.fbmc_weighted_spreading_vcvc(M=4,K=4)
        wd = ofdm.fbmc_weighted_despreading_vcvc(M=4,K=4)
        dst = blocks.vector_sink_c(vlen=4)
        self.tb.connect(src,ws,wd,dst)
        self.tb.run ()
        # check data
        output = dst.data()
        result_data = [output[0].real, (output[1].imag)*1j, output[2].real, (output[3].imag)*1j]
        # print result_data
        self.assertComplexTuplesAlmostEqual(tuple(expected_result),tuple(result_data),6)

    def test_002_t(self):
    	src_data =[1,2j,3,4j,5,6j,7,8j]
        expected_result = src_data
        src = blocks.vector_source_c(src_data, vlen=8)
        ws = ofdm.fbmc_weighted_spreading_vcvc(M=8,K=4)
        wd = ofdm.fbmc_weighted_despreading_vcvc(M=8,K=4)
        dst = blocks.vector_sink_c(vlen=8)
        self.tb.connect(src,ws,wd,dst)
        self.tb.run ()
        # check data
        output = dst.data()
        result_data = list()
        for i in range(8):
        	if i%2==0:
        		result_data.append(output[i].real)
        	else:
        		result_data.append(output[i].imag*1j)
        # print result_data
        self.assertComplexTuplesAlmostEqual(tuple(expected_result),tuple(result_data),6)

    def test_003_t(self):
    	src_data =[1,2j,3,4j,5,6j,7,8j,1j,2,3j,4,5j,6,7j,8]
        expected_result = src_data
        src = blocks.vector_source_c(src_data, vlen=8)
        ws = ofdm.fbmc_weighted_spreading_vcvc(M=8,K=4)
        wd = ofdm.fbmc_weighted_despreading_vcvc(M=8,K=4)
        dst = blocks.vector_sink_c(vlen=8)
        self.tb.connect(src,ws,wd,dst)
        self.tb.run ()
        # check data
        output = dst.data()
        result_data = list()
        for i in range(8):
        	if i%2==0:
        		result_data.append(output[i].real)
        	else:
        		result_data.append(output[i].imag*1j)
        for i in range(8):
        	if i%2==0:
        		result_data.append(output[i+8].imag*1j)
        	else:
        		result_data.append(output[i+8].real)
        # print result_data
        self.assertComplexTuplesAlmostEqual(tuple(expected_result),tuple(result_data),6)

    def test_004_t(self):
        M = int(math.pow(2,7))
        num = int(math.pow(2,15))
        src_data = list()
        for i in range(M*num):
            src_data.extend([int(random.random()*10), int(random.random()*10)*1j])
        expected_result = src_data
        src = blocks.vector_source_c(src_data, vlen=M)
        ws = ofdm.fbmc_weighted_spreading_vcvc(M=M,K=4)
        wd = ofdm.fbmc_weighted_despreading_vcvc(M=M,K=4)
        dst = blocks.vector_sink_c(vlen=M)
        self.tb.connect(src,ws,wd,dst)
        self.tb.run ()
        # check data
        output = dst.data()
        result_data = list()
        for k in range(num*2):
            for i in range(M):
                if i%2==0:
                    result_data.append(output[i+k*M].real)
                else:
                    result_data.append(output[i+k*M].imag*1j)

        self.assertComplexTuplesAlmostEqual(tuple(expected_result),tuple(result_data),6)


if __name__ == '__main__':
    gr_unittest.run(qa_fbmc_weighted_despreading_vcvc, "qa_fbmc_weighted_despreading_vcvc.xml")
