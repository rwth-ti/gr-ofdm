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
from fbmc_remove_preamble_vcvc import fbmc_remove_preamble_vcvc
from fbmc_insert_preamble_mu_vcvc import fbmc_insert_preamble_mu_vcvc

import math
import random

class qa_fbmc_insert_preamble_mu_vcvc (gr_unittest.TestCase):

    def setUp (self):
        self.tb = gr.top_block ()

    def tearDown (self):
        self.tb = None

    def test_001_t (self):
        M = 256
        syms_per_frame = 4
        num_frame = int(math.pow(2,10))
        start = 4
        end = 11
        zero_pads = 3
        extra_pad = True
        sel_preamble = 1
        # preamble = [0]*M*zero_pads+[0]*4+[1, -1j, -1, 1j]*3+[0]*(M-end-1)+[0]*M*zero_pads
        if sel_preamble == 0: # standard one vector center preamble [1,-j,-1,j]
            preamble = [0]*M*zero_pads+[0]*4+[1, -1j, -1, 1j]*2+[0]*(M-end-1)+[0]*M*zero_pads
        elif sel_preamble == 1: # standard preamble with triple repetition
            preamble = [0]*M*zero_pads+([0]*4+[1, -1j, -1, 1j]*2+[0]*(M-end-1))*3+[0]*M*zero_pads
        elif sel_preamble ==2: # IAM-R preamble [1, -1,-1, 1]
            preamble = [0]*M*zero_pads+[0]*4+[1, -1, -1, 1]*2+[0]*(M-end-1)+[0]*M*zero_pads
        else: # standard one vector center preamble [1,-j,-1,j]
            preamble = [0]*M*zero_pads+[0]*4+[1, -1j, -1, 1j]*2+[0]*(M-end-1)+[0]*M*zero_pads

        if extra_pad:
        	preamble.extend(M*[0])

    	# for i in range(len(preamble)):
     #    	print("i= "+str(i%M)+" "+str(preamble[i]))
     #    print("end")

        src_data=list()
        expected_result = list()
        # e = 0 # exp. res index
        for i in range(num_frame):
        	expected_result.extend(preamble)
        	for k in range(M*2*syms_per_frame):
	            temp = int(random.random()*10)
	            src_data.append(temp)
	            expected_result.append(temp)



        src = blocks.vector_source_c(src_data,vlen=M)
        ipr = fbmc_insert_preamble_mu_vcvc(M=M, syms_per_frame=syms_per_frame, start=start, end=end, sel_eq=0, sel_preamble=sel_preamble, zero_pads=zero_pads, extra_pad=extra_pad)
        dst = blocks.vector_sink_c(vlen=M)
        self.tb.connect(src,ipr,dst)
        self.tb.run ()
        # check data
        result_data = dst.data()

        # print len(result_data)
        # print len(expected_result)

        # for i in range(len(result_data)):
        # 	print(str(i/M)+"-"+str(i%M)+" "+str(result_data[i])+" "+str(expected_result[i]))
        
        # print result_data
        self.assertComplexTuplesAlmostEqual(tuple(expected_result),tuple(result_data))

    def test_002_t (self):
        M = 256
        syms_per_frame = 4
        num_frame = int(math.pow(2,10))
        start = 4
        end = 10
        zero_pads = 3
        extra_pad = True
        sel_preamble = 1
        # preamble = [0]*M*zero_pads+[0]*4+[1, -1j, -1, 1j]*3+[0]*(M-end-1)+[0]*M*zero_pads
        if sel_preamble == 0: # standard one vector center preamble [1,-j,-1,j]
            preamble = [0]*M*zero_pads+[0]*4+[1, -1j, -1, 1j]+[1, -1j, -1]+[0]*(M-end-1)+[0]*M*zero_pads
        elif sel_preamble == 1: # standard preamble with triple repetition
            preamble = [0]*M*zero_pads+([0]*4+[1, -1j, -1, 1j]+[1, -1j, -1]+[0]*(M-end-1))*3+[0]*M*zero_pads
        elif sel_preamble ==2: # IAM-R preamble [1, -1,-1, 1]
            preamble = [0]*M*zero_pads+[0]*4+[1, -1, -1, 1]+4+[1, -1, -1]+[0]*(M-end-1)+[0]*M*zero_pads
        else: # standard one vector center preamble [1,-j,-1,j]
            preamble = [0]*M*zero_pads+[0]*4+[1, -1j, -1, 1j]+[1, -1j, -1]+[0]*(M-end-1)+[0]*M*zero_pads

        if extra_pad:
        	preamble.extend(M*[0])

    	# for i in range(len(preamble)):
     #    	print("i= "+str(i%M)+" "+str(preamble[i]))
     #    print("end")

        src_data=list()
        expected_result = list()
        # e = 0 # exp. res index
        for i in range(num_frame):
        	expected_result.extend(preamble)
        	for k in range(M*2*syms_per_frame):
	            temp = int(random.random()*10)
	            src_data.append(temp)
	            expected_result.append(temp)



        src = blocks.vector_source_c(src_data,vlen=M)
        ipr = fbmc_insert_preamble_mu_vcvc(M=M, syms_per_frame=syms_per_frame, start=start, end=end, sel_eq=0, sel_preamble=sel_preamble, zero_pads=zero_pads, extra_pad=extra_pad)
        dst = blocks.vector_sink_c(vlen=M)
        self.tb.connect(src,ipr,dst)
        self.tb.run ()
        # check data
        result_data = dst.data()

        # print len(result_data)
        # print len(expected_result)

        # for i in range(len(result_data)):
        # 	print(str(i/M)+"-"+str(i%M)+" "+str(result_data[i])+" "+str(expected_result[i]))
        
        # print result_data
        self.assertComplexTuplesAlmostEqual(tuple(expected_result),tuple(result_data))

    def test_003_t (self):
        M = 16
        syms_per_frame = 20
        num_frame = int(math.pow(2,10))
        start = 5
        end = 9
        zero_pads = 1
        extra_pad = False
        sel_preamble = 1
        sel_eq = 2
        # preamble = [0]*M*zero_pads+[0]*4+[1, -1j, -1, 1j]*3+[0]*(M-end-1)+[0]*M*zero_pads
        if sel_preamble == 0: # standard one vector center preamble [1,-j,-1,j]
            preamble = [0]*M*zero_pads+[0]*4+[1, -1j, -1, 1j]+[1, -1j, -1]+[0]*(M-end-1-1)+[0]*M*zero_pads
        elif sel_preamble == 1: # standard preamble with triple repetition
            preamble = [0]*M*zero_pads+([0]*4+[1, -1j, -1, 1j]+[1, -1j, -1]+[0]*(M-end-1-1))*3+[0]*M*zero_pads
        elif sel_preamble ==2: # IAM-R preamble [1, -1,-1, 1]
            preamble = [0]*M*zero_pads+[0]*4+[1, -1, -1, 1]+4+[1, -1, -1]+[0]*(M-end-1-1)+[0]*M*zero_pads
        else: # standard one vector center preamble [1,-j,-1,j]
            preamble = [0]*M*zero_pads+[0]*4+[1, -1j, -1, 1j]+[1, -1j, -1]+[0]*(M-end-1-1)+[0]*M*zero_pads

        if extra_pad:
        	preamble.extend(M*[0])

    	# for i in range(len(preamble)):
     #    	print("i= "+str(i%M)+" "+str(preamble[i]))
     #    print("end")

        src_data=list()
        expected_result = list()
        # e = 0 # exp. res index
        for i in range(num_frame):
        	expected_result.extend(preamble)
        	for k in range(M*2*syms_per_frame):
	            temp = int(random.random()*10)
	            src_data.append(temp)
	            expected_result.append(temp)



        src = blocks.vector_source_c(src_data,vlen=M)
        ipr = fbmc_insert_preamble_mu_vcvc(M=M, syms_per_frame=syms_per_frame, start=start, end=end, sel_eq=sel_eq, sel_preamble=sel_preamble, zero_pads=zero_pads, extra_pad=extra_pad)
        dst = blocks.vector_sink_c(vlen=M)
        self.tb.connect(src,ipr,dst)
        self.tb.run ()
        # check data
        result_data = dst.data()

        # print len(result_data)
        # print len(expected_result)

        # for i in range(len(result_data)):
        # 	print(str(i/M)+"-"+str(i%M)+" "+str(result_data[i])+" "+str(expected_result[i]))
        
        # print result_data
        self.assertComplexTuplesAlmostEqual(tuple(expected_result),tuple(result_data))

    def test_004_t (self):
        # just to see if when syms_per_frame=0, it is still working.
        M = 16
        syms_per_frame = 1
        num_frame = int(math.pow(2,10))
        start = 5
        end = 9
        zero_pads = 1
        extra_pad = False
        sel_preamble = 1
        sel_eq = 2
        # preamble = [0]*M*zero_pads+[0]*4+[1, -1j, -1, 1j]*3+[0]*(M-end-1)+[0]*M*zero_pads
        if sel_preamble == 0: # standard one vector center preamble [1,-j,-1,j]
            preamble = [0]*M*zero_pads+[0]*4+[1, -1j, -1, 1j]+[1, -1j, -1]+[0]*(M-end-1-1)+[0]*M*zero_pads
        elif sel_preamble == 1: # standard preamble with triple repetition
            preamble = [0]*M*zero_pads+([0]*4+[1, -1j, -1, 1j]+[1, -1j, -1]+[0]*(M-end-1-1))*3+[0]*M*zero_pads
        elif sel_preamble ==2: # IAM-R preamble [1, -1,-1, 1]
            preamble = [0]*M*zero_pads+[0]*4+[1, -1, -1, 1]+4+[1, -1, -1]+[0]*(M-end-1-1)+[0]*M*zero_pads
        else: # standard one vector center preamble [1,-j,-1,j]
            preamble = [0]*M*zero_pads+[0]*4+[1, -1j, -1, 1j]+[1, -1j, -1]+[0]*(M-end-1-1)+[0]*M*zero_pads

        if extra_pad:
            preamble.extend(M*[0])

        # for i in range(len(preamble)):
     #      print("i= "+str(i%M)+" "+str(preamble[i]))
     #    print("end")

        src_data=list()
        expected_result = list()
        # e = 0 # exp. res index
        for i in range(num_frame):
            expected_result.extend(preamble)
            for k in range(M*2*syms_per_frame):
                temp = int(random.random()*10)
                src_data.append(temp)
                expected_result.append(temp)



        src = blocks.vector_source_c(src_data,vlen=M)
        ipr = fbmc_insert_preamble_mu_vcvc(M=M, syms_per_frame=syms_per_frame, start=start, end=end, sel_eq=sel_eq, sel_preamble=sel_preamble, zero_pads=zero_pads, extra_pad=extra_pad)
        dst = blocks.vector_sink_c(vlen=M)
        self.tb.connect(src,ipr,dst)
        self.tb.run ()
        # check data
        result_data = dst.data()

        # print len(result_data)
        # print len(expected_result)

        # for i in range(len(result_data)):
        #   print(str(i/M)+"-"+str(i%M)+" "+str(result_data[i])+" "+str(expected_result[i]))
        
        # print result_data
        self.assertComplexTuplesAlmostEqual(tuple(expected_result),tuple(result_data))

    def test_005_t (self):
        # just to see if when syms_per_frame=0, it is still working.
        M = 256
        syms_per_frame = 10
        num_frame = int(math.pow(2,10))
        start = 5
        end = 9
        zero_pads = 1
        extra_pad = False
        sel_preamble = 0
        sel_eq = 2
        # preamble = [0]*M*zero_pads+[0]*4+[1, -1j, -1, 1j]*3+[0]*(M-end-1)+[0]*M*zero_pads
        if sel_preamble == 0: # standard one vector center preamble [1,-j,-1,j]
            preamble = [0]*M*zero_pads+[0]*4+[1, -1j, -1, 1j]+[1, -1j, -1]+[0]*(M-end-1-1)+[0]*M*zero_pads
        elif sel_preamble == 1: # standard preamble with triple repetition
            preamble = [0]*M*zero_pads+([0]*4+[1, -1j, -1, 1j]+[1, -1j, -1]+[0]*(M-end-1-1))*3+[0]*M*zero_pads
        elif sel_preamble ==2: # IAM-R preamble [1, -1,-1, 1]
            preamble = [0]*M*zero_pads+[0]*4+[1, -1, -1, 1]+4+[1, -1, -1]+[0]*(M-end-1-1)+[0]*M*zero_pads
        else: # standard one vector center preamble [1,-j,-1,j]
            preamble = [0]*M*zero_pads+[0]*4+[1, -1j, -1, 1j]+[1, -1j, -1]+[0]*(M-end-1-1)+[0]*M*zero_pads

        if extra_pad:
            preamble.extend(M*[0])

        # for i in range(len(preamble)):
     #      print("i= "+str(i%M)+" "+str(preamble[i]))
     #    print("end")

        src_data=list()
        expected_result = list()
        # e = 0 # exp. res index
        for i in range(num_frame):
            # expected_result.extend(preamble)
            for k in range(M*2*syms_per_frame):
                temp = int(random.random()*10)
                src_data.append(temp)
                # expected_result.append(temp)

        expected_result.extend(src_data)



        src = blocks.vector_source_c(src_data,vlen=M)
        ipr = fbmc_insert_preamble_mu_vcvc(M=M, syms_per_frame=syms_per_frame, start=start, end=end, sel_eq=sel_eq, sel_preamble=sel_preamble, zero_pads=zero_pads, extra_pad=extra_pad)
        rpr = fbmc_remove_preamble_vcvc(M, syms_per_frame, sel_preamble, zero_pads, extra_pad)
        dst = blocks.vector_sink_c(vlen=M)
        self.tb.connect(src,ipr,rpr,dst)
        self.tb.run ()
        # check data
        result_data = dst.data()
        # print result_data
        self.assertComplexTuplesAlmostEqual(tuple(expected_result),tuple(result_data))


if __name__ == '__main__':
    gr_unittest.run(qa_fbmc_insert_preamble_mu_vcvc, "qa_fbmc_insert_preamble_mu_vcvc.xml")
