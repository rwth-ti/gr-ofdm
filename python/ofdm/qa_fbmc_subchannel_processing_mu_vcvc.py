#!/usr/bin/env python
# -*- coding: utf-8 -*-
# 
# Copyright 2015 <+YOU OR YOUR COMPANY+>.
# 
# This is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 3
# or (at your option)
# any later version.
# 
# This software is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
# 
# You should have received a copy of the GNU General Public License
# along with this software; see the file COPYING.  If not write to
# the Free Software Foundation Inc. 51 Franklin Street,
# Boston MA 02110-1301 USA.
# 

from gnuradio import gr, gr_unittest
from gnuradio import blocks

import ofdm_swig as ofdm
from fbmc_insert_preamble_mu_vcvc import fbmc_insert_preamble_mu_vcvc
from fbmc_remove_preamble_vcvc import fbmc_remove_preamble_vcvc

import random
import math
import scipy.io

class qa_fbmc_subchannel_processing_mu_vcvc (gr_unittest.TestCase):

    def setUp (self):
        self.tb = gr.top_block ()

    def tearDown (self):
        self.tb = None

    def test_001_t (self):
        # set up fg
        M = 16
        syms_per_frame = 20
        num_frame = int(math.pow(2,10))
        indices = [3,6,10,14] # num_users = 2
        sel_preamble = 1 # triple repetition preamble
        zero_pads = 4
        extra_pad = 1
        sel_eq = 0 # one tap equalizer

        # prepare test data containers
        src_data = list()
        expected_result1 = list()   # expected res for user 1
        expected_result2 = list()   # expected res for user 2
        preamble = list()
        

        # prepare preamble
        if sel_preamble == 0: # standard one vector center preamble [1,-j,-1,j]
            center_preamble = [0, 0, 0, 1j,1, -1j, -1, 0,0, 0, -1, 1j,1, -1j, -1, 0]
        elif sel_preamble == 1: # standard preamble with triple repetition
            tmp = [0, 0, 0, 1j,1, -1j, -1, 0,0, 0, -1, 1j,1, -1j, -1, 0]
            center_preamble = tmp*3 #[1/math.sqrt(3), -1j/math.sqrt(3), -1/math.sqrt(3), 1j/math.sqrt(3)]*((int)(M/4))*3
        elif sel_preamble ==2: # IAM-R preamble [1, -1,-1, 1]
            center_preamble = [0, 0, 0, 1, 1, -1, -1, 0, 0, 0, -1, 1,1, -1, -1, 0]
        else: # standard one vector center preamble [1,-j,-1,j]
            center_preamble = [0, 0, 0, 1j,1, -1j, -1, 0,0, 0, -1, 1j,1, -1j, -1, 0]

        preamble.extend([0]*zero_pads*M)
        preamble.extend(center_preamble)
        preamble.extend([0]*zero_pads*M)
        if extra_pad:
            preamble.extend([0]*M)

        # print len(preamble)

        # prepare test data
        for k in range(num_frame):
            # each frame will be multiplied by a random factor.
            factor = int(random.random()*10)+1
            tmp = [x*factor for x in preamble]
            src_data.extend(tmp)    # preamble is prepended.
            for l in range(2*syms_per_frame*M):
                if (l%M<3) or (l%M>14) or (l%M>6 and l%M<10):
                    src_data.extend([0])
                elif ((l%M>=3) and (l%M<=6)):
                    #belong to user1
                    data = int((random.random()*10+1)*abs(center_preamble[l%M]))
                    expected_result1.append(data)
                    src_data.append(data*factor)
                else:
                    # belong to user2
                    data = int((random.random()*10+1)*abs(center_preamble[l%M]))
                    expected_result2.append(data)
                    src_data.append(data*factor)

        # print "src:"
        # for k in range((syms_per_frame*2+len(preamble)/M)*num_frame):
        #     print src_data[k*M:(k+1)*M]
        # print str(len(src_data)-len(preamble)*num_frame)


        src = blocks.vector_source_c(src_data,vlen=M)
        scp = ofdm.fbmc_subchannel_processing_mu_vcvc(M=M,syms_per_frame=syms_per_frame,indices=indices,sel_preamble=sel_preamble,zero_pads=zero_pads,extra_pad=extra_pad,sel_eq=sel_eq)
        rem = fbmc_remove_preamble_vcvc(M, syms_per_frame, sel_preamble, zero_pads, extra_pad)
        avm1 = ofdm.fbmc_asymmetrical_vector_mask_vcvc(M,3,6)
        avm2 = ofdm.fbmc_asymmetrical_vector_mask_vcvc(M,10,14)
        dst1 = blocks.vector_sink_c(vlen=4)
        dst2 = blocks.vector_sink_c(vlen=5)
        dst99 = blocks.vector_sink_c(vlen=M)
        self.tb.connect((src,0),(scp,0))
        self.tb.connect((scp,0),(rem,0))
        self.tb.connect((rem,0),avm1)
        self.tb.connect((rem,0),avm2)
        self.tb.connect((avm1,0),dst1)
        self.tb.connect((avm2,0),dst2)

        # estimation probe is connected to dst99
        self.tb.connect((scp,1),dst99)
        self.tb.run ()
        # check data
        result_data1 = dst1.data()
        result_data2 = dst2.data()

        result_data99 = dst99.data()

        # print "res:"
        # for k in range(syms_per_frame*2*num_frame):
        #     print result_data1[k*4:(k+1)*4]

        # print "res99:"
        # for k in range(syms_per_frame*2*num_frame):
        #     print result_data99[k*M:(k+1)*M]
        # for i in range(len(result_data2)):
        #     print str(i)+"\t"+str(result_data2[i])
        # print result_data
        self.assertComplexTuplesAlmostEqual(expected_result1,result_data1,6)
        self.assertComplexTuplesAlmostEqual(expected_result2,result_data2,6)

    def test_002_t(self):
        # set up fg
        M = 16
        syms_per_frame = 20
        num_frame = int(math.pow(2,10))
        indices = [3,6,10,14] # num_users = 2
        sel_preamble = 0 # standard one-vector preamble
        zero_pads = 1
        extra_pad = 0
        sel_eq = 0 # one tap equalizer

        # prepare test data containers
        src_data = list()
        expected_result1 = list()   # expected res for user 1
        expected_result2 = list()   # expected res for user 2
        preamble = list()
        

        # prepare preamble
        if sel_preamble == 0: # standard one vector center preamble [1,-j,-1,j]
            center_preamble = [0, 0, 0, 1j,1, -1j, -1, 0,0, 0, -1, 1j,1, -1j, -1, 0]
        elif sel_preamble == 1: # standard preamble with triple repetition
            tmp = [0, 0, 0, 1j,1, -1j, -1, 0,0, 0, -1, 1j,1, -1j, -1, 0]
            center_preamble = tmp*3 #[1/math.sqrt(3), -1j/math.sqrt(3), -1/math.sqrt(3), 1j/math.sqrt(3)]*((int)(M/4))*3
        elif sel_preamble ==2: # IAM-R preamble [1, -1,-1, 1]
            center_preamble = [0, 0, 0, 1, 1, -1, -1, 0, 0, 0, -1, 1,1, -1, -1, 0]
        else: # standard one vector center preamble [1,-j,-1,j]
            center_preamble = [0, 0, 0, 1j,1, -1j, -1, 0,0, 0, -1, 1j,1, -1j, -1, 0]

        preamble.extend([0]*zero_pads*M)
        preamble.extend(center_preamble)
        preamble.extend([0]*zero_pads*M)
        if extra_pad:
            preamble.extend([0]*M)

        # print len(preamble)

        # prepare test data
        for k in range(num_frame):
            # each frame will be multiplied by a random factor.
            factor = int(random.random()*10)+1
            tmp = [x*factor for x in preamble]
            src_data.extend(tmp)    # preamble is prepended.
            for l in range(2*syms_per_frame*M):
                if (l%M<3) or (l%M>14) or (l%M>6 and l%M<10):
                    src_data.extend([0])
                elif ((l%M>=3) and (l%M<=6)):
                    #belong to user1
                    data = int((random.random()*10+1)*abs(center_preamble[l%M]))
                    expected_result1.append(data)
                    src_data.append(data*factor)
                else:
                    # belong to user2
                    data = int((random.random()*10+1)*abs(center_preamble[l%M]))
                    expected_result2.append(data)
                    src_data.append(data*factor)

        # print "src:"
        # for k in range((syms_per_frame*2+len(preamble)/M)*num_frame):
        #     print src_data[k*M:(k+1)*M]
        # # print str(len(src_data)-len(preamble)*num_frame)


        src = blocks.vector_source_c(src_data,vlen=M)
        scp = ofdm.fbmc_subchannel_processing_mu_vcvc(M=M,syms_per_frame=syms_per_frame,indices=indices,sel_preamble=sel_preamble,zero_pads=zero_pads,extra_pad=extra_pad,sel_eq=sel_eq)
        rem = fbmc_remove_preamble_vcvc(M, syms_per_frame, sel_preamble, zero_pads, extra_pad)
        avm1 = ofdm.fbmc_asymmetrical_vector_mask_vcvc(M,3,6)
        avm2 = ofdm.fbmc_asymmetrical_vector_mask_vcvc(M,10,14)
        dst1 = blocks.vector_sink_c(vlen=4)
        dst2 = blocks.vector_sink_c(vlen=5)
        dst99 = blocks.vector_sink_c(vlen=M)
        self.tb.connect((src,0),(scp,0))
        self.tb.connect((scp,0),(rem,0))
        self.tb.connect((rem,0),avm1)
        self.tb.connect((rem,0),avm2)
        self.tb.connect((avm1,0),dst1)
        self.tb.connect((avm2,0),dst2)

        # estimation probe is connected to dst99
        self.tb.connect((scp,1),dst99)
        self.tb.run ()
        # check data
        result_data1 = dst1.data()
        result_data2 = dst2.data()

        result_data99 = dst99.data()

        # print "res:"
        # for k in range(syms_per_frame*2*num_frame):
        #     print result_data1[k*4:(k+1)*4]

        # print "res99:"
        # for k in range(syms_per_frame*2*num_frame):
        #     print result_data99[k*M:(k+1)*M]
        # for i in range(len(result_data2)):
        #     print str(i)+"\t"+str(result_data2[i])
        # print result_data
        self.assertComplexTuplesAlmostEqual(expected_result1,result_data1,6)
        self.assertComplexTuplesAlmostEqual(expected_result2,result_data2,6)

    def test_003_t(self):
        # set up fg
        M = 16
        syms_per_frame = 20
        num_frame = int(math.pow(2,10))
        indices = [3,6,10,14] # num_users = 2
        sel_preamble = 1
        zero_pads = 2
        extra_pad = 0
        sel_eq = 4  #no eq

        # prepare test data containers
        src_data = list()
        expected_result = list()
        preamble = list()
        

        # prepare preamble
        if sel_preamble == 0: # standard one vector center preamble [1,-j,-1,j]
            center_preamble = [0, 0, 0, 1j,1, -1j, -1, 0,0, 0, -1, 1j,1, -1j, -1, 0]
        elif sel_preamble == 1: # standard preamble with triple repetition
            tmp = [0, 0, 0, 1j,1, -1j, -1, 0,0, 0, -1, 1j,1, -1j, -1, 0]
            center_preamble = tmp*3 #[1/math.sqrt(3), -1j/math.sqrt(3), -1/math.sqrt(3), 1j/math.sqrt(3)]*((int)(M/4))*3
        elif sel_preamble ==2: # IAM-R preamble [1, -1,-1, 1]
            center_preamble = [0, 0, 0, 1, 1, -1, -1, 0, 0, 0, -1, 1,1, -1, -1, 0]
        else: # standard one vector center preamble [1,-j,-1,j]
            center_preamble = [0, 0, 0, 1j,1, -1j, -1, 0,0, 0, -1, 1j,1, -1j, -1, 0]

        preamble.extend([0]*zero_pads*M)
        preamble.extend(center_preamble)
        preamble.extend([0]*zero_pads*M)
        if extra_pad:
            preamble.extend([0]*M)

        # print len(preamble)

        # prepare test data
        for k in range(num_frame):
            # each frame will be multiplied by a random factor.
            factor = int(random.random()*10)+1
            tmp = [x*factor for x in preamble]
            src_data.extend(tmp)
            for l in range(2*syms_per_frame*M):
                if (l%M<3) or (l%M>14) or (l%M>6 and l%M<10):
                    data = 0
                else:
                    data = int((random.random()*10+1)*abs(center_preamble[l%M]))
                expected_result.append(data*factor)
                src_data.append(data*factor)

        # print "exp:"
        # for k in range(syms_per_frame*2*num_frame):
        #     print expected_result[k*M:(k+1)*M]

        # print "src:"
        # for k in range((syms_per_frame*2+len(preamble)/M)*num_frame):
        #     print src_data[k*M:(k+1)*M]
        # # print str(len(src_data)-len(preamble)*num_frame)


        src = blocks.vector_source_c(src_data,vlen=M)
        scp = ofdm.fbmc_subchannel_processing_mu_vcvc(M=M,syms_per_frame=syms_per_frame,indices=indices,sel_preamble=sel_preamble,zero_pads=zero_pads,extra_pad=extra_pad,sel_eq=sel_eq)
        rem = fbmc_remove_preamble_vcvc(M, syms_per_frame, sel_preamble, zero_pads, extra_pad)
        dst = blocks.vector_sink_c(vlen=M)
        dst2 = blocks.vector_sink_c(vlen=M)
        self.tb.connect((src,0),(scp,0))
        self.tb.connect((scp,0),(rem,0))
        self.tb.connect((rem,0),dst)
        self.tb.connect((scp,1),dst2)
        self.tb.run ()
        # check data
        result_data = dst.data()
        result_data2 = dst2.data()

        # print "res:"
        # for k in range(syms_per_frame*2*num_frame):
        #     print result_data[k*M:(k+1)*M]
        # for i in range(len(result_data2)):
        #     print str(i)+"\t"+str(result_data2[i])
        # print result_data
        self.assertComplexTuplesAlmostEqual(expected_result,result_data,6)

    def test_004_t(self):
        # set up fg
        M = 16
        syms_per_frame = 20
        num_frame = int(math.pow(2,10))
        indices = [3,6,10,14] # num_users = 2
        sel_preamble = 1 # standard one-vector preamble
        zero_pads = 4
        extra_pad = 1
        sel_eq = 1 # three-tap equalizer

        # prepare test data containers
        src_data = list()
        expected_result1 = list()   # expected res for user 1
        expected_result2 = list()   # expected res for user 2
        preamble = list()
        

        # prepare preamble
        if sel_preamble == 0: # standard one vector center preamble [1,-j,-1,j]
            center_preamble = [0, 0, -1, 1j,1, -1j, -1, 1j,0, -1j, -1, 1j,1, -1j, -1, 1j]
        elif sel_preamble == 1: # standard preamble with triple repetition
            tmp = [0, 0, -1, 1j,1, -1j, -1, 1j,0, -1j, -1, 1j,1, -1j, -1, 1j]
            center_preamble = tmp*3 #[1/math.sqrt(3), -1j/math.sqrt(3), -1/math.sqrt(3), 1j/math.sqrt(3)]*((int)(M/4))*3
        elif sel_preamble ==2: # IAM-R preamble [1, -1,-1, 1]
            center_preamble = [0, 0, -1, 1, 1, -1, -1, 1, 0, 0, -1, 1,1, -1, -1, 1]
        else: # standard one vector center preamble [1,-j,-1,j]
            center_preamble = [0, 0, -1, 1j,1, -1j, -1, 1j,0, -1j, -1, 1j,1, -1j, -1, 1j]

        preamble.extend([0]*zero_pads*M)
        preamble.extend(center_preamble)
        preamble.extend([0]*zero_pads*M)
        if extra_pad:
            preamble.extend([0]*M)

        # print len(preamble)

        # prepare test data
        for k in range(num_frame):
            # each frame will be multiplied by a random factor.
            factor = int(random.random()*10)+1
            tmp = [x*factor for x in preamble]
            src_data.extend(tmp)    # preamble is prepended.
            for l in range(2*syms_per_frame*M):
                if (l%M<3) or (l%M>14) or (l%M>6 and l%M<10):
                    src_data.extend([0])
                elif ((l%M>=3) and (l%M<=6)):
                    #belong to user1
                    data = int((random.random()*10+1)*abs(center_preamble[l%M]))
                    expected_result1.append(data)
                    src_data.append(data*factor)
                else:
                    # belong to user2
                    data = int((random.random()*10+1)*abs(center_preamble[l%M]))
                    expected_result2.append(data)
                    src_data.append(data*factor)

        src_data.extend([0]*M) # we add this in order to feed the system with samples till the last relevant sample is acquired.

        # print "src:"
        # for k in range((syms_per_frame*2+len(preamble)/M)*num_frame):
        #     print src_data[k*M:(k+1)*M]
        # # print str(len(src_data)-len(preamble)*num_frame)


        src = blocks.vector_source_c(src_data,vlen=M)
        scp = ofdm.fbmc_subchannel_processing_mu_vcvc(M=M,syms_per_frame=syms_per_frame,indices=indices,sel_preamble=sel_preamble,zero_pads=zero_pads,extra_pad=extra_pad,sel_eq=sel_eq)
        skh = blocks.skiphead(gr.sizeof_gr_complex*M, 1)
        rem = fbmc_remove_preamble_vcvc(M, syms_per_frame, sel_preamble, zero_pads, extra_pad)
        avm1 = ofdm.fbmc_asymmetrical_vector_mask_vcvc(M,3,6)
        avm2 = ofdm.fbmc_asymmetrical_vector_mask_vcvc(M,10,14)
        dst1 = blocks.vector_sink_c(vlen=4)
        dst2 = blocks.vector_sink_c(vlen=5)
        dst99 = blocks.vector_sink_c(vlen=M)

        self.tb.connect((src,0),(scp,0))
        self.tb.connect((scp,0),(skh,0))
        self.tb.connect((skh,0),(rem,0))
        self.tb.connect((rem,0),avm1)
        self.tb.connect((rem,0),avm2)
        self.tb.connect((avm1,0),dst1)
        self.tb.connect((avm2,0),dst2)

        # estimation probe is connected to dst99
        self.tb.connect((scp,1),dst99)
        self.tb.run ()
        # check data
        result_data1 = dst1.data()
        result_data2 = dst2.data()

        result_data99 = dst99.data()

        # print "res:"
        # for k in range(syms_per_frame*2*num_frame):
        #     print result_data1[k*4:(k+1)*4]

        # print "res99:"
        # for k in range(syms_per_frame*2*num_frame):
        #     print result_data99[k*M:(k+1)*M]
        # for i in range(len(result_data2)):
        #     print str(i)+"\t"+str(result_data2[i])
        # print result_data
        self.assertComplexTuplesAlmostEqual(expected_result1,result_data1,6)
        self.assertComplexTuplesAlmostEqual(expected_result2,result_data2,6)
if __name__ == '__main__':
    gr_unittest.run(qa_fbmc_subchannel_processing_mu_vcvc, "qa_fbmc_subchannel_processing_mu_vcvc.xml")
