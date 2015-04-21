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

class qa_fbmc_oqam_postprocessing_vcvc (gr_unittest.TestCase):

	def setUp (self):
		self.tb = gr.top_block ()

	def tearDown (self):
		self.tb = None

	def test_001_t (self):
		# set up fg
		src_data = (1,0,0,1j,1j,-2,-3j,4,-2,8j,-6,5j,-9j,-4,2j,0)
		expected_result = (1+1j,2,3j,4-1j,2+9j,-8j-4,-6+2j,5j)
		src = blocks.vector_source_c(src_data,vlen=4)
		post = ofdm.fbmc_oqam_postprocessing_vcvc(M=4, offset=0, theta_sel=0)
		dst = blocks.vector_sink_c(vlen=4)
		self.tb.connect(src,post,dst)
		self.tb.run ()
		# check data
		result_data = dst.data()
		# print snk1.data()
		self.assertEqual(expected_result,result_data)

	def test_002_t (self):
		# set up fg
		src_data = (1+1j,2+2j,3-3j,4-4j,5+5j,-6-6j,-7+7j,8+8j)
		expected_result = src_data
		src = blocks.vector_source_c(src_data,vlen=4)
		# snk1 = blocks.vector_sink_c(vlen=4)
		pre = ofdm.fbmc_oqam_preprocessing_vcvc(M=4,offset=0, theta_sel=0)
		post = ofdm.fbmc_oqam_postprocessing_vcvc(M=4, offset=0, theta_sel=0)
		dst = blocks.vector_sink_c(vlen=4)
		self.tb.connect(src,pre,post,dst)
		# self.tb.connect(pre,snk1)
		self.tb.run ()
		# check data
		result_data = dst.data()
		# print snk1.data()
		self.assertEqual(expected_result,result_data)

	def test_003_t (self):
		# set up fg
		src_data = (1+1j,2+2j,3-3j,4-4j,5+5j,-6-6j,-7+7j,8+8j,9-9j,10+10j,-11+11j,1.2-1.2j,-1.3+1.3j,1.4-14j,-15-15j,16-16j)
		expected_result = src_data
		src = blocks.vector_source_c(src_data,vlen=16)
		# snk1 = blocks.vector_sink_c(vlen=4)
		pre = ofdm.fbmc_oqam_preprocessing_vcvc(M=16,offset=0, theta_sel=0)
		post = ofdm.fbmc_oqam_postprocessing_vcvc(M=16, offset=0, theta_sel=0)
		dst = blocks.vector_sink_c(vlen=16)
		self.tb.connect(src,pre,post,dst)
		# self.tb.connect(pre,snk1)
		self.tb.run ()
		# check data
		result_data = dst.data()
		# print snk1.data()
		self.assertComplexTuplesAlmostEqual(expected_result,result_data,7)

	def test_004_t (self):
		# set up fg
		src_data = (1+1j,2+2j,3-3j,4-4j,5+5j,-6-6j,-7+7j,8+8j)
		expected_result = src_data
		src = blocks.vector_source_c(src_data,vlen=4)
		# snk1 = blocks.vector_sink_c(vlen=4)
		pre = ofdm.fbmc_oqam_preprocessing_vcvc(M=4,offset=0, theta_sel=1)
		post = ofdm.fbmc_oqam_postprocessing_vcvc(M=4, offset=0, theta_sel=1)
		dst = blocks.vector_sink_c(vlen=4)
		self.tb.connect(src,pre,post,dst)
		# self.tb.connect(pre,snk1)
		self.tb.run ()
		# check data
		result_data = dst.data()
		# print snk1.data()
		self.assertEqual(expected_result,result_data)
 
	def test_005_t (self):
		# set up fg
		src_data = (1+1j,2+2j,3-3j,4-4j,5+5j,-6-6j,-7+7j,8+8j,9-9j,10+10j,-11+11j,1.2-1.2j,-1.3+1.3j,1.4-14j,-15-15j,16-16j)
		expected_result = src_data
		src = blocks.vector_source_c(src_data,vlen=16)
		# snk1 = blocks.vector_sink_c(vlen=4)
		pre = ofdm.fbmc_oqam_preprocessing_vcvc(M=16,offset=0, theta_sel=1)
		post = ofdm.fbmc_oqam_postprocessing_vcvc(M=16, offset=0, theta_sel=1)
		dst = blocks.vector_sink_c(vlen=16)
		self.tb.connect(src,pre,post,dst)
		# self.tb.connect(pre,snk1)
		self.tb.run ()
		# check data
		result_data = dst.data()
		# print snk1.data()
		self.assertComplexTuplesAlmostEqual(expected_result,result_data,7)
 
	def test_006_t(self):
		M = 2**7
		num = 2**15
		src_data = list()
		for i in range(num*M):
			src_data.append(int(random.random()*10)+1+(int(random.random()*10)+1)*1j)
		src = blocks.vector_source_c(src_data,vlen=M)
		# snk1 = blocks.vector_sink_c(vlen=4)
		pre = ofdm.fbmc_oqam_preprocessing_vcvc(M=M,offset=0, theta_sel=0)
		post = ofdm.fbmc_oqam_postprocessing_vcvc(M=M, offset=0, theta_sel=0)
		dst = blocks.vector_sink_c(vlen=M)
		self.tb.connect(src,pre,post,dst)
		# self.tb.connect(pre,snk1)
		self.tb.run ()
		# check data
		result_data = dst.data()
		print result_data==tuple(src_data)
# 		list1 = []
# 		list2 = []
# 		for i in range(0,2000000):#,len(result_data)):
# 			if result_data[i] != src_data[i]:
# 				list1.append(result_data[i])
# 			else:
# 				list2.append(src_data[i])
#  				
# 		print len(list1)
# 		print len(list2)
				
		self.assertComplexTuplesAlmostEqual(tuple(src_data),result_data,7)


if __name__ == '__main__':
    gr_unittest.run(qa_fbmc_oqam_postprocessing_vcvc, "qa_fbmc_oqam_postprocessing_vcvc.xml")
