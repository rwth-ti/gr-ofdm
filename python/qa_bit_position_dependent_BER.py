#!/usr/bin/env python

from gnuradio import gr, gr_unittest, eng_notation
import ofdm as ofdm
import numpy

from numpy import exp, concatenate
from numpy.random import random_integers

import os

class qa_bit_position_dependent_BER(gr_unittest.TestCase):
  def setUp (self):
    self.tb = gr.top_block()
    
  def tearDown(self):
    self.tb = None
  
  def test_001( self ):
    vlen = 256
    N = 100000
    
    refdata = random_integers(0, 1, N)
    data = random_integers(0, 1, N)
    
    ref = numpy.array([0]*vlen)
    for x in range(len(data)):
      ref[x%vlen] += 1 if refdata[x] != data[x] else 0
      
    src0 = gr.vector_source_b( refdata.tolist() )
    src1 = gr.vector_source_b( data.tolist() )
    src2 = gr.vector_source_i( [vlen]*N )
    
    uut = ofdm.bit_position_dependent_BER( "test" )
    
    self.tb.connect( src0, ( uut, 0 ) )
    self.tb.connect( src1, ( uut, 1 ) )
    self.tb.connect( src2, ( uut, 2 ) )
    
    self.tb.run()
    
    ret = numpy.array( uut.get_cntr_vec() )
    
    self.assert_( (ret==ref).all() )
    
  
  def test_002( self ):
    vlen = 200
    N = 100000
    _n = N / vlen
    
    refdata = random_integers(0, 1, N)
    data = random_integers(0, 1, N)
    
    
    ref = numpy.array([0]*(vlen/2))
    for x in range(N/2,N):
      ref[x%(vlen/2)] += 1 if refdata[x] != data[x] else 0
    
    vlen = concatenate( [ [vlen]*(_n/2),[vlen/2]*(_n)] ) 
    src0 = gr.vector_source_b( refdata.tolist() )
    src1 = gr.vector_source_b( data.tolist() )
    src2 = gr.vector_source_i( vlen.tolist() )
    
    uut = ofdm.bit_position_dependent_BER( "test" )
    
    self.tb.connect( src0, ( uut, 0 ) )
    self.tb.connect( src1, ( uut, 1 ) )
    self.tb.connect( src2, ( uut, 2 ) )
    
    if os.path.exists("test_000.uint"):
      os.remove("test_000.uint")
    
    self.assert_( not os.path.exists("test_000.uint") )
    
    self.tb.run()
    
    ret = numpy.array( uut.get_cntr_vec() )

    self.assert_( (ret==ref).all() )
    
    self.assert_( os.path.exists("test_000.uint"))  
    
    
  def test_003( self ):
    vlen = 200
    N = 100000
    _n = N / vlen
    
    refdata = random_integers(0, 1, N)
    data = random_integers(0, 1, N)
    
    vlen = concatenate( [ [vlen]*(_n/2),[vlen/2]*(_n/2),[vlen/4]*(_n)] ) 
    src0 = gr.vector_source_b( refdata.tolist() )
    src1 = gr.vector_source_b( data.tolist() )
    src2 = gr.vector_source_i( vlen.tolist() )
    
    uut = ofdm.bit_position_dependent_BER( "test" )
    
    self.tb.connect( src0, ( uut, 0 ) )
    self.tb.connect( src1, ( uut, 1 ) )
    self.tb.connect( src2, ( uut, 2 ) )
    
    if os.path.exists("test_000.uint"):
      os.remove("test_000.uint")
    if os.path.exists("test_001.uint"):
      os.remove("test_001.uint")
      
    self.assert_( not os.path.exists("test_000.uint") )
    self.assert_( not os.path.exists("test_001.uint") )
    
    self.tb.run()
    
    self.assert_( os.path.exists("test_000.uint"))
    self.assert_( os.path.exists("test_001.uint"))

    
if __name__ == '__main__':
  gr_unittest.main()
