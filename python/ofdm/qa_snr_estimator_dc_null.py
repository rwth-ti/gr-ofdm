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
        d_vlen=4
        d_skip=2
        d_dc_null=2

        sum_load=0
        sum_null=0

        #noise
        noise=np.random.normal(0,1,1000)
        src_data=[2,1]*10
#        src_data=[sum(x) for x in zip(data,noise)]
        src=blocks.vector_source_c(src_data,vlen=4)
        snr=ofdm.snr_estimator(d_vlen,d_skip)
        snr_dc_null=ofdm.snr_estimator_dc_null(d_vlen,d_skip,d_dc_null)
        dst=blocks.vector_sink_f()
        dst_noise=blocks.vector_sink_f()
        dst_dc_null=blocks.vector_sink_f()
        dst_dc_null_noise=blocks.vector_sink_f()
        #construct the flowgraph
        self.tb.connect(src,snr_dc_null)
        self.tb.connect(src,snr)

        self.tb.connect((snr_dc_null,0),dst_dc_null)
        self.tb.connect((snr_dc_null,1),dst_dc_null_noise)

        self.tb.connect((snr,0),dst)
        self.tb.connect((snr,1),dst_noise)
                
        # set up fg
        self.tb.run ()
        
        print "output", dst.data()
        print "output dc_null", dst_dc_null.data()
        # calculate reference data
        dc_null_noise=dst_dc_null.data()
        if not d_dc_null:
            for index,number in enumerate(src_data):
                square=number*number.conjugate()
                if not index%d_skip:
                    sum_load+=square
                else:
                    sum_null+=square
            estim =(1./d_skip)*((d_skip-1)*sum_load/sum_null-1)
            estim_noise = sum_null*d_skip/(d_skip-1)/d_vlen
        else:
            results=[0]*80
            estim_noise=results
            estim=results

#Compare with snr_estimator_block
        self.assertEqual(dst_dc_null.data(),dst.data())
        self.assertEqual(dst_dc_null_noise.data(),dst_noise.data())

#Compare with reference data from above
#       self.assertEqual(output2[0],estim_noise)
#       self.assertEqual(dst.data()[0],estim)

if __name__ == '__main__':
    gr_unittest.run(qa_snr_estimator_dc_null, "qa_snr_estimator_dc_null.xml")
