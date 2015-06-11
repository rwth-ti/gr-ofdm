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

class qa_fbmc_asymmetrical_vector_padding_vcvc (gr_unittest.TestCase):

	def setUp (self):
		self.tb = gr.top_block ()

	def tearDown (self):
		self.tb = None

	def test_001_t (self):
		# set up fg
		M = 2**7
		num = 2**10
		indices = tuple(range(24,101)) #30:100
		# print(indices)
		src_data = list()
		expected_result = list()
		for i in range(M*num):
			# print(str(i)+"\t"+"out")
			if (i%M) in indices:
				temp = int(random.random()*10)+1
				src_data.append(temp)
				expected_result.append(temp)
				# print(str(i)+"\t"+"in")
			else:
				expected_result.append(0)

		#print(src_data)
		# print(expected_result)

		src = blocks.vector_source_c(src_data,vlen=len(indices))
		avp = ofdm.fbmc_asymmetrical_vector_padding_vcvc(indices[0],indices[len(indices)-1],M,-1)
		dst = blocks.vector_sink_c(vlen=M)

		self.tb.connect(src,avp,dst)

		self.tb.run ()
		# check data
		result_data = dst.data()
		self.assertComplexTuplesAlmostEqual(tuple(expected_result),tuple(result_data),5)


if __name__ == '__main__':
	gr_unittest.run(qa_fbmc_asymmetrical_vector_padding_vcvc, "qa_fbmc_asymmetrical_vector_padding_vcvc.xml")
