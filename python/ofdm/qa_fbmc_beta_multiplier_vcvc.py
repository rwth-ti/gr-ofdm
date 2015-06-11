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
import math

class qa_fbmc_beta_multiplier_vcvc (gr_unittest.TestCase):

    def setUp (self):
        self.tb = gr.top_block ()

    def tearDown (self):
        self.tb = None

    def test_001_t (self):
        # set up fg
        src_data = (1,2,3,4,5,6,7,8)
        expected_result =(1,2,3,4,5,-6,7,-8)
        src= blocks.vector_source_c(src_data,vlen=4)
        bet= ofdm.fbmc_beta_multiplier_vcvc(M=4,K=4,lp=15,offset=0)
        dst= blocks.vector_sink_c(vlen=4)
        self.tb.connect(src,bet,dst)
        self.tb.run ()
        # check data
        result_data = dst.data()
        self.assertEqual(expected_result,result_data)

    def test_002_t (self):
        M=128
        num_elements = pow(2,16)
        src_data = list()
        expected_result = list()
        vector = 0
        for i in range(num_elements):
            src_data.append(int(random.random()*10)+1)
            if vector%2==0:
                #even vector all multiplied by 1
                expected_result.append(src_data[i])
            else:
                if i%2==0:
                    expected_result.append(src_data[i])
                else:
                    expected_result.append(-1*src_data[i])
            if i%M==M-1:
                vector = vector+1

        

        src = blocks.vector_source_c(src_data,vlen=M)
        bet = ofdm.fbmc_beta_multiplier_vcvc(M=M,K=4,lp=15,offset=0)
        dst = blocks.vector_sink_c(vlen=M)
        self.tb.connect(src,bet,dst)
        self.tb.run()
        result_data = dst.data()
        # while vector>0:
        #     self.assertEqual(tuple(expected_result[num_elements-M*vector:num_elements-1]),tuple(result_data[num_elements-M*vector:num_elements-1]))
        #     vector = vector -1
        # counter = 0
        # print "\nsample\tvector\tv.ind\texpect\tresult"
        # for i in range(8176-M*2,8192):
        #     print str(i)+"\t"+str(math.floor(i/M))+"\t"+str(counter)+"\t"+str(expected_result[i])+"\t"+str(result_data[i])
        #     counter=(counter+1)%16
        for i in range(vector):
            # print str(i*M)+":"+str(i*M+M)
            self.assertComplexTuplesAlmostEqual(tuple(expected_result[i*M:i*M+M]),tuple(result_data[i*M:i*M+M]),6)


if __name__ == '__main__':
    gr_unittest.run(qa_fbmc_beta_multiplier_vcvc, "qa_fbmc_beta_multiplier_vcvc.xml")
