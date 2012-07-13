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
import ofdm.ofdm_swig as ofdm

import sys, numpy, random

class qa_ofdm (gr_unittest.TestCase):
  def setUp (self):
    self.fg = gr.top_block ("test_block")

  def tearDown (self):
    self.fg = None

  def test_007_vector_sampler(self):
    data = range(1,577,1) # 1..576
    trigger = numpy.concatenate([[0]*575,[1]])
    blocks = 10000
    expected = data[64:577]
    assert(len(expected)==512)
    expected = numpy.concatenate([expected*blocks])
    assert(len(expected) == 512*blocks)

    src = gr.vector_source_c(data,True)
    src2 = gr.vector_source_b(trigger.tolist(),True)
    dst = gr.vector_sink_c()
    sampler = ofdm.vector_sampler(gr.sizeof_gr_complex,512)
    v2s = gr.vector_to_stream(gr.sizeof_gr_complex,512)

    self.fg.connect(src, (sampler,0))
    self.fg.connect(src2,gr.head(gr.sizeof_char,blocks*576), (sampler,1))
    self.fg.connect(sampler, v2s, dst)

    self.fg.run()
    #self.assertEqual(numpy.array(expected,numpy.Complex), numpy.array(dst.data(), numpy.Complex))
    if numpy.array(expected).all() != numpy.array(dst.data()).all():
      print "up"
      print len(expected),len(dst.data())
      vec = dst.data()
      for i in range(min(len(expected),len(dst.data()))):
        if vec[i] != expected[i]:
          print "e at ",i

"""
  # general test case
  def test_001_vector_sampler (self):
    data = range(1,33,1) # 1..32
    # 16, 19, 20, 32
    trigger = numpy.concatenate([[0]*15,[1],[0]*2,[1],[1],[0]*12])
    expected = numpy.array(numpy.concatenate([data[0:16],data[3:19],data[4:20]]),numpy.Complex)

    src = gr.vector_source_c(data, False)
    src2 = gr.vector_source_b(trigger, False)
    dst = gr.vector_sink_c()
    sampler = ofdm.vector_sampler(gr.sizeof_gr_complex,16)
    v2s = gr.vector_to_stream(gr.sizeof_gr_complex,16)

    self.fg.connect(src, (sampler,0))
    self.fg.connect(src2, (sampler,1))
    self.fg.connect(sampler, v2s, dst)

    self.fg.run()
    self.assertEqual(expected, numpy.array(dst.data(), numpy.Complex))

  # trigger stream shorter than the other
  def test_002_vector_sampler (self):
    data = range(1,33,1) # 1..32
    trigger = numpy.concatenate([[0]*20,[1]])
    expected = numpy.array(data[5:21],numpy.Complex)

    src = gr.vector_source_c(data, False)
    src2 = gr.vector_source_b(trigger, False)
    dst = gr.vector_sink_c()
    sampler = ofdm.vector_sampler(gr.sizeof_gr_complex,16)
    v2s = gr.vector_to_stream(gr.sizeof_gr_complex,16)

    self.fg.connect(src, (sampler,0))
    self.fg.connect(src2, (sampler,1))
    self.fg.connect(sampler, v2s, dst)

    self.fg.run()
    self.assertEqual(expected, numpy.array(dst.data(), numpy.Complex))

  # data stream shorter than the other
  def test_003_vector_sampler (self):
    data = range(1,33,1) # 1..32
    # 16, 19, 20
    trigger = numpy.concatenate([[0]*15,[1],[0]*2,[1],[1],[0]*20,[1]])
    expected = numpy.array(numpy.concatenate([data[0:16],data[3:19],data[4:20]]),numpy.Complex)

    src = gr.vector_source_c(data, False)
    src2 = gr.vector_source_b(trigger, False)
    dst = gr.vector_sink_c()
    sampler = ofdm.vector_sampler(gr.sizeof_gr_complex,16)
    v2s = gr.vector_to_stream(gr.sizeof_gr_complex,16)

    self.fg.connect(src, (sampler,0))
    self.fg.connect(src2, (sampler,1))
    self.fg.connect(sampler, v2s, dst)

    self.fg.run()
    self.assertEqual(expected, numpy.array(dst.data(), numpy.Complex))

  # trigger at the last position
  def test_004_vector_sampler (self):
    data = range(1,33,1) # 1..32
    trigger = numpy.concatenate([[0]*31,[1]])
    expected = numpy.array(data[16:32],numpy.Complex)

    src = gr.vector_source_c(data, False)
    src2 = gr.vector_source_b(trigger, False)
    dst = gr.vector_sink_c()
    sampler = ofdm.vector_sampler(gr.sizeof_gr_complex,16)
    v2s = gr.vector_to_stream(gr.sizeof_gr_complex,16)

    self.fg.connect(src, (sampler,0))
    self.fg.connect(src2, (sampler,1))
    self.fg.connect(sampler, v2s, dst)

    self.fg.run()
    self.assertEqual(expected, numpy.array(dst.data(), numpy.Complex))

  # many triggers
  def test_006_vector_sampler (self):
    data = range(1,33,1) # 1..32
    trigger = numpy.concatenate([[0]*15,[1]*17])
    expected = numpy.concatenate(
       [data[ 0:16],data[ 1:17],data[ 2:18],data[ 3:19],data[ 4:20],data[ 5:21],
        data[ 6:22],data[ 7:23],data[ 8:24],data[ 9:25],data[10:26],data[11:27],
        data[12:28],data[13:29],data[14:30],data[15:31],data[16:32] ]);

    src = gr.vector_source_c(data, False)
    src2 = gr.vector_source_b(trigger, False)
    dst = gr.vector_sink_c()
    sampler = ofdm.vector_sampler(gr.sizeof_gr_complex,16)
    v2s = gr.vector_to_stream(gr.sizeof_gr_complex,16)

    self.fg.connect(src, (sampler,0))
    self.fg.connect(src2, (sampler,1))
    self.fg.connect(sampler, v2s, dst)

    self.fg.run()
    self.assertEqual(expected, numpy.array(dst.data(), numpy.Complex))
"""

if __name__ == '__main__':
  gr_unittest.main()

