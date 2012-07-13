#!/usr/bin/env python

from gnuradio import gr, gr_unittest, eng_notation
import ofdm.ofdm_swig as ofdm
import numpy

from numpy import exp, concatenate
from gr_tools import fft

import os

class qa_channel_equalizer(gr_unittest.TestCase):
  def setUp (self):
    self.tb = gr.top_block()
    
  def tearDown(self):
    self.tb = None
  
  def test_001( self ):
    vlen = 256
    
    blocks = 4
    N = 4
    
    frame_start = concatenate( [ [1], [0]*(blocks-1) ] * N )
    inv_ctf = concatenate( [ [ 0.5 + 1j ] * vlen, [ 0.1 - 2j ] * vlen, 
                             [ -2 - 1.1j ] * vlen, [ 10.2 + 0j ] * vlen ] )
    data = numpy.repeat( numpy.arange(blocks)+1, vlen )
    data = concatenate( [ data ] * N )
    
    ref = [0]*len(data)
    
    for i in range( N ):
      t = inv_ctf[(i*vlen):((i+1)*vlen)]
      for r in range(blocks):
        x = i*vlen*blocks + r*vlen
        for j in range( vlen ):
          ref[x+j] = data[x+j] * t[j]

    src1 = gr.vector_source_c( data.tolist(), False, vlen )
    src2 = gr.vector_source_c( inv_ctf.tolist() , False, vlen )
    src3 = gr.vector_source_b( frame_start.tolist(), False )
    dst = gr.vector_sink_c()
    
    uut = ofdm.channel_equalizer( vlen )
    
    self.tb.connect( src1, ( uut, 0 ) )
    self.tb.connect( src2, ( uut, 1 ) )
    self.tb.connect( src3, ( uut, 2 ) )
    self.tb.connect( uut, gr.vector_to_stream( gr.sizeof_gr_complex, vlen ),
                     dst )
    
    self.tb.run()
    
    d = numpy.array( dst.data() )
    
    self.assertComplexTuplesAlmostEqual( d, ref, 3 )

  def test_002( self ):
    vlen = 256
    
    blocks = 100
    N = 4
    
    frame_start = concatenate( [ [1], [0]*(blocks-1) ] * N )
    inv_ctf = concatenate( [ [ 0.5 + 1j ] * vlen, [ 0.1 - 2j ] * vlen, 
                             [ -2 - 1.1j ] * vlen, [ 10.2 + 0j ] * vlen ] )
    data = numpy.repeat( numpy.arange(blocks)+1, vlen )
    data = concatenate( [ data ] * N )
    
    ref = [0]*len(data)
    
    for i in range( N ):
      t = inv_ctf[(i*vlen):((i+1)*vlen)]
      for r in range(blocks):
        x = i*vlen*blocks + r*vlen
        for j in range( vlen ):
          ref[x+j] = data[x+j] * t[j]

    src1 = gr.vector_source_c( data.tolist(), False, vlen )
    src2 = gr.vector_source_c( inv_ctf.tolist(), False, vlen )
    src3 = gr.vector_source_b( frame_start.tolist(), False )
    dst = gr.vector_sink_c()
    
    uut = ofdm.channel_equalizer( vlen )
    
    self.tb.connect( src1, ( uut, 0 ) )
    self.tb.connect( src2, ( uut, 1 ) )
    self.tb.connect( src3, ( uut, 2 ) )
    self.tb.connect( uut, gr.vector_to_stream( gr.sizeof_gr_complex, vlen ),
                     dst )
    
    self.tb.run()
    
    d = numpy.array( dst.data() )
    
    self.assertComplexTuplesAlmostEqual( d, ref, 3 )

  def test_100( self ):
    vlen = 208
    
    blocks = 12
    N = int( 1e7 )
    
    frame_start = concatenate( [ [1], [0]*(blocks-1) ] )
    inv_ctf = [ 0.5 + 1j ] * vlen
    data = numpy.repeat( numpy.arange(blocks)+1, vlen )
    
    src1 = gr.vector_source_c( data.tolist(), True, vlen )
    src2 = gr.vector_source_c( inv_ctf, True, vlen )
    src3 = gr.vector_source_b( frame_start.tolist(), True )
    
    limit1 = gr.head( gr.sizeof_gr_complex * vlen, N )
    
    uut = ofdm.channel_equalizer( vlen )
    
    self.tb.connect( src1, limit1, ( uut, 0 ) )
    self.tb.connect( src2, ( uut, 1 ) )
    self.tb.connect( src3, ( uut, 2 ) )
    self.tb.connect( uut, gr.null_sink( gr.sizeof_gr_complex * vlen ) )
    
    r = time_it( self.tb )
    

    print "New inverse CTF vector every %d OFDM blocks" % ( blocks )
    print "Rate: %s Samples/second" % \
      eng_notation.num_to_str( float(N) * vlen / r )
      
  def test_101( self ):
    vlen = 208
    
    blocks = 1
    N = int( 4e6 )
    
    frame_start = [1]
    inv_ctf = [ 0.5 + 1j ] * vlen
    data = numpy.repeat( numpy.arange(blocks)+1, vlen )
    
    src1 = gr.vector_source_c( data.tolist(), True, vlen )
    src2 = gr.vector_source_c( inv_ctf, True, vlen )
    src3 = gr.vector_source_b( frame_start, True )
    
    limit1 = gr.head( gr.sizeof_gr_complex * vlen, N )
    
    uut = ofdm.channel_equalizer( vlen )
    
    self.tb.connect( src1, limit1, ( uut, 0 ) )
    self.tb.connect( src2, ( uut, 1 ) )
    self.tb.connect( src3, ( uut, 2 ) )
    self.tb.connect( uut, gr.null_sink( gr.sizeof_gr_complex * vlen ) )
    
    r = time_it( self.tb )
    

    print "New inverse CTF vector every OFDM block"
    print "Rate: %s Samples/second" % \
      eng_notation.num_to_str( float(N) * vlen / r )
      
  def test_102( self ):
    vlen = 208
    
    blocks = 100
    N = int( 1e7 )
    
    frame_start = concatenate( [ [1], [0]*(blocks-1) ] )
    inv_ctf = [ 0.5 + 1j ] * vlen
    data = numpy.repeat( numpy.arange(blocks)+1, vlen )
    
    src1 = gr.vector_source_c( data.tolist(), True, vlen )
    src2 = gr.vector_source_c( inv_ctf, True, vlen )
    src3 = gr.vector_source_b( frame_start.tolist(), True )
    
    limit1 = gr.head( gr.sizeof_gr_complex * vlen, N )
    
    uut = ofdm.channel_equalizer( vlen )
    
    self.tb.connect( src1, limit1, ( uut, 0 ) )
    self.tb.connect( src2, ( uut, 1 ) )
    self.tb.connect( src3, ( uut, 2 ) )
    self.tb.connect( uut, gr.null_sink( gr.sizeof_gr_complex * vlen ) )
    
    r = time_it( self.tb )
    

    print "New inverse CTF vector every %d OFDM blocks" % ( blocks )
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
