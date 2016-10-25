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
import ofdm
import numpy as np

class qa_snr_estimator_dc_null (gr_unittest.TestCase):

    def setUp (self):
        self.tb = gr.top_block ()

    def tearDown (self):
        self.tb = None

    def test_001_t (self):
        vlen=16
        skip=4
        dc_null=0
        ofdm_sym=1
        expected_snr = ((1-0.01)/(0.01),)
        expected_noise = (0.01,)
        # define the blocks
        # all the power is allocated to the pilots
        src_data = [0.1]*(skip/2) + [skip] + [0.1]*(skip/2-1)
        src_data = src_data * (vlen/skip)
        src = blocks.vector_source_c(src_data,False,vlen)
        snr_estim = ofdm.snr_estimator_dc_null(vlen,skip,dc_null)
        dst = blocks.vector_sink_f()
        dst_noise = blocks.vector_sink_f()

        # construct the flowgraph
        self.tb.connect(src,snr_estim)
        self.tb.connect((snr_estim,0),dst)
        self.tb.connect((snr_estim,1),dst_noise)

        # set up fg
        self.tb.run ()
        print "snr", dst.data()
        print "noise", dst_noise.data()

        # Compare with reference data from above
        self.assertFloatTuplesAlmostEqual(dst.data(),expected_snr)
        self.assertFloatTuplesAlmostEqual(dst_noise.data(),expected_noise)

    def test_002_t (self):
        vlen=16
        skip=4
        dc_null=2
        ofdm_sym=2
        expected_snr = ((1-0.01)/(0.01), (1-0.01)/(0.01))
        expected_noise = (0.01, 0.01)
        # define the blocks
        src_data = [0.1]*(skip/2) + [skip] + [0.1]*(skip/2-1)
        src_data = src_data * (vlen/skip)
        src_data = [0]*(dc_null/2) + src_data[:(vlen/2-dc_null/2)]  + src_data[(vlen/2+dc_null/2):] + [0]*(dc_null/2)
        src_data = src_data * (ofdm_sym)
        src = blocks.vector_source_c(src_data,False,vlen)
        snr_estim = ofdm.snr_estimator_dc_null(vlen,skip,dc_null)
        dst = blocks.vector_sink_f()
        dst_noise = blocks.vector_sink_f()

        # construct the flowgraph
        self.tb.connect(src,snr_estim)
        self.tb.connect((snr_estim,0),dst)
        self.tb.connect((snr_estim,1),dst_noise)

        # set up fg
        self.tb.run ()
        print "snr", dst.data()
        print "noise", dst_noise.data()

        # Compare with reference data from above
        self.assertFloatTuplesAlmostEqual(dst.data(),expected_snr)
        self.assertFloatTuplesAlmostEqual(dst_noise.data(),expected_noise)


if __name__ == '__main__':
    gr_unittest.run(qa_snr_estimator_dc_null, "qa_snr_estimator_dc_null.xml")
