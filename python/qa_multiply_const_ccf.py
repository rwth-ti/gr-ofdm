#!/usr/bin/env python

from gnuradio import gr, gr_unittest
import ofdm_swig as ofdm
import numpy

class qa_multiply_const_ccf(gr_unittest.TestCase):
  def setUp (self):
    self.tb = gr.top_block()
    
  def tearDown(self):
    self.tb = None
  
  def test_001(self):
    data = [1.0]*1024
    ref = 4. * numpy.array( data )
    
    src = gr.vector_source_c(data)
    dst = gr.vector_sink_c()
    
    uut = ofdm.multiply_const_ccf( 4. )
    
    self.tb.connect( src, uut, dst )
    self.tb.run()
    
    self.assertEqual( list(ref), list(dst.data()) )
    
  def test_002(self):
    data = [1.0]*1024
    ref = 4. * numpy.array( data )
    
    src = gr.vector_source_c( data, True )
    dst = gr.vector_sink_c()
    limit = gr.head( gr.sizeof_gr_complex, 65536 )
    
    uut = ofdm.multiply_const_ccf( 4. )
    
    self.tb.connect( src, limit, uut, dst )
    self.tb.run()
    
    ref = numpy.concatenate( [ ref ] * 64 )
    self.assertEqual( list(ref), list(dst.data()) )
    
    
if __name__ == '__main__':
  gr_unittest.main()
