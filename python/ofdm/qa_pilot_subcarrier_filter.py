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

from gnuradio import gr, gr_unittest
import ofdm as ofdm
import preambles
from numpy import concatenate,reshape,zeros
from station_configuration import *

class qa_pilot_subcarrier_filter (gr_unittest.TestCase):
  def setUp (self):
    self.fg = gr.top_block ("test_block")

  def tearDown (self):
    self.fg = None

  def test_001(self):
    frames = 5
    config = station_configuration()
    config.subcarriers = 12
    config.data_subcarriers = 8

    config.training_data = dummy()
    config.training_data.shifted_pilot_tones = [1,4,8,11]

    data =  [1.0] * config.subcarriers
    for x in config.training_data.shifted_pilot_tones:
      data[x] = 2.0
    data = concatenate([data]*frames)

    ref = [1.0]*(config.data_subcarriers*frames)

    src = gr.vector_source_c(data)
    s2v = gr.stream_to_vector(gr.sizeof_gr_complex,config.subcarriers)
    dst = gr.vector_sink_c()
    v2s = gr.vector_to_stream(gr.sizeof_gr_complex,config.data_subcarriers)

    uut = preambles.pilot_subcarrier_filter()
    self.fg.connect(src,s2v,uut,v2s,dst)

    self.fg.run()
    self.assertEqual(ref,list(dst.data()))

class dummy:
  def __init__(self):
    self.shifted_pilot_tones = []

if __name__ == '__main__':
  gr_unittest.main()

