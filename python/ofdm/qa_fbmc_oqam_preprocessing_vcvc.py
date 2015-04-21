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

class qa_fbmc_oqam_preprocessing_vcvc (gr_unittest.TestCase):

    def setUp (self):
        self.tb = gr.top_block ()

    def tearDown (self):
        self.tb = None

    def test_001_t (self):
        # set up fg
        src_data = (1+1j,1-1j,-1-1j,-1+1j,1-1j,-1-1j,1+1j,-1+1j)
        expected_result = (1,-1j,1,-1j,1j,-1,1j,-1,-1,1j,1,1j,1j,-1,1j,1)
        src = blocks.vector_source_c(src_data,vlen=4)
        oqam = ofdm.fbmc_oqam_preprocessing_vcvc(4,0,0)
        dst = blocks.vector_sink_c(vlen=4)
        self.tb.connect(src,oqam,dst)
        self.tb.run ()
        # check data
        result_data=dst.data()
        self.assertEqual(expected_result,result_data)

    def test_002_t (self):
        # set up fg
        src_data =  (1+1j,1+1j,-1+1j,1-1j,-1+1j,-1-1j,1+1j,1-1j,-1-1j,-1+1j,1-1j,1-1j,-1-1j,1+1j,-1+1j,1+1j)
        expected_result = (1,1j,1,1j,-1,-1j,-1,1j,1j,-1,-1j,1,1j,1,-1j,1,1,-1j,1,-1j,1,-1j,-1,1j,1j,-1,-1j,-1,1j,1,1j,-1)
        src = blocks.vector_source_c(src_data,vlen=8)
        oqam = ofdm.fbmc_oqam_preprocessing_vcvc(8,0,0)
        dst = blocks.vector_sink_c(vlen=8)
        self.tb.connect(src,oqam,dst)
        self.tb.run ()
        # check data
        result_data=dst.data()
        self.assertEqual(expected_result,result_data)

    def test_003_t (self):
        # set up fg
        src_data = (1+1j,1-1j,-1-1j,-1+1j,1-1j,-1-1j,1+1j,-1+1j)
        expected_result = (1,-1j,-1,1j,1j,1,-1j,-1,1,-1j,1,1j,-1j,-1,1j,-1)
        src = blocks.vector_source_c(src_data,vlen=4)
        oqam = ofdm.fbmc_oqam_preprocessing_vcvc(M=4,offset=0,theta_sel=1)
        dst = blocks.vector_sink_c(vlen=4)
        self.tb.connect(src,oqam,dst)
        self.tb.run ()
        # check data
        result_data=dst.data()
        self.assertEqual(expected_result,result_data)

#     def test_004_t(self):
#         M= 2**7
#         num= 2**15
#         src_data = list()
#         expected_result =[None]*num*2*M
#         e = 0 #exp.res. index
#         for i in range(M*num):
#             k = i%M
#             n = 2*int(i/M)
#             re = int(random.random()*10)+1
#             im = int(random.random()*10)+1
#             src_data.append(re+im*1j)
#             if k%2 == 0:
#                 expected_result[e] = re * (1j**(k+n))
#                 expected_result[e+M] = im * (1j**(k+n+1))
#             else:
#                 expected_result[e] = im * (1j**(k+n))
#                 expected_result[e+M] = re * (1j**(k+n+1))
#             e = e+1
#             if k==M-1:
#                 e = e+M
#         src = blocks.vector_source_c(src_data,vlen=M)
#         oqam = ofdm.fbmc_oqam_preprocessing_vcvc(M=M,offset=0,theta_sel=0)
#         dst = blocks.vector_sink_c(vlen=M)
#         self.tb.connect(src,oqam,dst)
#         self.tb.run ()
#         # check data
#         result_data=dst.data()
#         # print "src:"
#         # print src_data
#         # print "exp:"
#         # print expected_result
#         # print "res:"
#         # print result_data
#         self.assertComplexTuplesAlmostEqual(tuple(expected_result),tuple(result_data),5)


if __name__ == '__main__':
    gr_unittest.run(qa_fbmc_oqam_preprocessing_vcvc, "qa_fbmc_oqam_preprocessing_vcvc.xml")
