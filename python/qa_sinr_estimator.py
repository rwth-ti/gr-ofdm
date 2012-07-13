#!/usr/bin/env python

from gnuradio import gr, gr_unittest, eng_notation
import ofdm.ofdm_swig as ofdm
import numpy
from snr_estimator import milans_sinr_sc_estimator, milans_sinr_sc_estimator2, milans_sinr_sc_estimator3

import os

class qa_snr_estimator(gr_unittest.TestCase):
  def setUp (self):
    self.tb = gr.top_block()
    
  def tearDown(self):
    self.tb = None
    
  def test_001(self):
    L=8
    vlen = 256
    data = [1.0]*vlen
    data1 = [1]*vlen
    vlen1=vlen*(L-1)/L
    ref_data = [0.0]*vlen1
    ref = numpy.array( ref_data )
    
    src = gr.vector_source_c(data,False,vlen)
    src1 = gr.vector_source_c(data1,False,vlen)
    
    dst = gr.vector_sink_f(vlen1)
    
    uut = ofdm.sinr_estimator(vlen, L)
    
    self.tb.connect( src, (uut,0), dst )
    self.tb.connect( src1, (uut,1))
    self.tb.run()
    
    self.assertEqual( list(ref), list(dst.data()) )
    
  def test_002(self):
    L=8
    vlen = 256
    
    dd = []
    for i in range (vlen/L):
        dd.extend([i*L])
    
    data = [1.0]*vlen
    data1 = [1]*vlen
    ref_data = [0.0]*vlen
    ref = numpy.array( ref_data )
    
    src = gr.vector_source_c(data,False,vlen)
    src1 = gr.vector_source_c(data1,False,vlen)
    
    dst = gr.vector_sink_f(vlen)
    
    uut = ofdm.sinr_estimator(vlen, L)
    uut1 = ofdm.sinr_interpolator(vlen, L, dd)
    
    self.tb.connect( src, (uut,0), uut1,dst )
    self.tb.connect( src1, (uut,1))
    self.tb.run()
    
    self.assertEqual( list(ref), list(dst.data()) )
    
  def test_003(self):
    L=8
    vlen = 256
    
    dd = []
    for i in range (vlen/L):
        dd.extend([i*L])
    
    data = [1.0]*vlen
    data1 = [1]*vlen
    ref_data = [0.0]*vlen
    ref = numpy.array( ref_data )
    ref1 = 0.0
    
    src = gr.vector_source_c(data,False,vlen)
    src1 = gr.vector_source_c(data1,False,vlen)
    
    dst = gr.vector_sink_f(vlen)
    dst1 = gr.vector_sink_f()
    
    uut = ofdm.sinr_estimator2(vlen, L)
    uut1 = ofdm.sinr_interpolator(vlen, L, dd)
    
    self.tb.connect( src, (uut,0), dst )
    self.tb.connect( src1, (uut,1))
    self.tb.connect( (uut,1), dst1)
    self.tb.run()
    
    self.assertEqual( list(ref), list(dst.data()) )
    self.assertEqual( ref1, dst1.data()[0])
  
  def test_100(self):
    vlen = 256
    L = 8
    N = int( 6e6 )
    
    data = [1] * vlen
    data1 = [2] * vlen
    
    src = gr.vector_source_c( data, True, vlen )
    src1 = gr.vector_source_c( data1, True, vlen )
    dst = gr.null_sink( gr.sizeof_float*vlen )
    dst1 = gr.null_sink( gr.sizeof_float )
    limit = gr.head( gr.sizeof_gr_complex * vlen, N )
    limit1 = gr.head( gr.sizeof_gr_complex * vlen, N )
    
    uut = milans_sinr_sc_estimator2( vlen, vlen, L )
    
    self.tb.connect( src, limit, uut, dst )
    self.tb.connect( src1, limit1, (uut,1))
    self.tb.connect( (uut,1), dst1)
    
    r = time_it( self.tb )
    
    print "Rate: %s Samples/second" \
      % eng_notation.num_to_str( float(N) * vlen / r )  
    
  
  def test_101(self):
    vlen = 256
    L = 8
    N = int( 6e6 )
    
    data = [1] * vlen
    data1 = [2] * vlen
    
    src = gr.vector_source_c( data, True, vlen )
    src1 = gr.vector_source_c( data1, True, vlen )
    dst = gr.null_sink( gr.sizeof_float*vlen )
    dst1 = gr.null_sink( gr.sizeof_float )
    limit = gr.head( gr.sizeof_gr_complex * vlen, N )
    limit1 = gr.head( gr.sizeof_gr_complex * vlen, N )
    
    uut = milans_sinr_sc_estimator3( vlen, vlen, L )
    
    self.tb.connect( src, limit, uut, dst )
    self.tb.connect( src1, limit1, (uut,1))
    self.tb.connect( (uut,1), dst1)
    
    r = time_it( self.tb )
    
    print "Rate: %s Samples/second" \
      % eng_notation.num_to_str( float(N) * vlen / r ) 

  def test_102(self):
    vlen = 256
    L = 8
    N = int( 6e6 )
    
    data = [1] * vlen
    data1 = [2] * vlen
    
    src = gr.vector_source_c( data, True, vlen )
    src1 = gr.vector_source_c( data1, True, vlen )
    dst = gr.null_sink( gr.sizeof_float*vlen )
    dst1 = gr.null_sink( gr.sizeof_float )
    limit = gr.head( gr.sizeof_gr_complex * vlen, N )
    limit1 = gr.head( gr.sizeof_gr_complex * vlen, N )
    
    uut = milans_sinr_sc_estimator( vlen, vlen, L )
    
    self.tb.connect( src, limit, uut, dst )
    self.tb.connect( src1, limit1, (uut,1))
    self.tb.connect( (uut,1), dst1)
    
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
