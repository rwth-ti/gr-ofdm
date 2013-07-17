#!/usr/bin/env python

from gnuradio import gr, gr_unittest
import ofdm as ofdm
from random import seed,randint
from numpy import concatenate


class qa_stream_controlled_mux (gr_unittest.TestCase):
  def setUp (self):
    self.fg = gr.top_block ("test_block")

  def tearDown (self):
    self.fg = None

  # static test
  def test_001 (self):
    stream = [ [0]*10, [1]*10, [2]*10 ]
    mux = [ 0,2,2,1,1,2,0,2,0,0,
            1,0,1,0,1,2,1,2,1,1,
            2,0,0,2,1,2,0,1,2,0 ]

    muxstream = gr.vector_source_s(mux)
    data = [gr.vector_source_s(stream[0]),
            gr.vector_source_s(stream[1]),
            gr.vector_source_s(stream[2])]
    dst = gr.vector_sink_s()

    uut = ofdm.stream_controlled_mux(gr.sizeof_short)

    self.fg.connect(muxstream,uut)
    self.fg.connect(data[0], (uut,1))
    self.fg.connect(data[1], (uut,2))
    self.fg.connect(data[2], (uut,3))

    self.fg.connect(uut,dst)
    self.fg.run()

    self.assertEqual(mux,list(dst.data()))

  # many input items
  def test_002 (self):
    l = 100000
    stream = [ [0]*l, [1]*l, [2]*l, [3]*l ]
    mux = concatenate(stream)

    seed()
    for i in range(l):
      a = randint(0,len(mux)-1)
      b = randint(0,len(mux)-1)
      mux[a],mux[b] = mux[b],mux[a]

    muxstream = gr.vector_source_s(mux.tolist())
    data = [gr.vector_source_s(stream[0]),
            gr.vector_source_s(stream[1]),
            gr.vector_source_s(stream[2]),
            gr.vector_source_s(stream[3])]
    dst = gr.vector_sink_s()

    uut = ofdm.stream_controlled_mux(gr.sizeof_short)

    self.fg.connect(muxstream,uut)
    self.fg.connect(data[0], (uut,1))
    self.fg.connect(data[1], (uut,2))
    self.fg.connect(data[2], (uut,3))
    self.fg.connect(data[3], (uut,4))

    self.fg.connect(uut,dst)
    self.fg.run()

    self.assertEqual(list(mux),list(dst.data()))

  # different input stream type
  def test_003 (self):
    stream = [ [float(0)]*10, [float(1)]*10, [float(2)]*10 ]
    mux = [ 0,2,2,1,1,2,0,2,0,0,
            1,0,1,0,1,2,1,2,1,1,
            2,0,0,2,1,2,0,1,2,0 ]

    muxstream = gr.vector_source_s(mux)
    data = [gr.vector_source_f(stream[0]),
            gr.vector_source_f(stream[1]),
            gr.vector_source_f(stream[2])]
    dst = gr.vector_sink_f()

    uut = ofdm.stream_controlled_mux(gr.sizeof_float)

    self.fg.connect(muxstream,uut)
    self.fg.connect(data[0], (uut,1))
    self.fg.connect(data[1], (uut,2))
    self.fg.connect(data[2], (uut,3))

    self.fg.connect(uut,dst)
    self.fg.run()

    self.assertEqual(map(float,mux),list(dst.data()))

  # input streams differ in length
  def test_004 (self):
    stream = [ [0]*10, [1]*5, [2]*8 ]
    mux = [ 0,2,2,1,1,2,0,2,0,0,
            1,0,1,0,1,2,2,1,1,
            2,0,0,2,1,2,0,1,2,0 ]
    ref = [ 0,2,2,1,1,2,0,2,0,0,
            1,0,1,0,1,2,2]

    muxstream = gr.vector_source_s(mux)
    data = [gr.vector_source_s(stream[0]),
            gr.vector_source_s(stream[1]),
            gr.vector_source_s(stream[2])]
    dst = gr.vector_sink_s()

    uut = ofdm.stream_controlled_mux(gr.sizeof_short)

    self.fg.connect(muxstream,uut)
    self.fg.connect(data[0], (uut,1))
    self.fg.connect(data[1], (uut,2))
    self.fg.connect(data[2], (uut,3))

    self.fg.connect(uut,dst)
    self.fg.run()

    self.assertEqual(ref,list(dst.data()))





#  # static test
#  def test_005 (self):
#    stream = [ [0]*10, [1]*10, [2]*10 ]
#    mux = [ 0,2,2,1,1,2,0,2,0,0,
#            1,0,1,0,1,2,1,2,1,1,
#            2,0,0,2,1,2,0,1,2,0 ]
#
#    muxstream = gr.vector_source_s(mux)
#    data = [gr.vector_source_c(stream[0]),
#            gr.vector_source_c(stream[1]),
#            gr.vector_source_c(stream[2])]
#    dst = gr.vector_sink_c()
#
#    uut = ofdm.stream_controlled_mux_c()
#
#    self.fg.connect(muxstream,uut)
#    self.fg.connect(data[0], (uut,1))
#    self.fg.connect(data[1], (uut,2))
#    self.fg.connect(data[2], (uut,3))
#
#    self.fg.connect(uut,dst)
#    self.fg.run()
#
#    self.assertEqual(mux,list(dst.data()))
#
#  # many input items
#  def test_006 (self):
#    l = 100000
#    stream = [ [0]*l, [1]*l, [2]*l, [3]*l ]
#    mux = concatenate(stream)
#
#    seed()
#    for i in range(l):
#      a = randint(0,len(mux)-1)
#      b = randint(0,len(mux)-1)
#      mux[a],mux[b] = mux[b],mux[a]
#
#    muxstream = gr.vector_source_s(mux)
#    data = [gr.vector_source_s(stream[0]),
#            gr.vector_source_s(stream[1]),
#            gr.vector_source_s(stream[2]),
#            gr.vector_source_s(stream[3])]
#    dst = gr.vector_sink_s()
#
#    uut = ofdm.stream_controlled_mux(gr.sizeof_short)
#
#    self.fg.connect(muxstream,uut)
#    self.fg.connect(data[0], (uut,1))
#    self.fg.connect(data[1], (uut,2))
#    self.fg.connect(data[2], (uut,3))
#    self.fg.connect(data[3], (uut,4))
#
#    self.fg.connect(uut,dst)
#    self.fg.run()
#
#    self.assertEqual(list(mux),list(dst.data()))
#
#  # different input stream type
#  def test_003 (self):
#    stream = [ [float(0)]*10, [float(1)]*10, [float(2)]*10 ]
#    mux = [ 0,2,2,1,1,2,0,2,0,0,
#            1,0,1,0,1,2,1,2,1,1,
#            2,0,0,2,1,2,0,1,2,0 ]
#
#    muxstream = gr.vector_source_s(mux)
#    data = [gr.vector_source_f(stream[0]),
#            gr.vector_source_f(stream[1]),
#            gr.vector_source_f(stream[2])]
#    dst = gr.vector_sink_f()
#
#    uut = ofdm.stream_controlled_mux(gr.sizeof_float)
#
#    self.fg.connect(muxstream,uut)
#    self.fg.connect(data[0], (uut,1))
#    self.fg.connect(data[1], (uut,2))
#    self.fg.connect(data[2], (uut,3))
#
#    self.fg.connect(uut,dst)
#    self.fg.run()
#
#    self.assertEqual(map(float,mux),list(dst.data()))
#
#  # input streams differ in length
#  def test_004 (self):
#    stream = [ [0]*10, [1]*5, [2]*8 ]
#    mux = [ 0,2,2,1,1,2,0,2,0,0,
#            1,0,1,0,1,2,2,1,1,
#            2,0,0,2,1,2,0,1,2,0 ]
#    ref = [ 0,2,2,1,1,2,0,2,0,0,
#            1,0,1,0,1,2,2]
#
#    muxstream = gr.vector_source_s(mux)
#    data = [gr.vector_source_s(stream[0]),
#            gr.vector_source_s(stream[1]),
#            gr.vector_source_s(stream[2])]
#    dst = gr.vector_sink_s()
#
#    uut = ofdm.stream_controlled_mux(gr.sizeof_short)
#
#    self.fg.connect(muxstream,uut)
#    self.fg.connect(data[0], (uut,1))
#    self.fg.connect(data[1], (uut,2))
#    self.fg.connect(data[2], (uut,3))
#
#    self.fg.connect(uut,dst)
#    self.fg.run()
#
#    self.assertEqual(ref,list(dst.data()))


if __name__ == '__main__':
  gr_unittest.main()

