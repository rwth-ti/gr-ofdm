#!/usr/bin/env python

from gnuradio import gr, gr_unittest
import ofdm_swig as ofdm

class qa_vector_sum (gr_unittest.TestCase):
  def setUp (self):
    self.fg = gr.top_block ("test_block")

  def tearDown (self):
    self.fg = None

  def test_vcc_001(self):
    N = 10

    data = [1.0+2.0j]*N

    src = gr.vector_source_c(data)
    s2v = gr.stream_to_vector(gr.sizeof_gr_complex,N)
    dst = gr.vector_sink_c()

    uut = ofdm.vector_sum_vcc(N)

    self.fg.connect(src,s2v,uut,dst)

    self.fg.run()

    self.assertEqual([sum(data)],list(dst.data()))

  def test_vcc_002(self):
    N = 10

    data = [1.0+2.0j]*(N*2)

    src = gr.vector_source_c(data)
    s2v = gr.stream_to_vector(gr.sizeof_gr_complex,N)
    dst = gr.vector_sink_c()

    uut = ofdm.vector_sum_vcc(N)

    self.fg.connect(src,s2v,uut,dst)

    self.fg.run()

    self.assertEqual([sum(data[0:N]),sum(data[N:2*N])],list(dst.data()))

  def test_vff_001(self):
    N = 10

    data = [2.0]*N

    src = gr.vector_source_c(data)
    s2v = gr.stream_to_vector(gr.sizeof_gr_complex,N)
    dst = gr.vector_sink_c()

    uut = ofdm.vector_sum_vcc(N)

    self.fg.connect(src,s2v,uut,dst)

    self.fg.run()

    self.assertEqual([sum(data)],list(dst.data()))

  def test_vff_002(self):
    N = 10

    data = [2.0]*(N*2)

    src = gr.vector_source_c(data)
    s2v = gr.stream_to_vector(gr.sizeof_gr_complex,N)
    dst = gr.vector_sink_c()

    uut = ofdm.vector_sum_vcc(N)

    self.fg.connect(src,s2v,uut,dst)

    self.fg.run()

    self.assertEqual([sum(data[0:N]),sum(data[N:2*N])],list(dst.data()))

if __name__ == '__main__':
  gr_unittest.main()

