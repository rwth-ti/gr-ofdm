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
from fbmc_overlapping_serial_to_parallel_cvc import fbmc_overlapping_serial_to_parallel_cvc

import random

class qa_fbmc_overlapping_serial_to_parallel_cvc (gr_unittest.TestCase):

    def setUp (self):
        self.tb = gr.top_block ()

    def tearDown (self):
        self.tb = None

    def test_001_t (self):
        M = 2**10
        num = 2**10
        src_data = list()
        for i in range(M*num):
            src_data.append(int(random.random()*10))
        expected_result = list()
        expected_result.extend(src_data[0:M/2])
        for i in range(1,num*2):
            expected_result.extend(src_data[(M*i/2):(M*i/2+M/2)]*2)
        expected_result.extend([0]*(M/2))
        # src_data.extend([0]*(M/2))

        src = blocks.vector_source_c(src_data, vlen=1)
        stp = fbmc_overlapping_serial_to_parallel_cvc(M=M)
        dst = blocks.vector_sink_c(vlen=M)
        self.tb.connect(src,stp,dst)
        self.tb.run ()
        # check data
        result_data = dst.data()
        for i in range(len(expected_result)):
        	s = str(i)
        	if i<len(src_data):
        		s=s+"\t"+str(src_data[i])
        	else:
        		s=s+"\t"+"-"
        	s=s+"\t"+str(expected_result[i])        	
    		if i<len(result_data):
    			s=s+"\t"+str(result_data[i])
    		# else:
    		# 	s=s+"\t"+"-"
			# print s
        # for i in range(len(result_data)):
        # 	print str(i)+"\t"+str(expected_result[i])+"\t"+str(result_data[i])        	
        # print "src:"
        # print src_data
        # print "exp:"
        # print expected_result
        # print "res:"
        # print result_data
        # self.assertComplexTuplesAlmostEqual(tuple(expected_result),result_data,6)
        self.assertComplexTuplesAlmostEqual(tuple(expected_result[0:M*num*2-M]),result_data,6)


if __name__ == '__main__':
    gr_unittest.run(qa_fbmc_overlapping_serial_to_parallel_cvc, "qa_fbmc_overlapping_serial_to_parallel_cvc.xml")
