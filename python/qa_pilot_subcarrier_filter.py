#!/usr/bin/env python

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

