#!/usr/bin/env python

from gnuradio import gr, gr_unittest, eng_notation
import ofdm_swig as ofdm
import numpy
from snr_estimator import milans_snr_estimator

import os

class qa_snr_estimator(gr_unittest.TestCase):
  def setUp (self):
    self.tb = gr.top_block()
    
  def tearDown(self):
    self.tb = None
    

   
  def test_001(self):
      
      
    vlen = 256
    L = 8
    N = int( 4e6 )
    #u = range (vlen/L*(L-1))
    #zeros_ind= map(lambda z: z+1+z/(L-1),u)
    #data = [(1.0-0.2/numpy.sqrt(L))*numpy.sqrt(L)+ 0.1] * vlen
    data = [1] * vlen
    
#    for x in zeros_ind:
#     data[x]=0.1
    limit = gr.head( gr.sizeof_gr_complex * vlen, N )


    
    src = gr.vector_source_c( data, True, vlen )
    dst = gr.vector_sink_f()
    dst1 = gr.vector_sink_f()

    
    
    uut = ofdm.snr_estimator( vlen, L )
    snrm= gr.single_pole_iir_filter_ff(0.1)
    self.tb.connect( src, limit, uut,snrm, dst )
    self.tb.connect( (uut,1), dst1)
    
    self.tb.run()
    
    d = dst.data()[0]
    d1 = dst1.data()[0]
     
    self.assertAlmostEqual(d,0.0)
    self.assertAlmostEqual(d1,1.0)
    
  
  def test_100(self):
    vlen = 256
    L = 8
    N = int( 4e6 )
    
    data = [1] * vlen
    #data2 = [2] * vlen
    
    src = gr.vector_source_c( data, True, vlen )
    dst = gr.null_sink( gr.sizeof_float )
    dst1 = gr.null_sink( gr.sizeof_float )
    limit = gr.head( gr.sizeof_gr_complex * vlen, N )
    
    uut = ofdm.snr_estimator( vlen, L )
    
    self.tb.connect( src, limit, uut, dst )
    self.tb.connect( (uut,1), dst1)
    
    r = time_it( self.tb )
    
    print "Rate: %s Samples/second" \
      % eng_notation.num_to_str( float(N) * vlen / r ) 

  def test_101(self):
    vlen = 256
    L = 8
    N = int( 4e6 )
    
    data = [1] * vlen
    #data2 = [2] * vlen
    
    src = gr.vector_source_c( data, True, vlen )
    dst = gr.null_sink( gr.sizeof_float )
    dst1 = gr.null_sink( gr.sizeof_float )
    limit = gr.head( gr.sizeof_gr_complex * vlen, N )
    
    uut = ofdm.snr_estimator( vlen, L )
    scsnrdb = gr.single_pole_iir_filter_ff(0.1)
    snrm = self._snr_measurement = gr.nlog10_ff(10,1,0)
    self.tb.connect( src, limit, uut,scsnrdb,snrm, dst )
    self.tb.connect( (uut,1), dst1)
    
    r = time_it( self.tb )
    
    print "Rate: %s Samples/second" \
      % eng_notation.num_to_str( float(N) * vlen / r ) 
 
  def test_102(self):
    vlen = 256
    L = 8
    N = int( 4e6 )
    
    data = [1] * vlen
    #data2 = [2] * vlen
    
    src = gr.vector_source_c( data, True, vlen )
    dst = gr.null_sink( gr.sizeof_float )
    limit = gr.head( gr.sizeof_gr_complex * vlen, N )
    
    uut = milans_snr_estimator( vlen, vlen, L )
    
    self.tb.connect( src, limit, uut,dst )
    
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
