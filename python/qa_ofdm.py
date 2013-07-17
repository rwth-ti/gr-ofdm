#!/usr/bin/env python
#
# Copyright 2004,2007 Free Software Foundation, Inc.
#
# This file is part of GNU Radio
#
# GNU Radio is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 3, or (at your option)
# any later version.
#
# GNU Radio is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with GNU Radio; see the file COPYING.  If not, write to
# the Free Software Foundation, Inc., 51 Franklin Street,
# Boston, MA 02110-1301, USA.
#

from gnuradio import gr, gr_unittest
import ofdm as ofdm

class qa_ofdm (gr_unittest.TestCase):

    def setUp (self):
        self.tb = gr.top_block ()

    def tearDown (self):
        self.tb = None

    def test_001_cube_ff (self):
        src_data = (-3, 4, -5.5, 2, 3)
        expected_result = (-27, 64, -166.375, 8, 27)
        src = gr.vector_source_f (src_data)
        sqr = ofdm.cube_ff ()
        dst = gr.vector_sink_f ()
        self.tb.connect (src, sqr)
        self.tb.connect (sqr, dst)
        self.tb.run ()
        result_data = dst.data ()
	print "Test 1: cube_ff";
	print "expected result", expected_result;
	print "actual result", result_data; 
        self.assertFloatTuplesAlmostEqual (expected_result, result_data, 6)

    def test_002_power4_ff (self):
        src_data = (-3, 4, -5.5, 2, 3)
        expected_result = (81, 256, 915.0625, 16, 81)
        src = gr.vector_source_f (src_data)
        sqr = ofdm.power4_ff ()
        dst = gr.vector_sink_f ()
        self.tb.connect (src, sqr)
        self.tb.connect (sqr, dst)
        self.tb.run ()
        result_data = dst.data ()
	print "Test 2: power4_ff";
        print "expected result", expected_result;
        print "actual result", result_data;

        self.assertFloatTuplesAlmostEqual (expected_result, result_data, 6)

if __name__ == '__main__':
    gr_unittest.main ()
