#!/usr/bin/env python

from gnuradio import gr, gr_unittest, eng_notation
import ofdm as ofdm
import numpy

from numpy import exp, concatenate
from gr_tools import fft

import os

class qa_CTF_MSE_enhancer(gr_unittest.TestCase):
  def setUp (self):
    self.tb = gr.top_block()
    
  def tearDown(self):
    self.tb = None
  
  def simple_test( self, shift ):
    vlen = 256
    cir_len = 12
    tail = vlen - cir_len - shift
    
    cir = [1.0+0.0j]*cir_len
    
    if shift > ( vlen - cir_len ):
      shifted_cir = [0.1+0.0j] * vlen
      shifted_cir[ shift : vlen ] = cir[ 0 : (vlen-shift) ]
      shifted_cir[ 0 : (cir_len - vlen + shift) ] = cir[ (vlen-shift) : cir_len ]
      ref_cir = [0.0j] * vlen
      ref_cir[ shift : vlen ] = cir[ 0 : (vlen-shift) ]
      ref_cir[ 0 : (cir_len - vlen + shift) ] = cir[ (vlen-shift) : cir_len ]

    else:
      shifted_cir = concatenate( [ [0.1]*shift, cir, [0.1]*tail ] )
      ref_cir =  concatenate( [ [0]*shift, cir, [0]*tail ] )
    
    src = gr.vector_source_c( shifted_cir, False, vlen )
    dst = gr.vector_sink_c()
    fft = gr.fft_vcc( vlen, True, [], True )
    ifft = gr.fft_vcc( vlen, False, [], True )
    ifft_scale = gr.multiply_const_vcc( [1./vlen]*vlen )
    
    uut = ofdm.CTF_MSE_enhancer( vlen, cir_len )
    
    self.tb.connect( src, fft, uut, ifft, ifft_scale,
                     gr.vector_to_stream( gr.sizeof_gr_complex, vlen ), dst )
    self.tb.run()
    
    d = numpy.array( dst.data(), numpy.complex )
    
    self.assertComplexTuplesAlmostEqual( ref_cir, d, 3 )

    
  def profile( self, shift ):
    vlen = 256
    cir_len = 12
    tail = vlen - cir_len - shift
    N = int( 1e6 )
    
    cir = [1]*cir_len

    shifted_cir = concatenate( [ [0.1]*shift, cir, [0.1]*tail ] )
    CTF = fft( shifted_cir )
    
    
    src = gr.vector_source_c( CTF, True, vlen )
    limit = gr.head( gr.sizeof_gr_complex * vlen, N )
    
    uut = ofdm.CTF_MSE_enhancer( vlen, cir_len )
    
    self.tb.connect( src, limit, uut, 
                     gr.null_sink( gr.sizeof_gr_complex * vlen ) )
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
    self.simple_test(244)
    
  def test_005(self):
    self.simple_test(255)
    
  def test_100(self):
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
