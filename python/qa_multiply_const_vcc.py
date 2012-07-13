#!/usr/bin/env python

from gnuradio import gr, gr_unittest, eng_notation
import ofdm.ofdm_swig as ofdm
import numpy

import os

class qa_multiply_const_vcc(gr_unittest.TestCase):
  def setUp (self):
    self.tb = gr.top_block()
    
  def tearDown(self):
    self.tb = None
    
  def test_001(self):
    vlen = 208
    N = int( 1e4 )
    
    data = numpy.repeat( numpy.arange( 100 ), vlen )
    data2 = [2+1j] * vlen
    
    src = gr.vector_source_c( data.tolist(), True, vlen )
    dst = gr.vector_sink_f()
    
    ref = gr.multiply_const_vcc( data2 )
    uut = ofdm.multiply_const_vcc( data2 )
    
     
    ref_stream = gr.vector_to_stream( gr.sizeof_gr_complex, vlen )
    uut_stream = gr.vector_to_stream( gr.sizeof_gr_complex, vlen )
    cmp = gr.sub_cc()
    magsqd = gr.complex_to_mag_squared()
    acc = ofdm.accumulator_ff()
    skiphead = gr.skiphead( gr.sizeof_float, N-1 )
    limit = gr.head( gr.sizeof_float, 1 )
        
    self.tb.connect( src, uut, uut_stream, cmp, magsqd, acc, skiphead, limit, 
                     dst )
    self.tb.connect( src, ref, ref_stream, (cmp,1) )
    
    self.tb.run()
    
    d = dst.data()[0]
    
    self.assertAlmostEqual(d, 0.0)
    
  def test_002(self):
    vlen = 208
    N = int( 1e4 )
    
    data = numpy.repeat( numpy.arange( 100 ), vlen )
    data2 = [-2+1.3j] * vlen
    
    src = gr.vector_source_c( data.tolist(), True, vlen )
    dst = gr.vector_sink_f()
    
    ref = gr.multiply_const_vcc( data2 )
    uut = ofdm.multiply_const_vcc( data2 )
    
    
    ref_stream = gr.vector_to_stream( gr.sizeof_gr_complex, vlen )
    uut_stream = gr.vector_to_stream( gr.sizeof_gr_complex, vlen )
    cmp = gr.sub_cc()
    magsqd = gr.complex_to_mag_squared()
    acc = ofdm.accumulator_ff()
    skiphead = gr.skiphead( gr.sizeof_float, N-1 )
    limit = gr.head( gr.sizeof_float, 1 )
        
    self.tb.connect( src, uut, uut_stream, cmp, magsqd, acc, skiphead, limit, 
                     dst )
    self.tb.connect( src, ref, ref_stream, (cmp,1) )
    
    self.tb.run()
    
    d = dst.data()[0]
    
    self.assertAlmostEqual(d, 0.0)
    
    
  
  def test_100(self):
    vlen = 208
    N = int( 2e6 )
    
    data = [1] * vlen
    data2 = [2] * vlen
    
    src = gr.vector_source_c( data, True, vlen )
    dst = gr.null_sink( gr.sizeof_gr_complex * vlen )
    limit = gr.head( gr.sizeof_gr_complex * vlen, N )
    
    uut = gr.multiply_const_vcc( data2 )
    
    self.tb.connect( src, limit, uut, dst )
    
    r = time_it( self.tb )
    
    print "Rate: %s Samples/second" \
      % eng_notation.num_to_str( float(N) * vlen / r ) 


  def test_101(self):
    vlen = 208
    N = int( 1e7 )
    
    data = [1] * vlen
    data2 = [2] * vlen
    
    src = gr.vector_source_c( data, True, vlen )
    dst = gr.null_sink( gr.sizeof_gr_complex * vlen )
    limit = gr.head( gr.sizeof_gr_complex * vlen, N )
    
    uut = ofdm.multiply_const_vcc( data2 )
    
    self.tb.connect( src, limit, uut, dst )
    
    r = time_it( self.tb )
    
    print "Rate: %s Samples/second" \
      % eng_notation.num_to_str( float(N) * vlen / r )     
    
def time_it(tb):
    start = os.times()
    tb.run()
    stop = os.times()
    delta = map((lambda a, b: a-b), stop, start)
    user, sys, childrens_user, childrens_sys, real = delta
    total_user = user + childrens_user
    total_sys  = sys + childrens_sys
    print "real             %7.3f" % (real,)
    print "user             %7.3f" % (total_user,)
    print "sys              %7.3f" % (total_sys,)
    
    return real

    
if __name__ == '__main__':
  gr_unittest.main()
