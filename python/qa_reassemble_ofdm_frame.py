#!/usr/bin/env python

from gnuradio import gr, gr_unittest, eng_notation
import ofdm.ofdm_swig as ofdm
import numpy

from numpy import concatenate
from numpy.random import randint,random_sample

import os

class qa_reassemble_ofdm_frame(gr_unittest.TestCase):
  def setUp (self):
    self.tb = gr.top_block()
    
  def tearDown(self):
    self.tb = None
  
  def test_001(self):
    N = 1000
    framelength = 12
    vlen = 20
    
    failures = int(0.1 * N)
    
    data = numpy.arange( N ) + 1
    data = numpy.repeat( data, vlen )
    frame_start = [0]*N
    
    for i in range( N / framelength ):
      frame_start[i*framelength] = 1
      
    for x in range(failures):
      frame_start[ randint(0,N) ] = 1
      
    ref = []
    for x in range(N):
      if frame_start[x] != 0:
        complete_frame = True
        for y in range(1,framelength):
          z = x+y
          
          if z >= N:
            complete_frame = False
            break
          
          if frame_start[z] != 0:
            complete_frame = False
            break
        
        if complete_frame:
          ref.extend( data[ (x*vlen) : ((x+framelength)*vlen) ] )
    
    ref = numpy.array( ref, numpy.complex )
    
    src = gr.vector_source_c( data.tolist(), False, vlen )
    dst = gr.vector_sink_c()
    src2 = gr.vector_source_b( frame_start )
    
    uut = ofdm.reassemble_ofdm_frame( vlen, framelength )
    
    self.tb.connect( src, uut, 
                     gr.vector_to_stream( gr.sizeof_gr_complex, vlen ), dst )
    self.tb.connect( src2, (uut,1) )
    
    self.tb.run()
    
    d = numpy.array(dst.data())
    
    self.assertComplexTuplesAlmostEqual(ref,d,5)
    

  def test_002(self):
    N = 1000
    framelength = 12
    vlen = 20
    
    failure_prob = 0.1
    
    data = numpy.arange( N ) + 1
    data = numpy.repeat( data, vlen )
    frame_start = [0]*N
    
    for i in range( N / framelength ):
      if random_sample() > failure_prob:
        frame_start[i*framelength] = 1
      
    ref = []
    for x in range(N):
      if frame_start[x] != 0:
        complete_frame = True
        for y in range(1,framelength):
          z = x+y
          
          if z >= N:
            complete_frame = False
            break
          
          if frame_start[z] != 0:
            complete_frame = False
            break
        
        if complete_frame:
          ref.extend( data[ (x*vlen) : ((x+framelength)*vlen) ] )
    
    ref = numpy.array( ref, numpy.complex )
    
    src = gr.vector_source_c( data.tolist(), False, vlen )
    dst = gr.vector_sink_c()
    src2 = gr.vector_source_b( frame_start )
    
    uut = ofdm.reassemble_ofdm_frame( vlen, framelength )
    
    self.tb.connect( src, uut, 
                     gr.vector_to_stream( gr.sizeof_gr_complex, vlen ), dst )
    self.tb.connect( src2, (uut,1) )
    
    self.tb.run()
    
    d = numpy.array(dst.data())
    
    self.assertComplexTuplesAlmostEqual(ref,d,5)
    
    
  def test_100(self):
    N = 10
    M = int(1e6)
    framelength = 12
    vlen = 208
    
    data = numpy.arange( N ) + 1
    data = numpy.repeat( data, vlen )
    frame_start = [0]*N
    
    for i in range( N / framelength ):
      frame_start[i*framelength] = 1
      
    
    src = gr.vector_source_c( data.tolist(), True, vlen )
    dst = gr.null_sink( gr.sizeof_gr_complex * vlen )
    src2 = gr.vector_source_b( frame_start, True )
    
    uut = ofdm.reassemble_ofdm_frame( vlen, framelength )
    
    limit2 = gr.head( gr.sizeof_char, N * M )
    self.tb.connect( src, uut,  dst )
    self.tb.connect( src2, limit2, (uut,1) )
    
    r = time_it( self.tb )
    
    print "Rate: %s Samples/second" % \
      eng_notation.num_to_str( float(N * M) * vlen / r )
    
    
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
