#!/usr/bin/env python

from gnuradio import gr, gr_unittest
import ofdm as ofdm
import numpy


class qa_bernoulli_bit_src (gr_unittest.TestCase):
  def setUp (self):
    self.tb = gr.top_block ("test_block")

  def tearDown (self):
    self.tb = None

  def std_test(self, p, N):
    N = int( N )
    
    src = ofdm.bernoulli_bit_src( p )    
    c2f = gr.char_to_float()
    acc = ofdm.accumulator_ff()
    dst = gr.vector_sink_f()
    
    skiphead = gr.skiphead( gr.sizeof_float, N-1 )
    limit = gr.head( gr.sizeof_float, 1 )
    
    self.tb.connect( src, c2f, acc, skiphead, limit, dst )
    self.tb.run()
    
    data = numpy.array( dst.data() )
    
    m = data[len(data)-1]
    exp = N * p
    
    print "Bernoulli experiment N =",N,"expected",exp,"and is",m
    print "Relative error:", abs( m/exp - 1.0 )
    
    self.assertEqual( len(data), 1 )
    self.assert_( numpy.abs( m - exp ) < 0.05 * exp )
    
  def test_001(self):
    self.std_test( 0.5 , 10e6 )

  def test_002(self):
    self.std_test( 1e-1, 10e6 )

  def test_003(self):
    self.std_test( 1e-2 , 10e6 )

  def test_004(self):
    self.std_test( 1e-4 , 10e7 )

#  def test_005(self):
#    self.std_test( 1e-7 , 10e10 )


if __name__ == '__main__':
  gr_unittest.main()

