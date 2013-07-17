#!/usr/bin/env python

from gnuradio import gr, gr_unittest
import ofdm as ofdm

from numpy import concatenate,zeros

class qa_skip (gr_unittest.TestCase):
  def setUp (self):
    self.fg = gr.top_block ("test_block")

  def tearDown (self):
    self.fg = None

  def test_001 (self):
    blocklen = 10
    vlen = 4
    blocks = 2

    skip = [1,4,8]

    data = [[float(i)]*vlen for i in range(0,blocklen*blocks)]
    trigger = [concatenate([[1],[0]*(blocklen-1)])]*blocks
    trigger_ref = [concatenate([[1],[0]*(blocklen-len(skip)-1)])]*blocks

    ref = []
    for x in range(len(data)):
      p = x % blocklen
      if not (p in skip):
        ref.append(data[x])

    data = concatenate(data)
    ref = concatenate(ref)
    trigger = concatenate(trigger)
    trigger_ref = concatenate(trigger_ref)

    src = gr.vector_source_f(data)
    src2 = gr.vector_source_b(trigger.tolist())
    dst = gr.vector_sink_f()
    dst2 = gr.vector_sink_b()
    uut = ofdm.skip(gr.sizeof_float*vlen,blocklen)

    for x in skip:
      uut.skip(x)


    self.fg.connect(src,gr.stream_to_vector(gr.sizeof_float,vlen),
                    uut,gr.vector_to_stream(gr.sizeof_float,vlen),dst)
    self.fg.connect(src2,(uut,1),dst2)

    self.fg.run()

    self.assertFloatTuplesAlmostEqual(ref,dst.data())
    self.assertEqual(list(trigger_ref),list(dst2.data()))



if __name__ == '__main__':
  gr_unittest.main()

