#!/usr/bin/env python

from gnuradio import gr
from gnuradio import gr, blocks, analog, filter
import ofdm
import numpy

from numpy import sqrt


class test_demapper:
  def __init__ ( self ):
    pass
    
  def test_symbol_src ( self, arity ):
    vlen = 1
    N = int( 1e7 )
    
    demapper = ofdm.generic_demapper_vcb( vlen )
    const = demapper.get_constellation( arity )
    assert( len( const ) == 2**arity )
    
    symsrc = ofdm.symbol_random_src( const, vlen )
    acc = ofdm.accumulator_cc()
    skiphead = blocks.skiphead( gr.sizeof_gr_complex, N-1 )
    limit = blocks.head( gr.sizeof_gr_complex, 1 )
    dst = blocks.vector_sink_c()
    
    c2mag = blocks.complex_to_mag_squared()
    acc_c2m = ofdm.accumulator_ff()
    skiphead_c2m = blocks.skiphead( gr.sizeof_float, N-1 )
    limit_c2m = blocks.head( gr.sizeof_float, 1 )
    dst_c2m = blocks.vector_sink_f()
    
    tb = gr.top_block ( "test__block" )
    tb.connect( symsrc, acc, skiphead, limit, dst )
    tb.connect( symsrc, c2mag, acc_c2m, skiphead_c2m, limit_c2m, dst_c2m )
    tb.run()
    
    data = numpy.array( dst.data() )
    data_c2m = numpy.array( dst_c2m.data() )
    
    m = data / N
    av_pow = data_c2m / N
    
    assert( abs( m ) < 0.01 )
    assert( abs( 1.0 - av_pow ) < 0.5  )
    
    print "Uniform distributed random symbol source has"
    print "\tno offset for N=%d, relative error: %f" % (arity, abs( m ) )
    print "\tAverage signal power equal 1.0, relative error: %f\t\tOK" \
           % ( abs( 1.0 - av_pow ) )
    
    
    
    
  def sim ( self, arity, snr_db, N ):
    
    vlen = 1
    N = int( N )
    snr = 10.0**(snr_db/10.0)
    
    sigpow = 1.0
    noise_pow = sigpow / snr
    
    demapper = ofdm.generic_demapper_vcb( vlen )
    const = demapper.get_constellation( arity )
    assert( len( const ) == 2**arity )
    
    symsrc = ofdm.symbol_random_src( const, vlen )
    noise_src = ofdm.complex_white_noise( 0.0, sqrt( noise_pow ) )
    channel = blocks.add_cc()
    bitmap_src = blocks.vector_source_b( [arity] * vlen, True, vlen )
    bm_trig_src = blocks.vector_source_b( [1], True )
    ref_bitstream = blocks.unpack_k_bits_bb( arity )
    bitstream_xor = blocks.xor_bb()
    bitstream_c2f = blocks.char_to_float()
    acc_biterr = ofdm.accumulator_ff()
    skiphead = blocks.skiphead( gr.sizeof_float, N-1 )
    limit = blocks.head( gr.sizeof_float, 1 )
    dst = blocks.vector_sink_f()
    
    tb = gr.top_block ( "test_block" )
    
    tb.connect( (symsrc,0), (channel,0) )
    tb.connect( noise_src,  (channel,1) )
    tb.connect( channel,     (demapper,0), (bitstream_xor,0) )
    tb.connect( bitmap_src,  (demapper,1) )
    tb.connect( bm_trig_src, (demapper,2) )
    tb.connect( (symsrc,1), ref_bitstream, (bitstream_xor,1) )
    tb.connect( bitstream_xor, bitstream_c2f, acc_biterr )
    tb.connect( acc_biterr, skiphead, limit, dst )

    tb.run()
    
    bit_errors = numpy.array( dst.data() )
    assert( len( bit_errors ) == 1 )
    bit_errors = bit_errors[0]
    
    return bit_errors / N
    
    
  def start ( self ):
    
    for i in range(1,9):
      self.test_symbol_src( i )
    
    N = 1e7
    
    min_ber = 100. / N
    
    ber_curves = dict()
    
    narity_range = range(1,9)
    
    for arity in narity_range:
      ber_arr = []
      snr_range = range(0, 36, 1)
      for snr_db in snr_range:
        ber = self.sim( arity, snr_db, N )
        ber_arr.append( ber )
        
        print "For n-arity %d and SNR = %.1f dB, BER is ~%g" \
               % ( arity, snr_db , ber )
  
        if ber < min_ber:
          break
        
      
      ber_curves[arity] = ber_arr  


      
    print "snr = [",
    for snr_db in snr_range:
      print "%.1f," % ( snr_db ),
    print "]"


    print "ber = [",
    for arity in narity_range:
      curve = ber_curves[arity]
      for x in curve:
        print "%7g," % (x),
      for i in range( len( snr_range ) - len( curve ) ):
        print " 0.0,",
      print ";"
    print "]"
    
    print "ber_ref = [",
    for arity in narity_range:
      curve = ber_curves[arity]
      if arity == 1:
        mode = 'pam'
      elif arity == 2 or arity == 3:
        mode = 'psk'
      else:
        mode = 'qam'
      print "berawgn(snr(1:%d)-10*log10(%d), '%s', %d " \
               % (len(curve),arity, mode, 2**arity ) ,
      if arity == 2 or arity == 3:
        print ", 'nondiff'",
      print "), ",
      for i in range( len( snr_range ) - len( curve ) ):
        print " 0.0,",
      print ";"
    print "]"
    
    print "semilogy(snr,ber,'x')"
    print "hold on"
    print "semilogy(snr,ber_ref,'--o')"
    print "legend('BPSK','QPSK','8PSK','16QAM','32QAM','64QAM','128QAM','256QAM')"
    print "grid on"
    print "xlabel 'SNR (dB)'"
    print "ylabel 'approximate BER'"
    print "title 'BER over SNR for OFDM demapper, N=%d window size'" % ( N )


if __name__ == '__main__':
  t = test_demapper()
  t.start()
  
