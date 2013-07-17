#!/usr/bin/env python

from gnuradio import gr, gr_unittest, eng_notation
import ofdm as ofdm
import numpy, os

class qa_frame_mux(gr_unittest.TestCase):
  def setUp (self):
    self.tb = gr.top_block()
    
  def tearDown(self):
    self.tb = None
  
  def test_001(self):
    vlen = 256
    frame_data_blocks = 10
    preambles = 1
    frame_len = frame_data_blocks + preambles
    
    data = [1.0] * ( frame_data_blocks * vlen )
    preamble = [2.0] * ( preambles * vlen )
    ref = numpy.concatenate( [ preamble, data ] )
    
    src = gr.vector_source_c( data, False, vlen )
    dst = gr.vector_sink_c()
    
    uut = ofdm.frame_mux( vlen, frame_len )
    
    uut.add_preamble( preamble )
    
    self.tb.connect( src, uut, 
                     gr.vector_to_stream( gr.sizeof_gr_complex, vlen ), dst )
    self.tb.run()
    
    self.assertEqual( list(ref), list(dst.data()) )
    
  def test_002(self):
    vlen = 256
    frame_data_blocks = 10
    preambles = 1
    frame_len = frame_data_blocks + preambles
    frames = 5
    
    data = [1.0] * ( frame_data_blocks * vlen )
    preamble = [2.0] * ( preambles * vlen )
    ref = numpy.concatenate( [ preamble, data ] * frames )
    
    src = gr.vector_source_c( data, True, vlen )
    dst = gr.vector_sink_c()
    limit = gr.head( gr.sizeof_gr_complex * vlen, frame_len * frames )
    
    uut = ofdm.frame_mux( vlen, frame_len )
    
    uut.add_preamble( preamble )
    
    self.tb.connect( src, limit, uut, 
                     gr.vector_to_stream( gr.sizeof_gr_complex, vlen ), dst )
    self.tb.run()
    
    self.assertEqual( list(ref), list(dst.data()) )
    
  def test_003(self):
    vlen = 256
    frame_data_blocks = 10
    preambles = 2
    frame_len = frame_data_blocks + preambles
    
    data = [1.0] * ( frame_data_blocks * vlen )
    preamble1 = [2.0] * vlen
    preamble2 = [3.0] * vlen
    ref = numpy.concatenate( [ preamble1, preamble2, data ] )
    
    src = gr.vector_source_c( data, False, vlen )
    dst = gr.vector_sink_c()
    
    uut = ofdm.frame_mux( vlen, frame_len )
    
    uut.add_preamble( preamble1 )
    uut.add_preamble( preamble2 )
    
    self.tb.connect( src, uut, 
                     gr.vector_to_stream( gr.sizeof_gr_complex, vlen ), dst )
    self.tb.run()
    
    self.assertEqual( list(ref), list(dst.data()) )
    
  def test_004(self):
    self.profile()
    
  def profile(self):
    vlen = 256
    frame_data_blocks = 10
    preambles = 2
    frame_len = frame_data_blocks + preambles
    
    N = int( 1e6 )
    
    data = [1.0] * ( frame_data_blocks * vlen )
    preamble1 = [2.0] * vlen
    preamble2 = [3.0] * vlen
    
    src = gr.vector_source_c( data, True, vlen )
    dst = gr.null_sink( gr.sizeof_gr_complex * vlen )
    limit = gr.head( gr.sizeof_gr_complex * vlen, N * frame_data_blocks )
    
    uut = ofdm.frame_mux( vlen, frame_len )
    
    uut.add_preamble( preamble1 )
    uut.add_preamble( preamble2 )
    
    self.tb.connect( src, limit, uut, dst )
    
    r = time_it(self.tb)
    
    print "Throughput: %s Samples/second" % \
      eng_notation.num_to_str( float(N) * frame_data_blocks * vlen / r )
    
    
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
#    print "(user+sys)/real  %7.3f" % ((total_user + total_sys)/real,)
    
    return real

    
if __name__ == '__main__':
  gr_unittest.main()
