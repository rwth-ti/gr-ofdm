#!/usr/bin/env python
#
# Copyright 2004 Free Software Foundation, Inc.
#
# This file is part of GNU Radio
#
# GNU Radio is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2, or (at your option)
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
from numpy import concatenate
import sys, numpy, random

class qa_ofdm (gr_unittest.TestCase):
	def setUp (self):
		self.fg = gr.top_block ("test_block")

	def tearDown (self):
		self.fg = None

	def test_001 (self):
		repetitions = 4
		#unsigned short input_bits, unsigned short repetitions
		uut = ofdm.repetition_encoder_sb(4, repetitions, [0]*(4*repetitions))
		src = gr.vector_source_s([16+8+4+2+1, 16+1])
		dst = gr.vector_sink_b()

		self.fg.connect(src, uut, dst)
		self.fg.run()

		ref = concatenate([[1,1,1,1]*repetitions, [1,0,0,0]*repetitions])
		self.assertEqual(list(ref), list(dst.data()))


	def test_002 (self):
		repetitions = 4
		input = concatenate([[1,1,1,1]*repetitions, [1,0,0,0]*repetitions])

		#unsigned short output_bits, unsigned short repetitions
		uut = ofdm.repetition_decoder_bs(4, repetitions, [0]*(4*repetitions))
		src = gr.vector_source_b(input.tolist())
		dst = gr.vector_sink_s()

		self.fg.connect(src, uut, dst)
		self.fg.run()

		ref = concatenate([[8+4+2+1], [1]])
		self.assertEqual(list(ref), list(dst.data()))


	def test_003 (self):
		repetitions = 4
		inout = [8+4+2+1, 1]
		#unsigned short input_bits, unsigned short repetitions
		uut1 = ofdm.repetition_encoder_sb(4, repetitions, [1,0,1,1,1,0,1,1,1,0,1,1,0,1,1,0])
		uut2 = ofdm.repetition_decoder_bs(4, repetitions, [1,0,1,1,1,0,1,1,1,0,1,1,0,1,1,0])
		src = gr.vector_source_s(inout)
		dst = gr.vector_sink_s()

		self.fg.connect(src, uut1, uut2, dst)
		self.fg.run()

		self.assertEqual(inout, list(dst.data()))


if __name__ == '__main__':
	gr_unittest.main()

