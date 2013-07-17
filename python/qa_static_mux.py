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
    imux = []
    for x in mux:
      imux.append(int(x))

    data = [gr.vector_source_s(stream[0]),
            gr.vector_source_s(stream[1]),
            gr.vector_source_s(stream[2])]
    dst = gr.vector_sink_s()

    uut = ofdm.static_mux_v(gr.sizeof_short, imux)

    self.fg.connect(data[0], (uut,0))
    self.fg.connect(data[1], (uut,1))
    self.fg.connect(data[2], (uut,2))

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

    imux = []
    for x in mux:
      imux.append(int(x))
      
    data = [gr.vector_source_s(stream[0]),
            gr.vector_source_s(stream[1]),
            gr.vector_source_s(stream[2]),
            gr.vector_source_s(stream[3])]
    dst = gr.vector_sink_s()

    uut = ofdm.static_mux_v(gr.sizeof_short, imux)

    self.fg.connect(data[0], (uut,0))
    self.fg.connect(data[1], (uut,1))
    self.fg.connect(data[2], (uut,2))
    self.fg.connect(data[3], (uut,3))

    self.fg.connect(uut,dst)
    self.fg.run()

    self.assertEqual(list(mux),list(dst.data()))

  # different input stream type
  def test_003 (self):
    stream = [ [float(0)]*10, [float(1)]*10, [float(2)]*10 ]
    mux = [ 0,2,2,1,1,2,0,2,0,0,
            1,0,1,0,1,2,1,2,1,1,
            2,0,0,2,1,2,0,1,2,0 ]

    imux = []
    for x in mux:
      imux.append(int(x))
      
    data = [gr.vector_source_f(stream[0]),
            gr.vector_source_f(stream[1]),
            gr.vector_source_f(stream[2])]
    dst = gr.vector_sink_f()

    uut = ofdm.static_mux_v(gr.sizeof_float, imux)

    self.fg.connect(data[0], (uut,0))
    self.fg.connect(data[1], (uut,1))
    self.fg.connect(data[2], (uut,2))

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

    imux = []
    for x in mux:
      imux.append(int(x))
      
    data = [gr.vector_source_s(stream[0]),
            gr.vector_source_s(stream[1]),
            gr.vector_source_s(stream[2])]
    dst = gr.vector_sink_s()

    uut = ofdm.static_mux_v(gr.sizeof_short, imux)

    self.fg.connect(data[0], (uut,0))
    self.fg.connect(data[1], (uut,1))
    self.fg.connect(data[2], (uut,2))

    self.fg.connect(uut,dst)
    self.fg.run()

    self.assertEqual(ref,list(dst.data()))
    
  def test_005 (self):
    stream = [ [0]*10, [1]*10, [2]*10 ]
    mux = [ 0,1,2 ]
    ref = [ 0,1,2,0,1,2,0,1,2,0,1,2,0,1,2,0,1,2,0,1,2,
           0,1,2,0,1,2,0,1,2 ]

    imux = []
    for x in mux:
      imux.append(int(x))
      
    data = [gr.vector_source_s(stream[0]),
            gr.vector_source_s(stream[1]),
            gr.vector_source_s(stream[2])]
    dst = gr.vector_sink_s()

    uut = ofdm.static_mux_v(gr.sizeof_short, imux)

    self.fg.connect(data[0], (uut,0))
    self.fg.connect(data[1], (uut,1))
    self.fg.connect(data[2], (uut,2))

    self.fg.connect(uut,dst)
    self.fg.run()

    self.assertEqual(ref,list(dst.data()))

  def test_006 (self):
    l = 100000
    stream = [ [0]*l, [1]*l, [2]*l ]
    mux = [ 0,2,1 ]
    ref = concatenate([mux]*l)

    imux = []
    for x in mux:
      imux.append(int(x))
      
    data = [gr.vector_source_s(stream[0]),
            gr.vector_source_s(stream[1]),
            gr.vector_source_s(stream[2])]
    dst = gr.vector_sink_s()

    uut = ofdm.static_mux_v(gr.sizeof_short, imux)

    self.fg.connect(data[0], (uut,0))
    self.fg.connect(data[1], (uut,1))
    self.fg.connect(data[2], (uut,2))

    self.fg.connect(uut,dst)
    self.fg.run()

    self.assertEqual(list(ref),list(dst.data()))
    
#  def test_007(self):
#    mux = [-1,0,1]
#    
#    imux = []
#    for x in mux:
#      imux.append(int(x))
#      
#    uut = ofdm.static_mux_v(gr.sizeof_short, imux)
#    dst = gr.vector_sink_s()
#    
#    self.fg.connect(gr.vector_source_s([0,0,0]),(uut,0))
#    self.fg.connect(uut,dst)
#    
#    try:
#      self.fg.run()
#    except:
#      pass
#    


if __name__ == '__main__':
  gr_unittest.main()
