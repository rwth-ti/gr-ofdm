#!/usr/bin/env python

from gnuradio import gr, gr_unittest, eng_notation
import ofdm as ofdm
import numpy

from numpy import exp, concatenate
from gr_tools import fft

import os

class qa_find_cir_shift(gr_unittest.TestCase):
  def setUp (self):
    self.tb = gr.top_block()
    
  def tearDown(self):
    self.tb = None
  
  def simple_test( self, shift ):
    vlen = 256
    cir_len = 12
    tail = vlen - cir_len - shift
    
    cir = [1]*cir_len

    shifted_cir = concatenate( [ [0]*shift, cir, [0]*tail ] )
    
    src = gr.vector_source_c( shifted_cir.tolist() , False, vlen )
    dst = gr.vector_sink_s()
    fft = gr.fft_vcc( vlen, True, [], True )
    
    uut = ofdm.find_cir_shift( vlen, cir_len )
    
    self.tb.connect( src, fft, uut, dst )
    self.tb.run()
    
    d = numpy.array( dst.data() )
    
    self.assertEqual( shift, d[0] )
    
  def profile( self, shift ):
    vlen = 256
    cir_len = 12
    tail = vlen - cir_len - shift
    N = int( 2e6 )
    
    cir = [1]*cir_len

    shifted_cir = concatenate( [ [0]*shift, cir, [0]*tail ] )
    CTF = fft( shifted_cir )
    
    
    src = gr.vector_source_c( CTF, True, vlen )
    limit = gr.head( gr.sizeof_gr_complex * vlen, N )
    
    uut = ofdm.find_cir_shift( vlen, cir_len )
    
    self.tb.connect( src, limit, uut, gr.null_sink( gr.sizeof_short ) )
    r = time_it(self.tb)
    
    print "Expected rate: %s Samples/second" \
      % eng_notation.num_to_str( float(N) * vlen / r ) 
    
    
  def test_001(self):
    self.simple_test(0)

  def test_002(self):
    self.simple_test(5)
    
  def test_003(self):
    self.simple_test(130)    

  def test_004(self):
    self.simple_test(240)
    
  def test_005(self):
    self.profile(10)
    
    
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
