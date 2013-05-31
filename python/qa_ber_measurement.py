#!/usr/bin/env python

from gnuradio import gr, gr_unittest
import ofdm_swig as ofdm
import numpy


class qa_ber_measurement (gr_unittest.TestCase):
  def setUp (self):
    self.tb = gr.top_block ("test_block")

  def tearDown (self):
    self.tb = None

  def std_test(self, p, N, Nwin ):
    N = int( N )
    Nwin = int( Nwin )
    
    src = ofdm.bernoulli_bit_src( 0.5 )
    err_src = ofdm.bernoulli_bit_src( p )
    xor = gr.xor_bb()
    #berm = ofdm.ber_measurement( Nwin )
    skiphead = gr.skiphead( gr.sizeof_float, N-1 )
    limit = gr.head( gr.sizeof_float, 1 )
    dst = gr.vector_sink_f()
    
    berm = gr.single_pole_iir_filter_ff( 10.0/float(Nwin) )
    self.tb.connect( err_src, gr.char_to_float(), 
                     berm, 
                     skiphead, limit, dst )
    self.tb.connect( berm, gr.multiply_const_ff( 1.0/p), gr.file_sink( gr.sizeof_float, "ber_out.float" ) )
    #self.tb.connect( src,     (xor,0), berm, skiphead, limit, dst )
    #self.tb.connect( err_src, (xor,1) )
    #self.tb.connect( src, (berm,1) )
    self.tb.run()
    
    data = numpy.array( dst.data() )
    
    self.assertEqual( len(data), 1 )
    print "Soll",p,"Ist",data[len(data)-1],"Relative Abweichung",numpy.abs( data[len(data)-1] - p ) / p
     
    
#  def test_001(self):
#    self.std_test( 0.2 , 1e6, 1e6 )
#
#  def test_002(self):
#    self.std_test( 1e-1, 1e6, 1e6 )
#
#  def test_003(self):
#    self.std_test( 1e-2 , 1e6, 1e6 )
#
#  def test_004(self):
#    self.std_test( 1e-3 , 10e6, 10e6 )
#
#  def test_005(self):
#    self.std_test( 1e-4 , 1e7, 1e7 )

  def test_006(self):
    self.std_test( 1e-4 , 1e8, 1e8 )
#
#  def test_007(self):
#    self.std_test( 1e-7 , 1e10, 1e10 )

if __name__ == '__main__':
  gr_unittest.main()

