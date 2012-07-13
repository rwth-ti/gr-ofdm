#!/usr/bin/env python

from gnuradio import gr, gr_unittest
import ofdm.ofdm_swig as ofdm
from random import randint

class qa_modulation(gr_unittest.TestCase):
  def setUp (self):
    self.tb = gr.top_block()
    
  def tearDown(self):
    self.tb = None
  
  def stdtest_01(self,bps):
    # no reuse, bps bits per symbol
    vsyms = 10
    vlen = 10
    bits = vsyms*vlen*bps
    
    refdata = [randint(0,1) for i in range(bits)]
    cmap = [bps]*(vsyms*vlen)
    
    src = gr.vector_source_b(refdata)
    dst = gr.vector_sink_b()
    
    src_map = gr.vector_source_b(cmap)
    s2v = gr.stream_to_vector(gr.sizeof_char, vlen)
    self.tb.connect(src_map,s2v)
    
    dut1 = ofdm.generic_mapper_bcv(vlen)
    dut2 = ofdm.generic_demapper_vcb(vlen)
    
    self.tb.connect(src,dut1,dut2,dst)
    self.tb.connect(s2v,(dut1,1))
    self.tb.connect(s2v,(dut2,1))
    
    self.tb.run()
    
    self.assertEqual(list(dst.data()),refdata)
    
if __name__ == '__main__':
  gr_unittest.main()
