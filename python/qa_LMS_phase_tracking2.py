#!/usr/bin/env python

from gnuradio import gr, gr_unittest, eng_notation
import ofdm as ofdm
import numpy

from numpy import exp, concatenate
from gr_tools import fft

from preambles import default_block_header

import os

class qa_LMS_phase_tracking2(gr_unittest.TestCase):
  def setUp (self):
    self.tb = gr.top_block()
    
  def tearDown(self):
    self.tb = None
    
  def test_001(self):
    self.simple_test( 0.005, 0.01 )

  def test_002(self):
    self.simple_test( -0.005, 0.01 )
    
  def test_003(self):
    self.simple_test( 0.005, -0.01 )

  def test_004(self):
    self.simple_test( -0.005, -0.01 )
    
  def test_005(self):
    self.simple_test( 0.0, 0.1 )
    
  def test_006(self):
    self.simple_test( 0.005, 0.0 )
    
  def test_007(self):
    self.simple_test( 0.01, -0.01 )
    
  def test_008(self):
    self.simple_test( 0.01, 0.01 )
    
  def test_009(self):
    self.simple_test2(0.001, 0.1)
    
  def test_010(self):
    self.simple_test3( 0.005, 0.01 )

  def test_011(self):
    self.simple_test3( -0.005, 0.01 )
    
  def test_012(self):
    self.simple_test3( 0.005, -0.01 )

  def test_013(self):
    self.simple_test3( -0.005, -0.01 )
    
  def test_014(self):
    self.simple_test3( 0.0, 0.1 )
    
  def test_015(self):
    self.simple_test3( 0.005, 0.0 )
    
  def test_016(self):
    self.simple_test3( 0.01, -0.01 )
    
  def test_017(self):
    self.simple_test3( 0.01, 0.01 )
      
  def simple_test( self, gamma, beta ):
    vlen = 208
    N = 10
    pcount = 8
    pdist = vlen / pcount
    assert( ( pdist % 2 ) == 0 )
    
    nondata_blocks = []
    pilot_subc = numpy.arange(pcount) * pdist + pdist/2 - vlen/2
    assert( pilot_subc[0] == - pilot_subc[len(pilot_subc)-1] )

    data = [1.+0.j] * vlen
    frame_start = [0] * N
    
#    gamma = 0.005
#    beta = 0.01
    
    sub_dc = vlen/2
    
    ind_range = numpy.arange( vlen ) - vlen/2
    assert( ind_range[0] == -vlen/2 )
    
    phase_offset = ind_range * gamma + numpy.ones(vlen) * beta
    assert( phase_offset[sub_dc] == beta )
    
    phase_offset = exp( 1j * phase_offset )
    
    data = data * phase_offset
    data = concatenate( [data] * N )
    
    src = gr.vector_source_c( data, False, vlen )
    src2 = gr.vector_source_b( frame_start, False )
    dst = gr.vector_sink_c()
    
    uut = ofdm.LMS_phase_tracking2( vlen, pilot_subc.tolist(), nondata_blocks )
    
    self.tb.connect( src, uut, 
                     gr.vector_to_stream( gr.sizeof_gr_complex, vlen ), dst ) 
    self.tb.connect( src2, ( uut, 1 ) )
    
    self.tb.run()
    
    d = numpy.array( dst.data() )
    ad = numpy.angle(d)
    
    self.assertFloatTuplesAlmostEqual( numpy.zeros(len(ad)), ad, 3 )
    
    
  def simple_test2( self, gamma, beta ):
    vlen = 208
    N = 20
    pcount = 8
    pdist = vlen / pcount
    assert( ( pdist % 2 ) == 0 )
    
    nondata_blocks = [0, 1]
    pilot_subc = numpy.arange(pcount) * pdist + pdist/2 - vlen/2
    assert( pilot_subc[0] == - pilot_subc[len(pilot_subc)-1] )

    data = [1.+0.j] * vlen
    frame_start = [0] * N
    frame_start[0] = 1
    
    sub_dc = vlen/2
    
    ind_range = numpy.arange( vlen ) - vlen/2
    assert( ind_range[0] == -vlen/2 )
    
    phase_offset = ind_range * gamma + numpy.ones(vlen) * beta
    assert( phase_offset[sub_dc] == beta )
    phase= phase_offset
    
    phase_offset = exp( 1j * phase_offset )
    
    data = data * phase_offset
    data = concatenate( [data] * N )
    
    src = gr.vector_source_c( data, False, vlen )
    src2 = gr.vector_source_b( frame_start, False )
    dst = gr.vector_sink_c()
    
    uut = ofdm.LMS_phase_tracking2( vlen, pilot_subc.tolist(), nondata_blocks )
    
    self.tb.connect( src, uut, 
                     gr.vector_to_stream( gr.sizeof_gr_complex, vlen ), dst ) 
    self.tb.connect( src2, ( uut, 1 ) )
    
    self.tb.run()
    
    d = numpy.array( dst.data() )
    
    ad = numpy.angle( d[ (len(nondata_blocks)*vlen):len(d) ] )
    ad2 = numpy.angle( d[ 0 : (len(nondata_blocks)*vlen) ] )
    
    self.assertFloatTuplesAlmostEqual( 
      concatenate( [phase]*len(nondata_blocks) ), ad2, 3 )
    
    self.assertFloatTuplesAlmostEqual( numpy.zeros(len(ad)), ad, 3 )
    
    
  def simple_test3( self, gamma, beta ):
    vlen = 208
    N = 20
    pcount = 8
    pdist = vlen / pcount
    assert( ( pdist % 2 ) == 0 )
    
#    bh = default_block_header( vlen, fftlen, None)
    
    nondata_blocks = [0, 1]
    pilot_subc = numpy.arange(pcount) * pdist + pdist/2 - vlen/2
    assert( pilot_subc[0] == - pilot_subc[len(pilot_subc)-1] )
    
    
    shifted_pilot_subc = pilot_subc + vlen/2
    

    data = numpy.array( [1.+1j] * vlen )
    frame_start = [0] * N
    frame_start[0] = 1
    
    data[ shifted_pilot_subc ] = 1.0
        
    sub_dc = vlen/2
    
    ind_range = numpy.arange( vlen ) - vlen/2
    assert( ind_range[0] == -vlen/2 )
    
    phase_offset = ind_range * gamma + numpy.ones(vlen) * beta
    assert( phase_offset[sub_dc] == beta )
    phase= phase_offset
    

    phase_offset = exp( 1j * phase_offset )
    
    refdata = data
    data = data * phase_offset
    data = concatenate( [data] * N )
    
    src = gr.vector_source_c( data, False, vlen )
    src2 = gr.vector_source_b( frame_start, False )
    dst = gr.vector_sink_c()
    
    uut = ofdm.LMS_phase_tracking2( vlen, pilot_subc.tolist(), nondata_blocks )
    
    self.tb.connect( src, uut, 
                     gr.vector_to_stream( gr.sizeof_gr_complex, vlen ), dst ) 
    self.tb.connect( src2, ( uut, 1 ) )
    
    self.tb.run()
    
    d = numpy.array( dst.data() )
    
    ad = numpy.angle( d[ (len(nondata_blocks)*vlen):len(d) ] )
    ad2 = numpy.angle( d[ 0 : (len(nondata_blocks)*vlen) ] )
    
    ref_ad = []
    for x in range(len(ad)/vlen):
      ref_ad.extend( numpy.angle(refdata) )
    
    self.assertFloatTuplesAlmostEqual( 
      concatenate([phase + numpy.angle(refdata)]*len(nondata_blocks)), ad2, 3 )
    
    self.assertFloatTuplesAlmostEqual( ref_ad, ad, 3 )
    
    
  def test_30( self ):
    
    gamma = 0.001
    beta = -0.1
    
    vlen = 208
    N = 20
    M = 5
    pcount = 8
    pdist = vlen / pcount
    assert( ( pdist % 2 ) == 0 )
    
    nondata_blocks = [0, 1]
    pilot_subc = numpy.arange(pcount) * pdist + pdist/2 - vlen/2
    assert( pilot_subc[0] == - pilot_subc[len(pilot_subc)-1] )

    data = [1.+0.j] * vlen
    frame_start = [0] * N
    frame_start[0] = 1
    
    sub_dc = vlen/2
    
    ind_range = numpy.arange( vlen ) - vlen/2
    assert( ind_range[0] == -vlen/2 )
    
    phase_offset = ind_range * gamma + numpy.ones(vlen) * beta
    assert( phase_offset[sub_dc] == beta )
    phase = phase_offset
    
    phase_offset = exp( 1j * phase_offset )
    
    data = data * phase_offset
    data = concatenate( [data] * N )
    
    src = gr.vector_source_c( data, True, vlen )
    src2 = gr.vector_source_b( frame_start, True )
    dst = gr.vector_sink_c()
    
    limit2 = gr.head( gr.sizeof_char, N * M )
    
    uut = ofdm.LMS_phase_tracking2( vlen, pilot_subc.tolist(), nondata_blocks )
    
    self.tb.connect( src, uut, 
                     gr.vector_to_stream( gr.sizeof_gr_complex, vlen ), dst ) 
    self.tb.connect( src2, limit2, ( uut, 1 ) )
    
    self.tb.run()
    
    d = numpy.array( dst.data() )
    
    for i in range( M ):
      xx = i * N * vlen
      ad = numpy.angle( d[ (xx+len(nondata_blocks)*vlen):(xx+N*vlen) ] )
      ad2 = numpy.angle( d[ xx : (xx+len(nondata_blocks)*vlen) ] )
      
      self.assertFloatTuplesAlmostEqual( 
        concatenate( [phase]*len(nondata_blocks) ), ad2, 3 )
      
      self.assertFloatTuplesAlmostEqual( numpy.zeros(len(ad)), ad, 3 )
      
      
      
  def test_100( self ):
    gamma = 0.001
    beta = -0.1
    
    N = int(2e6)
    
    vlen = 208
    pcount = 8
    pdist = vlen / pcount
    assert( ( pdist % 2 ) == 0 )
    
    nondata_blocks = []
    pilot_subc = numpy.arange(pcount) * pdist + pdist/2 - vlen/2
    assert( pilot_subc[0] == - pilot_subc[len(pilot_subc)-1] )

    data = [1.+0.j] * vlen
    frame_start = [0] 

    sub_dc = vlen/2
    
    ind_range = numpy.arange( vlen ) - vlen/2
    assert( ind_range[0] == -vlen/2 )
    
    phase_offset = ind_range * gamma + numpy.ones(vlen) * beta
    assert( phase_offset[sub_dc] == beta )
    
    phase_offset = exp( 1j * phase_offset )
    
    data = data * phase_offset
    
    src = gr.vector_source_c( data, True, vlen )
    src2 = gr.vector_source_b( frame_start, True )
    dst = gr.null_sink( gr.sizeof_gr_complex * vlen )
    
    limit2 = gr.head( gr.sizeof_char, N )
    
    uut = ofdm.LMS_phase_tracking2( vlen, pilot_subc.tolist(), nondata_blocks )
    
    self.tb.connect( src, uut, dst ) 
    self.tb.connect( src2, limit2, ( uut, 1 ) )
    
    r = time_it( self.tb )
    
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
