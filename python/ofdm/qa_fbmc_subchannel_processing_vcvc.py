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
import scipy.io

class qa_fbmc_subchannel_processing_vcvc (gr_unittest.TestCase):

    def setUp (self):
        self.tb = gr.top_block ()

    def tearDown (self):
        self.tb = None

    def test_001_t (self):
        # set up fg
        src_data = (0,0,0,0,1,-1j,-1,1j,0,0,0,0,
        	1,1,1,1,2,2,2,2,3,3,3,3,4,4,4,4,
        	0,0,0,0,2,-2j,-2,2j,0,0,0,0,
        	2,2,2,2,4,4,4,4,6,6,6,6,8,8,8,8)
        expected_result = (0,0,0,0,1,-1j,-1,1j,0,0,0,0,
        	1,1,1,1,2,2,2,2,3,3,3,3,4,4,4,4,
        	0,0,0,0,2,-2j,-2,2j,0,0,0,0,
        	1,1,1,1,2,2,2,2,3,3,3,3,4,4,4,4)
        src = blocks.vector_source_c(src_data,vlen=4)
        scp = ofdm.fbmc_subchannel_processing_vcvc(M=4,syms_per_frame=2,preamble=[0,0,0,0,1,-1j,-1,1j,0,0,0,0],sel_eq=0)
        dst = blocks.vector_sink_c(vlen=4)
        dst2 = blocks.vector_sink_c(vlen=4)
        self.tb.connect((src,0),(scp,0))
        self.tb.connect((scp,0),dst)
        self.tb.connect((scp,1),dst2)
        self.tb.run ()
        # check data
        result_data = dst.data()
        result_data2 = dst2.data()
        for i in range(len(result_data2)):
            print str(i)+"\t"+str(result_data2[i])
        # print result_data
        self.assertComplexTuplesAlmostEqual(expected_result,result_data,6)

    def test_002_t(self):
        # set up fg
        src_data = (0,0,0,0,1,-1j,-1,1j,0,0,0,0,
        	1,1,1,1,2,2,2,2,3,3,3,3,4,4,4,4,
        	0,0,0,0,2,-2j,-2,2j,0,0,0,0,
        	2,2,2,2,4,4,4,4,6,6,6,6,8,8,8,8)
        expected_result = (0,0,0,0,1,-1j,-1,1j,0,0,0,0,
        	1,1,1,1,2,2,2,2,3,3,3,3,4,4,4,4,
        	0,0,0,0,2,-2j,-2,2j,0,0,0,0,
        	2,2,2,2,4,4,4,4,6,6,6,6,8,8,8,8)
        src = blocks.vector_source_c(src_data,vlen=4)
        scp = ofdm.fbmc_subchannel_processing_vcvc(M=4,syms_per_frame=2,preamble=[0,0,0,0,1,-1j,-1,1j,0,0,0,0],sel_eq=3)
        dst = blocks.vector_sink_c(vlen=4)
        dst2 = blocks.vector_sink_c(vlen=4)
        self.tb.connect((src,0),(scp,0))
        self.tb.connect((scp,0),dst)
        self.tb.connect((scp,1),dst2)
        self.tb.run ()
        # check data
        result_data = dst.data()
        # print result_data
        self.assertComplexTuplesAlmostEqual(expected_result,result_data,6)

    def test_003_t(self):
        # test no equalizer
        center_preamble = [1,-1j,-1,1j]
        M = 2**5
        syms_per_frame = 20
        num_frames = 2**5
        preamble = [0]*M+center_preamble*(M/4)+[0]*M
        src_data = list()
        expected_result =list()
        for i in range(2*syms_per_frame*M*num_frames):
            if i%(2*syms_per_frame*M)==0:
                src_data.extend(preamble)
                expected_result.extend(preamble)
            val = int(random.random()*10)
            src_data.append(val)
            expected_result.append(val)
        src = blocks.vector_source_c(src_data,vlen=M)
        scp = ofdm.fbmc_subchannel_processing_vcvc(M=M,syms_per_frame=syms_per_frame,preamble=preamble,sel_eq=3)
        dst = blocks.vector_sink_c(vlen=M)
        dst2 = blocks.vector_sink_c(vlen=M)
        self.tb.connect((src,0),(scp,0))
        self.tb.connect((scp,0),dst)
        self.tb.connect((scp,1),dst2)
        self.tb.run ()
        # check data
        result_data = dst.data()
        f = open('..\..\matlab\sp_python_output.txt', 'w')
        s = "i\tsrc\texp\tres\tdiff\n"
        f.write(s)
        for i in range(2*syms_per_frame*M*num_frames):
            s = str(i)+"\t"+str(src_data[i])+"\t"+str(expected_result[i])+"\t"+str(result_data[i])+"\t"+str(abs(expected_result[i]-result_data[i])>0)+"\n"
            f.write(s)
        f.close()
        # for i in range(len(result_data)):
        #     print str(i)+"\t"+str(expected_result[i])+"\t"+str(result_data[i])
        # print result_data
        self.assertComplexTuplesAlmostEqual(expected_result,result_data,6)

    def test_004_t(self):
        # test with one tap equalizer
        M = 2**7
        syms_per_frame = 20
        num_frames = 2**8
        src_data = list()
        expected_result =list()
        for i in range(2*syms_per_frame*M*num_frames):
            if i%(2*syms_per_frame*M)==0:
                mul = int(random.random()*10)+1
                center_preamble = [1*mul,-1j*mul,-1*mul,1j*mul]
                preamble = [0]*M+center_preamble*(M/4)+[0]*M
                # add preamble
                src_data.extend(preamble)
                expected_result.extend(preamble)
            val = int(random.random()*10)
            src_data.append(mul*val)
            expected_result.append(val)
        # get original preamble back
        center_preamble = [1,-1j,-1,1j]
        preamble = [0]*M+center_preamble*(M/4)+[0]*M
        src = blocks.vector_source_c(src_data,vlen=M)
        scp = ofdm.fbmc_subchannel_processing_vcvc(M=M,syms_per_frame=syms_per_frame,preamble=preamble,sel_eq=0)
        dst = blocks.vector_sink_c(vlen=M)
        dst2 = blocks.vector_sink_c(vlen=M)
        self.tb.connect((src,0),(scp,0))
        self.tb.connect((scp,0),dst)
        self.tb.connect((scp,1),dst2)
        self.tb.run ()
        # check data
        result_data = dst.data()
        f = open('..\..\matlab\sp_python_output.txt', 'w')
        s = "i\tfr\tsrc\texp\tres\tdiff\n"
        f.write(s)
        for i in range(2*syms_per_frame*M*num_frames):
            s = str(i)+"\t"+str(int(i/(2*syms_per_frame*M)))+"\t"+str(src_data[i])+"\t"+str(expected_result[i])+"\t"+str(result_data[i])+"\t"+str(abs(expected_result[i]-result_data[i])>0)+"\n"
            f.write(s)
        f.close()
        
        # frame based check
        for i in range(num_frames):
            self.assertComplexTuplesAlmostEqual(tuple(
                expected_result[(i+1)*len(preamble)+i*(2*syms_per_frame*M):(i+1)*len(preamble)+(i+1)*(2*syms_per_frame*M)]),
            tuple(
                result_data[(i+1)*len(preamble)+i*(2*syms_per_frame*M):(i+1)*len(preamble)+(i+1)*(2*syms_per_frame*M)]),6)

    def test_005_t (self):
        # another test with one tap equalizer
        M = 2**7
        syms_per_frame = 20
        num_frames = 2**8
        root_center = [1,-1j,-1,1j]
        src_data = list()
        expected_result =list()
        for i in range(2*syms_per_frame*M*num_frames):
            if i%(2*syms_per_frame*M)==0:
                mul =  [int(10*random.random())+1 for j in range(M)]
                center_preamble = [mul[j]*root_center[j%4] for j in range(M)]
                preamble = [0]*M+center_preamble*(M/len(center_preamble))+[0]*M
                # add preamble
                src_data.extend(preamble)
                expected_result.extend(preamble)
            val = int(random.random()*10)
            src_data.append(mul[i%M]*val)
            expected_result.append(val)
        # get original preamble back        
        preamble = [0]*M+root_center*(M/4)+[0]*M
        src = blocks.vector_source_c(src_data,vlen=M)
        scp = ofdm.fbmc_subchannel_processing_vcvc(M=M,syms_per_frame=syms_per_frame,preamble=preamble,sel_eq=0)
        dst = blocks.vector_sink_c(vlen=M)
        dst2 = blocks.vector_sink_c(vlen=M)
        self.tb.connect((src,0),(scp,0))
        self.tb.connect((scp,0),dst)
        self.tb.connect((scp,1),dst2)
        self.tb.run ()
        # check data
        result_data = dst.data()
        f = open('..\..\matlab\sp_python_output.txt', 'w')
        s = "i\tfr\tsrc\texp\tres\tdiff\n"
        f.write(s)
        for i in range(2*syms_per_frame*M*num_frames):
            s = str(i)+"\t"+str(int(i/(2*syms_per_frame*M)))+"\t"+str(src_data[i])+"\t"+str(expected_result[i])+"\t"+str(result_data[i])+"\t"+str(abs(expected_result[i]-result_data[i])>0)+"\n"
            f.write(s)
        f.close()
        
        # frame based check
        for i in range(num_frames):
            self.assertComplexTuplesAlmostEqual(tuple(
                expected_result[(i+1)*len(preamble)+i*(2*syms_per_frame*M):(i+1)*len(preamble)+(i+1)*(2*syms_per_frame*M)]),
            tuple(
                result_data[(i+1)*len(preamble)+i*(2*syms_per_frame*M):(i+1)*len(preamble)+(i+1)*(2*syms_per_frame*M)]),6)

    def test_006_t (self):
        # test with three-tap equalizer with linear interpolation
        ##############################
        # this test case should be used along with MATLAB script data_generator_for_qa_scp.m
        # you can find that script in gr-fbmc/matlab/
        # remember to set eq_select = 3;
        # first create src_data and expected_result sequences as well as parameters (M,syms_per_frame,num_frames)
        # the parameters will be created in the same folder.
        # after generation of required data, you can run this test case.
        # with help of scipy libraries, those parameters will be fetched and computed.
        ##############################
        mat_src = scipy.io.loadmat('../../../matlab/src_data_linear.mat')
        mat_exp = scipy.io.loadmat('../../../matlab/expected_result_linear.mat')
        mat_par = scipy.io.loadmat('../../../matlab/parameters_linear.mat')
        M = int(mat_par['parameters']['M'][0][0][0][0])
        syms_per_frame = int(mat_par['parameters']['syms_per_frame'][0][0][0][0])
        num_frames = int(mat_par['parameters']['num_frames'][0][0][0][0])
        # root_center = list()
        # for i in range(len(mat_par['parameters']['center'][0][0])):
        #     root_center.append(mat_par['parameters']['center'][0][0][0][i])
        root_center = [1,-1j,-1,1j]*(M/4)
        src_data = list()
        expected_result =list()
        for i in range(len(mat_src['src_data'])):
            src_data.append(mat_src['src_data'][i][0])
        for i in range(len(mat_exp['expected_result'])):
            expected_result.append(mat_exp['expected_result'][i][0])

        # print src_data
        
        preamble = [0]*M+root_center+[0]*M
        src = blocks.vector_source_c(src_data,vlen=M)
        scp = ofdm.fbmc_subchannel_processing_vcvc(M=M,syms_per_frame=syms_per_frame,preamble=preamble,sel_eq=1)
        dst = blocks.vector_sink_c(vlen=M)
        dst2 = blocks.vector_sink_c(vlen=M)
        self.tb.connect((src,0),(scp,0))
        self.tb.connect((scp,0),dst)
        self.tb.connect((scp,1),dst2)
        self.tb.run ()
        # check data
        result_data = dst.data()
        # print len(result_data)
        self.assertComplexTuplesAlmostEqual(tuple(expected_result),tuple(result_data),4)

    def test_007_t(self):
        # test with three-tap equalizer with geometric interpolation
        ##############################
        # this test case should be used along with MATLAB script data_generator_for_qa_scp.m
        # you can find that script in gr-fbmc/matlab/
        # remember to set eq_select = 2;
        # first create src_data and expected_result sequences as well as parameters (M,syms_per_frame,num_frames)
        # the parameters will be created in the same folder.
        # after generation of required data, you can run this test case.
        # with help of scipy libraries, those parameters will be fetched and computed.
        ##############################
        mat_src = scipy.io.loadmat('../../../matlab/src_data_geometric.mat')
        mat_exp = scipy.io.loadmat('../../../matlab/expected_result_geometric.mat')
        mat_par = scipy.io.loadmat('../../../matlab/parameters_geometric.mat')
        M = int(mat_par['parameters']['M'][0][0][0][0])
        syms_per_frame = int(mat_par['parameters']['syms_per_frame'][0][0][0][0])
        num_frames = int(mat_par['parameters']['num_frames'][0][0][0][0])
        # root_center = list()
        # for i in range(len(mat_par['parameters']['center'][0][0])):
        #     root_center.append(mat_par['parameters']['center'][0][0][0][i])
        root_center = [1,-1j,-1,1j]*(M/4)
        src_data = list()
        expected_result =list()
        for i in range(len(mat_src['src_data'])):
            src_data.append(mat_src['src_data'][i][0])
        for i in range(len(mat_exp['expected_result'])):
            expected_result.append(mat_exp['expected_result'][i][0])

        # print src_data
        
        preamble = [0]*M+root_center+[0]*M
        src = blocks.vector_source_c(src_data,vlen=M)
        scp = ofdm.fbmc_subchannel_processing_vcvc(M=M,syms_per_frame=syms_per_frame,preamble=preamble,sel_eq=2)
        dst = blocks.vector_sink_c(vlen=M)
        dst2 = blocks.vector_sink_c(vlen=M)
        self.tb.connect((src,0),(scp,0))
        self.tb.connect((scp,0),dst)
        self.tb.connect((scp,1),dst2)
        self.tb.run ()
        # check data
        result_data = dst.data()
        # print len(result_data)
        self.assertComplexTuplesAlmostEqual(tuple(expected_result),tuple(result_data),4)

    def test_008_t(self):
        # test estimation with a different size of preamble
        M = 2**10
        syms_per_frame = 20
        num_frames = 2**8
        root_center = [1,-1j,-1,1j]
        src_data = list()
        expected_result =list()
        for i in range(2*syms_per_frame*M*num_frames):
            if i%(2*syms_per_frame*M)==0:
                mul =  [int(10*random.random())+1 for j in range(M)]
                center_preamble = [mul[j]*root_center[j%4] for j in range(M)]
                preamble = [0]*4*M+center_preamble*(M/len(center_preamble))+[0]*4*M
                # add preamble
                src_data.extend(preamble)
                expected_result.extend(preamble)
            val = int(random.random()*10)
            src_data.append(mul[i%M]*val)
            expected_result.append(val)
        # get original preamble back        
        preamble = [0]*4*M+root_center*(M/4)+[0]*4*M
        src = blocks.vector_source_c(src_data,vlen=M)
        scp = ofdm.fbmc_subchannel_processing_vcvc(M=M,syms_per_frame=syms_per_frame,preamble=preamble,sel_eq=0)
        dst = blocks.vector_sink_c(vlen=M)
        dst2 = blocks.vector_sink_c(vlen=M)
        self.tb.connect((src,0),(scp,0))
        self.tb.connect((scp,0),dst)
        self.tb.connect((scp,1),dst2)
        self.tb.run ()
        # check data
        result_data = dst.data()
        f = open('..\..\matlab\sp_python_output.txt', 'w')
        s = "i\tfr\tsrc\texp\tres\tdiff\n"
        f.write(s)
        for i in range(2*syms_per_frame*M*num_frames):
            s = str(i)+"\t"+str(int(i/(2*syms_per_frame*M)))+"\t"+str(src_data[i])+"\t"+str(expected_result[i])+"\t"+str(result_data[i])+"\t"+str(abs(expected_result[i]-result_data[i])>0)+"\n"
            f.write(s)
        f.close()
        
        # frame based check
        for i in range(num_frames):
            self.assertComplexTuplesAlmostEqual(tuple(
                expected_result[(i+1)*len(preamble)+i*(2*syms_per_frame*M):(i+1)*len(preamble)+(i+1)*(2*syms_per_frame*M)]),
            tuple(
                result_data[(i+1)*len(preamble)+i*(2*syms_per_frame*M):(i+1)*len(preamble)+(i+1)*(2*syms_per_frame*M)]),6)

    def test_009_t(self):
        # test estimation with a different size of preamble
        M = 2**10
        syms_per_frame = 20
        num_frames = 2**8
        root_center = [1,-1j,-1,1j]
        src_data = list()
        expected_result =list()
        for i in range(2*syms_per_frame*M*num_frames):
            if i%(2*syms_per_frame*M)==0:
                mul =  [int(10*random.random())+1 for j in range(M)]
                center_preamble = [mul[j]*root_center[j%4] for j in range(M)]
                preamble = [0]*5*M+center_preamble*(M/len(center_preamble))+[0]*5*M
                # add preamble
                src_data.extend(preamble)
                expected_result.extend(preamble)
            val = int(random.random()*10)
            src_data.append(mul[i%M]*val)
            expected_result.append(val)
        # get original preamble back        
        preamble = [0]*5*M+root_center*(M/4)+[0]*5*M
        src = blocks.vector_source_c(src_data,vlen=M)
        scp = ofdm.fbmc_subchannel_processing_vcvc(M=M,syms_per_frame=syms_per_frame,preamble=preamble,sel_eq=0)
        dst = blocks.vector_sink_c(vlen=M)
        dst2 = blocks.vector_sink_c(vlen=M)
        self.tb.connect((src,0),(scp,0))
        self.tb.connect((scp,0),dst)
        self.tb.connect((scp,1),dst2)
        self.tb.run ()
        # check data
        result_data = dst.data()
        f = open('..\..\matlab\sp_python_output.txt', 'w')
        s = "i\tfr\tsrc\texp\tres\tdiff\n"
        f.write(s)
        for i in range(2*syms_per_frame*M*num_frames):
            s = str(i)+"\t"+str(int(i/(2*syms_per_frame*M)))+"\t"+str(src_data[i])+"\t"+str(expected_result[i])+"\t"+str(result_data[i])+"\t"+str(abs(expected_result[i]-result_data[i])>0)+"\n"
            f.write(s)
        f.close()
        
        # frame based check
        for i in range(num_frames):
            self.assertComplexTuplesAlmostEqual(tuple(
                expected_result[(i+1)*len(preamble)+i*(2*syms_per_frame*M):(i+1)*len(preamble)+(i+1)*(2*syms_per_frame*M)]),
            tuple(
                result_data[(i+1)*len(preamble)+i*(2*syms_per_frame*M):(i+1)*len(preamble)+(i+1)*(2*syms_per_frame*M)]),6)


if __name__ == '__main__':
    gr_unittest.run(qa_fbmc_subchannel_processing_vcvc, "qa_fbmc_subchannel_processing_vcvc.xml")
