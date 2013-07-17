#!/usr/bin/env python

from gnuradio import gr, gr_unittest
import ofdm as ofdm
import numpy


class qa_complex_white_noise (gr_unittest.TestCase):
  def setUp (self):
    self.tb = gr.top_block ("test_block")

  def tearDown (self):
    self.tb = None

  def stdtest ( self, mean, sigma, N ):    
    N = int(N)
    
    self.tearDown()
    
    for i in range(1):
      self.setUp()
        
      src = ofdm.complex_white_noise( mean, sigma )
      limit = gr.head( gr.sizeof_gr_complex, N )
      dst = gr.vector_sink_c()
      
      self.tb.connect( src, limit, dst )
      self.tb.run()
      
      data = numpy.array( dst.data() )
      
      m = sum(data)/N
      v = sum((numpy.absolute(data - m))**2)/(N-1)
      o = numpy.sqrt(v)
      
      print "Short time expectation of mean: ",m
      print "Short time expectation of standard deviation: ",o
      
          
      self.assertEqual(len(data),N)
      self.assert_(  numpy.abs(o-sigma) < 0.001 * sigma )
      
      self.tearDown()
    
  def test_001(self):
    self.stdtest( 0.0,    10.0 , 10e6 )
    
  def test_002(self):
    self.stdtest( -10.0,  16.0 , 10e6 )
    
  def test_003(self):
    self.stdtest( 2.2,     4.0 , 10e6 )
    
  def test_004(self):
    mean1 = 1.0+4.0j
    mean2 = 2.0-1.0j
    sigma1 = 2.0
    sigma2 = 4.0
    N = int( 10e6 )
    
    src1 = ofdm.complex_white_noise( mean1, sigma1 )
    src2 = ofdm.complex_white_noise( mean2, sigma2 )
    add = gr.add_cc()
    limit1 = gr.head( gr.sizeof_gr_complex, N )
    limit2 = gr.head( gr.sizeof_gr_complex, N )
    dst = gr.vector_sink_c()
    
    dst1 = gr.vector_sink_c()
    dst2 = gr.vector_sink_c()
    
    self.tb.connect( src1, limit1, add, dst )
    self.tb.connect( src2, limit2, (add,1))
    self.tb.connect( limit1, dst1 )
    self.tb.connect( limit2, dst2 )
    self.tb.run()
    
    data = numpy.array( dst.data() )
    data1 = numpy.array( dst1.data() )
    data2 = numpy.array( dst2.data() )
    
    m = sum(data)/N
    v = sum((numpy.absolute(data - m))**2)/(N-1)
    o = numpy.sqrt(v)

    mult_mean = sum(data1  *  data2) / N
    
    print mult_mean, mean1*mean2
    
    exp_mult_mean = mean1*mean2 # stochastic independence
    exp_mean = mean1+mean2
    expected_var = sigma1**2 + sigma2**2
    
    print "Short time expectation of multiplied signals: ",mult_mean
    print "Short time expectation of mean: ",m
    print "Short time expectation of standard deviation: ",o
    
    self.assertEqual(len(data),N)
    self.assert_( numpy.abs(m - (exp_mean)) < 0.001 * abs(exp_mean) )
    self.assert_( numpy.abs(v-expected_var) < 0.001 * expected_var )
    self.assert_( numpy.abs(mult_mean - exp_mult_mean ) < 0.001 * abs(mult_mean) )
    
    
  def test_005(self):
    mean = 0.0
    sigma = 10.0
    N = int( 10e6 )
    
    src = ofdm.complex_white_noise( mean, sigma )
    limit = gr.head( gr.sizeof_gr_complex, N )
    dst = gr.vector_sink_c()
    
    self.tb.connect( src, limit, dst )
    self.tb.run()
    
    data = numpy.array( dst.data() )
    
    p = sum((numpy.absolute(data))**2)/N
    
    print "Short time expectation of signal power: ",p
    
        
    self.assertEqual(len(data),N)
    self.assert_(  numpy.abs(p-sigma**2) < 0.01 * sigma**2 )
    
  def test_006(self):
    mean = 0.0
    sigma = 10.0
    N = int( 10e6 )
    
    f0 = 1.0
    f1 = 0.5
    
    src = ofdm.complex_white_noise( mean, sigma )
    limit = gr.head( gr.sizeof_gr_complex, N )
    filter = gr.fir_filter_ccf( 1, [f0, f1] )
    dst = gr.vector_sink_c()
    
    self.tb.connect( src, filter, limit, dst )
    self.tb.run()
    
    data = numpy.array( dst.data() )
    
    exp_R0 = (sigma*f0)**2 + (sigma*f1)**2
    exp_R1 = sigma**2 * f1
    exp_R2 = 0.0
    
    R0 = sum( data * numpy.conjugate(data) ) / N
    R1 = sum( data[0:len(data)-1] * numpy.conjugate( data[1::] ) )/(N-1)
    R2 = sum( data[0:len(data)-2] * numpy.conjugate( data[2::] ) )/(N-2)
    
    print "Autocorrelation of filtered noise, t=0:", R0
    print "Autocorrelation of filtered noise, t=1:", R1
    print "Autocorrelation of filtered noise, t=2:", R2
    
    self.assertEqual( len(data), N )
    self.assert_( numpy.abs(R0 - exp_R0) < 0.01 * exp_R0 )
    self.assert_( numpy.abs(R1 - exp_R1) < 0.01 * exp_R1 )
    self.assert_( numpy.abs(R2 - exp_R2) < 0.1 )

  def test_007 ( self ):
    mean = 1.0
    sigma = 2.0
    K = 100
        
    N = int( 10e6 )
    
    self.setUp()
    
    src = []
    for i in range( K ):
      src.append( ofdm.complex_white_noise( mean, sigma ) )
    
    add = gr.add_cc()
    for i in range( K ):
      self.tb.connect( src[i], (add,i) )
    
    limit = gr.head( gr.sizeof_gr_complex, N )
    dst = gr.vector_sink_c()
    
    self.tb.connect( add, limit, dst )
    self.tb.run()
    
    data = numpy.array( dst.data() )
    
    m = sum(data)/N
    v = sum((numpy.absolute(data - m))**2)/(N-1)
    
    print "Short time expectation of mean: ",m
    print "Short time expectation of variance: ",v
    
    exp_mean = K * mean
    exp_var = K * sigma**2
    
        
    self.assertEqual(len(data),N)
    self.assert_(  numpy.abs(m - exp_mean) < 0.001 * exp_mean )
    self.assert_(  numpy.abs(v - exp_var) < 0.005 * exp_var )



if __name__ == '__main__':
  gr_unittest.main()

