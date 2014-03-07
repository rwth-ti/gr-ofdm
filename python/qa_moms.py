#!/usr/bin/env python
# 
# Copyright 2014 Institute for Theoretical Information Technology,
#                RWTH Aachen University
#                www.ti.rwth-aachen.de
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

from gnuradio import gr, gr_unittest, blocks
from moms import moms
import ofdm as ofdm

class qa_scf (gr_unittest.TestCase):

    def setUp (self):
        self.tb = gr.top_block ("test_block")

    def tearDown (self):
        self.tb = None 

    def std_test (self, src_data, soff, expected):
        src = blocks.vector_source_c (src_data,False,1)
        interp = moms(2,1)
        dst = blocks.vector_sink_c (1)
        self.tb.connect (src, interp)
        self.tb.connect (interp, dst)
        self.tb.run ()
        result_data = dst.data ()
        print result_data
        self.assertEqual(expected, result_data)

    def test_001_moms (self):
        soff = 1
        src_vec = range(1,10)
        expected = (0.5, 1.0, 1.5, 2.0, 2.5, 3.0, 3.5, 4.0)
        self.std_test (src_vec, soff, expected)

if __name__ == '__main__':
    gr_unittest.main ()


