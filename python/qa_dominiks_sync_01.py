#!/usr/bin/env python

from gnuradio import gr, gr_unittest, eng_notation
import ofdm as ofdm
import numpy
from autocorrelator import autocorrelator
from preambles import morellimengali_designer
from random import randint
from numpy import sqrt, concatenate, delete, s_
from numpy.random import randint, seed, random_integers
from gr_tools import log_to_file

import os

from test_channel_estimator import awgn_channel




class qa_sync(gr_unittest.TestCase):
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
    
    N = int( 1e5 )
    
    pre0,fd = morellimengali_designer.create( subc, vlen, L )

    ofdm_frames = \
      ofdm_frame_src( vlen, data_blocks, pre0, cplen, framelength, 
                      bits_per_subc )
    
    scmetric = autocorrelator( vlen/2, vlen/2 )
    gimetric = autocorrelator( vlen, cplen )
    
#    ctrl_shift = gr.vector_source_f([0.0],True)
    
    sigpow = float( vlen )
    snr_db = 10.0
    awgn_chan = awgn_channel( snr_db, sigpow )
    
    rxbaseband = awgn_chan
    self.tb.connect( ofdm_frames, awgn_chan )
    
    
    uut = ofdm.dominiks_sync_01( vlen, cplen )
    
    limit_stream = gr.head( gr.sizeof_gr_complex * vlen, N )
    
    self.tb.connect( rxbaseband, scmetric )
    self.tb.connect( rxbaseband, gimetric )
    
    self.tb.connect( rxbaseband, ( uut, 0 ) )
    self.tb.connect( scmetric, ( uut, 1 ) )
    self.tb.connect( gimetric, ( uut, 2 ) )
#    self.tb.connect( ctrl_shift, ( uut, 3 ) )
    
    self.tb.connect( ( uut, 0 ), limit_stream,
                     gr.null_sink( gr.sizeof_gr_complex * vlen ) )
    self.tb.connect( ( uut, 1 ), gr.null_sink( gr.sizeof_char ) )
    
#    log_to_file( self.tb, (uut,0), "data/uut0.compl" )
#    log_to_file( self.tb, (uut,0), "data/uut0.float", True )
    
#    framestart_f = gr.char_to_float()
#    self.tb.connect( (uut,1), framestart_f )
#    log_to_file( self.tb, framestart_f, "data/framestart.float" )

    
    
    self.tb.run()
    
  def test_002(self):
    vlen = 256
    subc = 208
    L = 8
    cplen = 12
    blocklen = vlen + cplen
    framelength = 11
    bits_per_subc = [2]*vlen
    data_blocks = 10
    
    N = int( 1e2 )
    
    pre0,fd = morellimengali_designer.create( subc, vlen, L )

    ofdm_frames = \
      ofdm_frame_src( vlen, data_blocks, pre0, cplen, framelength, 
                      bits_per_subc )
      
    ofdm_frame_sink = gr.vector_sink_c()
    tb2 = gr.top_block()
    tb2.connect( ofdm_frames, 
                 gr.head( gr.sizeof_gr_complex,  int(1e2) * blocklen ),
                 ofdm_frame_sink )
    tb2.run()
    
    of = numpy.array( ofdm_frame_sink.data() )
    
    print len( of )
    print (N/2*blocklen)
    
    of = delete( of, s_[(N/2*blocklen) : ((N+3)*blocklen/2) ] )
    
    print len( of )
    
    ofdm_frames = gr.vector_source_c( list(of), True )
    
    scmetric = autocorrelator( vlen/2, vlen/2 )
    gimetric = autocorrelator( vlen, cplen )
    
#    ctrl_shift = gr.vector_source_f([0.0],True)
    
    sigpow = float( vlen )
    snr_db = 80.0
    awgn_chan = awgn_channel( snr_db, sigpow )
    
#    rxbaseband = awgn_chan
#    self.tb.connect( ofdm_frames, awgn_chan )
    rxbaseband = ofdm_frames
    
    
    uut = ofdm.dominiks_sync_01( vlen, cplen )
    
    limit_stream = gr.head( gr.sizeof_gr_complex * vlen, N )
    
    self.tb.connect( rxbaseband, scmetric )
    self.tb.connect( rxbaseband, gimetric )
    
    self.tb.connect( rxbaseband, ( uut, 0 ) )
    self.tb.connect( scmetric, ( uut, 1 ) )
    self.tb.connect( gimetric, ( uut, 2 ) )
#    self.tb.connect( ctrl_shift, ( uut, 3 ) )
    
    self.tb.connect( ( uut, 0 ), limit_stream,
                     gr.null_sink( gr.sizeof_gr_complex * vlen ) )
    self.tb.connect( ( uut, 1 ), gr.null_sink( gr.sizeof_char ) )
    
#    log_to_file( self.tb, (uut,0), "data/uut0.compl" )
#    log_to_file( self.tb, (uut,0), "data/uut0.float", True )
#    
#    framestart_f = gr.char_to_float()
#    self.tb.connect( (uut,1), framestart_f )
#    log_to_file( self.tb, framestart_f, "data/framestart.float" )

    
    
#    self.tb.run()
    r = time_it( self.tb )
    print eng_notation.num_to_str( float(N * blocklen) / r )
    
           
      
class ofdm_frame_src ( gr.hier_block2 ):
  def __init__( self, vlen, data_blocks, preamble_block, cp_len,
                framelength, bits_per_subc ):
    gr.hier_block2.__init__( self,
        "ofdm_frame_src",
        gr.io_signature(0,0,0),
        gr.io_signature( 1, 1, gr.sizeof_gr_complex ) )
    
    
    data_block_src_i = data_block_src( bits_per_subc, vlen, data_blocks )
    
    ofdm_frame_mux = ofdm.frame_mux( vlen, framelength ) 
    ofdm_frame_mux.add_preamble( preamble_block )
    
    block_stream = ofdm.cyclic_prefixer( vlen, vlen+cp_len )
    
    self.connect( data_block_src_i, ofdm_frame_mux, block_stream, self )
    
    self.reset_blocks = [ data_block_src_i ]
    self.src = data_block_src_i
    
#    mux_ctrl = concatenate([[0],[1]*(framelength-1)])
#    
#    preamble_src = gr.vector_source_c( preamble_block, True, vlen )
#    self.preamble_src = preamble_src
#    
#    block_mux = ofdm.static_mux_v( vlen * gr.sizeof_gr_complex, mux_ctrl )
#    block_stream = ofdm.cyclic_prefixer( vlen, vlen+cp_len )
#    
#    self.connect( preamble_src, ( block_mux, 0 ) )
#    self.connect( data_block_src_i, ( block_mux, 1 ) )
#    self.connect( block_mux, block_stream, self )
#    
#    self.reset_blocks = [ data_block_src_i, block_mux ]
#    self.src = data_block_src_i
    
    
  def reset(self):
    for x in self.reset_blocks:
      x.reset()
      
#    self.preamble_src.rewind()
    
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
