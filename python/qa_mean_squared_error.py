#!/usr/bin/env python

from gnuradio import gr, gr_unittest
import ofdm_swig as ofdm

class qa_mean_squared_error(gr_unittest.TestCase):
  def setUp (self):
    self.tb = gr.top_block()
    
  def tearDown(self):
    self.tb = None
  
  def test_001(self):
    data = [1, 1j, 1+1j]
    ref = [4]
    
    src = gr.vector_source_c(data)
    dst = gr.vector_sink_f()
    
    uut = ofdm.mean_squared_error( 1, 3, False, 1.0 )
    
    self.tb.connect( src, uut, dst )
    self.tb.run()
    
    self.assertEqual( ref, list(dst.data()) )
    
  def test_002(self):
    data = [1, 1j, 1+1j]
    ref = [4]
    
    src = gr.vector_source_c(data,False,3)
    dst = gr.vector_sink_f()
    
    uut = ofdm.mean_squared_error( 3, 1, False, 1.0 )
    
    self.tb.connect( src, uut, dst )
    self.tb.run()
    
    self.assertEqual( ref, list(dst.data()) )
    
  def test_003(self):
    data = [1, 1j, 1+1j]
    ref = [2]
    
    src = gr.vector_source_c(data,False,3)
    dst = gr.vector_sink_f()
    
    uut = ofdm.mean_squared_error( 3, 1, False, 2.0 )
    
    self.tb.connect( src, uut, dst )
    self.tb.run()
    
    self.assertEqual( ref, list(dst.data()) )
    
if __name__ == '__main__':
  gr_unittest.main()
