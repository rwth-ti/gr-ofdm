#!/usr/bin/env python

from gnuradio import gr, gr_unittest, eng_notation
import ofdm.ofdm_swig as ofdm
import numpy

from numpy import exp, concatenate

import os

class qa_postprocess_CTF_estimate(gr_unittest.TestCase):
  def setUp (self):
    self.tb = gr.top_block()
    
  def tearDown(self):
    self.tb = None
  
  def test_001( self ):
    vlen = 256
    N = int( 10 )
    
    ctf = [1.+1.j]*vlen
    
    ref_inv_ctf = 1. / numpy.array( ctf )
    
    ref_disp_ctf = numpy.array( ctf )
    ref_disp_ctf = abs( ref_disp_ctf ) ** 2
    ref_disp_ctf = ref_disp_ctf / sum( ref_disp_ctf ) * vlen
    
    uut = ofdm.postprocess_CTF_estimate( vlen )
    
    src = gr.vector_source_c( ctf, True, vlen )
    dst = gr.vector_sink_c()
    dst2 = gr.vector_sink_f()
    
    limit = gr.head( gr.sizeof_gr_complex * vlen, N )
    
    self.tb.connect( src, limit, uut, 
                     gr.vector_to_stream( gr.sizeof_gr_complex, vlen ), dst )
    self.tb.connect( ( uut, 1 ), 
                     gr.vector_to_stream( gr.sizeof_float, vlen ), dst2 )
    
    self.tb.run()
    
    d1 = numpy.array( dst.data() )
    d2 = numpy.array( dst2.data() )
    
    for i in range( N ):
      self.assertComplexTuplesAlmostEqual( d1[(i*vlen):((i+1)*vlen)], ref_inv_ctf, 3 )
      self.assertFloatTuplesAlmostEqual( ref_disp_ctf, d2[(i*vlen):((i+1)*vlen)], 3 )
 
  def test_002( self ):
    vlen = 256
    N = int( 10 )
    
    ctf = [4.-1.j]*vlen
    
    ref_inv_ctf = 1. / numpy.array( ctf )
    
    ref_disp_ctf = numpy.array( ctf )
    ref_disp_ctf = abs( ref_disp_ctf ) ** 2
    ref_disp_ctf = ref_disp_ctf / sum( ref_disp_ctf ) * vlen
    
    uut = ofdm.postprocess_CTF_estimate( vlen )
    
    src = gr.vector_source_c( ctf, True, vlen )
    dst = gr.vector_sink_c()
    dst2 = gr.vector_sink_f()
    
    limit = gr.head( gr.sizeof_gr_complex * vlen, N )
    
    self.tb.connect( src, limit, uut, 
                     gr.vector_to_stream( gr.sizeof_gr_complex, vlen ), dst )
    self.tb.connect( ( uut, 1 ), 
                     gr.vector_to_stream( gr.sizeof_float, vlen ), dst2 )
    
    self.tb.run()
    
    d1 = numpy.array( dst.data() )
    d2 = numpy.array( dst2.data() )
    
    for i in range( N ):
      self.assertComplexTuplesAlmostEqual( d1[(i*vlen):((i+1)*vlen)], ref_inv_ctf, 3 )
      self.assertFloatTuplesAlmostEqual( ref_disp_ctf, d2[(i*vlen):((i+1)*vlen)], 3 )
      
  def test_100(self):
    vlen = 256
    N = int( 2e6 )
    
    ctf = [1.+1.j]*vlen
    
    uut = ofdm.postprocess_CTF_estimate( vlen )
    
    src = gr.vector_source_c( ctf, True, vlen )
    dst = gr.null_sink( gr.sizeof_gr_complex * vlen )
    dst2 = gr.null_sink( gr.sizeof_float * vlen )
    
    limit = gr.head( gr.sizeof_gr_complex * vlen, N )
    
    self.tb.connect( src, limit, uut,  dst )
    self.tb.connect( ( uut, 1 ),  dst2 )
    
    r = time_it(self.tb)
    
    print "Rate: %s Samples/second" % \
      eng_notation.num_to_str( float(N) * vlen / r )
    
    
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
