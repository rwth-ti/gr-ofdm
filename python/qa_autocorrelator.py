#!/usr/bin/env python

from gnuradio import gr, gr_unittest, eng_notation
import ofdm as ofdm
import numpy
from preambles import morellimengali_designer, schmidl_ifo_designer
from random import randint
from numpy import sqrt, concatenate
from numpy.random import randint, seed, random_integers
from gr_tools import log_to_file

from schmidl import recursive_timing_metric

import os

class autocorrelator ( gr.hier_block2 ):
  def __init__( self, lag, n_samples ):
    gr.hier_block2.__init__( self,
        "autocorrelator",
        gr.io_signature(
            1, 1,
            gr.sizeof_gr_complex ),
        gr.io_signature(
            1, 1,
            gr.sizeof_float ) )
    s1 = ofdm.autocorrelator_stage1( lag )
    s2 = ofdm.autocorrelator_stage2( n_samples )
    
    self.connect( self, s1, s2, self )
    self.connect( (s1,1), (s2,1) )
    
    self.s2 = s2


class qa_autocorrelator(gr_unittest.TestCase):
  def setUp (self):
    self.tb = gr.top_block()
    
  def tearDown(self):
    self.tb = None
  
  def test_001(self):
    vlen = 256
    subc = 208
    L = 8
    cplen = 12
    blocklen = vlen + cplen
    framelength = 11
    bits_per_subc = [2]*vlen
    data_blocks = 10
    
    N = int( 1e8 )
    
    profiling = False

    pre0,fd = morellimengali_designer.create( subc, vlen, L )

    
    ofdm_frames = \
      ofdm_frame_src( vlen, data_blocks, pre0, cplen, framelength, 
                      bits_per_subc )
    
    uut = autocorrelator( vlen/2, vlen/2 )
    
    ref = recursive_timing_metric( vlen )
    
    
    limit_stream = gr.head( gr.sizeof_float, N )
    
    self.tb.connect( ofdm_frames, uut, limit_stream, 
                     gr.null_sink( gr.sizeof_float ) )
    
#    limit_stream.enable_detailed_profiling( profiling )
#    uut.s2.enable_detailed_profiling( profiling )
    
    
    if not profiling:
      limit_stream2 = gr.head( gr.sizeof_float, N )
      
      compare = gr.sub_ff()
      err_acc = ofdm.accumulator_ff()
      skip_err = gr.skiphead( gr.sizeof_float, N-1 )
      last_err_val = gr.head( gr.sizeof_float, 1 )
      err_sink = gr.vector_sink_f()
      
      self.tb.connect( ofdm_frames, ref, limit_stream2, 
                       gr.null_sink( gr.sizeof_float ) )
    
    
      self.tb.connect( uut, ( compare, 0 ) )
      self.tb.connect( ref, ( compare, 1 ) )
      self.tb.connect( compare, err_acc )
      self.tb.connect( err_acc, skip_err )
      self.tb.connect( skip_err, last_err_val )
      self.tb.connect( last_err_val, err_sink )
    
    
#    log_to_file( self.tb, limit_stream, "data/autocorr_uut.float" )
#    log_to_file( self.tb, limit_stream2, "data/autocorr_ref.float" )
    
#    r = time_it( self.tb )
    self.tb.run()
    
#    print "Expected throughput:  %s Samples/s" % ( eng_notation.num_to_str( float(N) / r ) )
    
    if not profiling:
      e = numpy.array( err_sink.data() )[0]
      print "Err: %.7f" % ( e )

  def test_002(self):
    vlen = 256
    subc = 208
    L = 8
    cplen = 12
    blocklen = vlen + cplen
    framelength = 11
    bits_per_subc = [2]*vlen
    data_blocks = 10
    
    N = int( 1e9 )
    
    # GI metric

    pre0,fd = morellimengali_designer.create( subc, vlen, L )

    
    ofdm_frames = \
      ofdm_frame_src( vlen, data_blocks, pre0, cplen, framelength, 
                      bits_per_subc )
    
    #uut = ofdm.autocorrelator0( vlen, cplen )
    uut = autocorrelator( vlen, cplen )
    
    limit_stream = gr.head( gr.sizeof_float, N )
    
    self.tb.connect( ofdm_frames, uut, limit_stream, 
                     gr.null_sink( gr.sizeof_float ) )

#    log_to_file( self.tb, limit_stream, "data/cyclicprefix_autocorr.float" )
    
    r = time_it( self.tb )
    
    print "Expected throughput:  %s Samples/s" % ( eng_notation.num_to_str( float(N) / r ) )


  def test_100(self):
    vlen = 256
    subc = 208
    L = 8
    cplen = 12
    blocklen = vlen + cplen
    framelength = 11
    bits_per_subc = [2]*vlen
    data_blocks = 10
    
    # SC metric, ofdm frames generated statically
    
    M = 10
    
    Nsamples_per_frame = framelength * (vlen+cplen) 
    
    N = int( 1e9 )

    pre0,fd = morellimengali_designer.create( subc, vlen, L )

    
    ofdm_frames = \
      ofdm_frame_src( vlen, data_blocks, pre0, cplen, framelength, 
                      bits_per_subc )
      
    dst = gr.vector_sink_c()
    
    #uut = ofdm.autocorrelator( vlen/2, vlen/2 )
    uut = autocorrelator( vlen/2, vlen/2 )
    
    limit_stream = gr.head( gr.sizeof_gr_complex, Nsamples_per_frame * M )
     
    tb = gr.top_block("s")
    tb.connect( ofdm_frames, limit_stream, dst )
    tb.run()
    
    src = gr.vector_source_c( dst.data(), True )
    limit = gr.head( gr.sizeof_gr_complex, N )
    self.tb.connect( src, limit, uut, 
                     gr.null_sink( gr.sizeof_float ) )


    r = time_it( self.tb )
    
    print "SC rate: %s Samples/second" \
      % ( eng_notation.num_to_str( float(N) / r ) )
      

  def test_101(self):
    vlen = 256
    subc = 208
    L = 8
    cplen = 12
    blocklen = vlen + cplen
    framelength = 11
    bits_per_subc = [2]*vlen
    data_blocks = 10
    
    # SC metric, ofdm frames generated statically
    
    M = 10
    
    Nsamples_per_frame = framelength * (vlen+cplen) 
    
    N = int( 1e9 )

    pre0,fd = morellimengali_designer.create( subc, vlen, L )

    
    ofdm_frames = \
      ofdm_frame_src( vlen, data_blocks, pre0, cplen, framelength, 
                      bits_per_subc )
      
    dst = gr.vector_sink_c()
    
    #uut = ofdm.autocorrelator( vlen, cplen )
    uut = autocorrelator( vlen, cplen )
    
    limit_stream = gr.head( gr.sizeof_gr_complex, Nsamples_per_frame * M )
     
    tb = gr.top_block("s")
    tb.connect( ofdm_frames, limit_stream, dst )
    tb.run()
    
    src = gr.vector_source_c( dst.data(), True )
    limit = gr.head( gr.sizeof_gr_complex, N )
    self.tb.connect( src, limit, uut, 
                     gr.null_sink( gr.sizeof_float ) )


    r = time_it( self.tb )
    
    print "GI rate: %s Samples/second" \
      % ( eng_notation.num_to_str( float(N) / r ) )
       
      
class ofdm_frame_src ( gr.hier_block2 ):
  def __init__( self, vlen, data_blocks, preamble_block, cp_len,
                framelength, bits_per_subc ):
    gr.hier_block2.__init__( self,
        "ofdm_frame_src",
        gr.io_signature(0,0,0),
        gr.io_signature( 1, 1, gr.sizeof_gr_complex ) )
    
    
    data_block_src_i = data_block_src( bits_per_subc, vlen, data_blocks ) 
    
    mux_ctrl = concatenate([[0],[1]*(framelength-1)])
    
    preamble_src = gr.vector_source_c( preamble_block, True, vlen )
    self.preamble_src = preamble_src
    
    block_mux = ofdm.static_mux_v( vlen * gr.sizeof_gr_complex, mux_ctrl.tolist() )
    block_stream = ofdm.cyclic_prefixer( vlen, vlen+cp_len )
    
    self.connect( preamble_src, ( block_mux, 0 ) )
    self.connect( data_block_src_i, ( block_mux, 1 ) )
    self.connect( block_mux, block_stream, self )
    
    self.reset_blocks = [ data_block_src_i, block_mux ]
    self.src = data_block_src_i
    
    
  def reset(self):
    for x in self.reset_blocks:
      x.reset()
      
    self.preamble_src.rewind()
    
  def get_bitdata( self ):
    return self.src.get_bitdata()
  
  
      
class data_block_src ( gr.hier_block2 ):
  def __init__( self, bits_per_subc, vlen, nblocks = 1 ):
    gr.hier_block2.__init__( self,
          "data_block_src",
          gr.io_signature(0,0,0),
          gr.io_signature( 1, 1, gr.sizeof_gr_complex * vlen ) )
    
    demapper = ofdm.generic_demapper_vcb(1)
    sigconst = dict()
    for i in range(1, max( bits_per_subc ) + 1 ):
      sigconst[i] = demapper.get_constellation( i )
    
    self.sigconst = sigconst
    
    self.nblocks = nblocks
    self.vlen = vlen
    self.bpsubc = bits_per_subc
    
    self.gen_bit_data(nblocks, vlen, bits_per_subc)
    self.build_blocks()
    self.connect_blocks()
    
  def gen_bit_data(self, nblocks, vlen, bpsubc ):   
    fd = [0]*(nblocks*vlen)
    #bits = [0]*(nblocks*sum(bpsubc))
    bits = random_integers( 0, 1, nblocks*sum(bpsubc) )
    ind = 0
    ind_bits = 0
    for blk in range( nblocks ):
      #fd = []
      for i in range( vlen ):
        sym = 0
        for x in range( bpsubc[ i ] ):
          #bit = randint( 0, 1 )
          sym = sym*2 + bits[ind_bits]
          #bits[ind_bits] = bit
          ind_bits += 1
      
        fd[ind] = self.sigconst[ bpsubc[i] ][ sym ]
        ind += 1
        
    self.fd = fd
    self.bitdata = bits
    
  def build_blocks(self):
    self.ifft = gr.fft_vcc( self.vlen, False, [], True )
    self.rebuild_blocks()
    
  def rebuild_blocks(self):
    self.src = gr.vector_source_c( self.fd, True, self.vlen )
    
  def connect_blocks(self):
    self.connect( self.src, self.ifft, self )
  
  def disconnect_blocks(self):
    self.disconnect( self.src, self.ifft, self )
        
  def reset(self):
    self.disconnect_blocks()
    self.gen_bit_data(self.nblocks, self.vlen, self.bpsubc)
    self.rebuild_blocks()
    self.connect_blocks()
    
  def get_bitdata( self ):
    return self.bitdata
  
  
  
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
