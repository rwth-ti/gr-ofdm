#!/usr/bin/env python

from gnuradio import gr
from gnuradio import gr, blocks, analog, filter
# import ofdm
import numpy
from fbmc_transmitter_hier_bc import fbmc_transmitter_hier_bc
from fbmc_receiver_hier_cb import fbmc_receiver_hier_cb

from numpy import sqrt
import math
# from fbmc_swig


class test_demapper_fbmc:
  def __init__ ( self ):
    pass
    
  # def test_symbol_src ( self, arity ):
  #   vlen = 1
  #   N = int( 1e7 )
    
  #   demapper = ofdm.generic_demapper_vcb( vlen )
  #   const = demapper.get_constellation( arity )
  #   assert( len( const ) == 2**arity )
    
  #   symsrc = ofdm.symbol_random_src( const, vlen )
  #   acc = ofdm.accumulator_cc()
  #   skiphead = blocks.skiphead( gr.sizeof_gr_complex, N-1 )
  #   limit = blocks.head( gr.sizeof_gr_complex, 1 )
  #   dst = blocks.vector_sink_c()
    
  #   c2mag = blocks.complex_to_mag_squared()
  #   acc_c2m = ofdm.accumulator_ff()
  #   skiphead_c2m = blocks.skiphead( gr.sizeof_float, N-1 )
  #   limit_c2m = blocks.head( gr.sizeof_float, 1 )
  #   dst_c2m = blocks.vector_sink_f()
    
  #   tb = gr.top_block ( "test__block" )
  #   tb.connect( symsrc, acc, skiphead, limit, dst )
  #   tb.connect( symsrc, c2mag, acc_c2m, skiphead_c2m, limit_c2m, dst_c2m )
  #   tb.run()
    
  #   data = numpy.array( dst.data() )
  #   data_c2m = numpy.array( dst_c2m.data() )
    
  #   m = data / N
  #   av_pow = data_c2m / N
    
  #   assert( abs( m ) < 0.01 )
  #   assert( abs( 1.0 - av_pow ) < 0.5  )
    
  #   print "Uniform distributed random symbol source has"
  #   print "\tno offset for N=%d, relative error: %f" % (arity, abs( m ) )
  #   print "\tAverage signal power equal 1.0, relative error: %f\t\tOK" \
  #          % ( abs( 1.0 - av_pow ) )
    
    
    
    
  def sim ( self, arity, snr_db, N ):
    M = 1024
    theta_sel = 0
    syms_per_frame = 10
    qam_size = 2**arity
    preamble = [0]*M+[1, -1j, -1, 1j]*(M/4)+[0]*M
    # num_symbols = 2**12
    exclude_preamble = 1
    # SNR = 20
    K = 4
    N = int( N ) # num of !samples!
    num_bits = N*arity
    amp = (10.0**(float(-1*snr_db)/20.0))/math.sqrt(2)
    # print amp
    tx = fbmc_transmitter_hier_bc(M, K, qam_size, syms_per_frame, theta_sel, exclude_preamble, None)
    rx = fbmc_receiver_hier_cb(M, K, qam_size, syms_per_frame, theta_sel, 3, exclude_preamble, None)

    # # src = blocks.vector_source_b(src_data, vlen=1)
    xor_block = blocks.xor_bb()
    head1 = blocks.head(gr.sizeof_char*1, N)
    head0 = blocks.head(gr.sizeof_char*1, N)
    add_block = blocks.add_vcc(1)
    src = blocks.vector_source_b(map(int, numpy.random.randint(0, qam_size, 100000)), True)
    noise = analog.fastnoise_source_c(analog.GR_GAUSSIAN, amp, 0, 8192)
    dst = blocks.vector_sink_b(vlen=1)

    tb = gr.top_block ( "test_block" )
    tb.connect((src, 0), (head1, 0)) #esas
    tb.connect((head1, 0), (xor_block, 0)) #esas
    tb.connect((src, 0), (tx, 0)) #esas
    tb.connect((tx, 0), (add_block, 0)) #esas
    tb.connect((noise, 0), (add_block, 1)) #esas
    # tb.connect((head0, 0), (add_block, 1)) #esas
    tb.connect((add_block, 0), (rx, 0)) #esas
    tb.connect((rx, 0),(head0, 0)) #esas
    tb.connect((head0, 0), (xor_block, 1)) #esas
    tb.connect((xor_block, 0), (dst, 0)) #esas  

    tb.run()

    # what we record in dst.data will be output of xor_block. now we have to process those data
    # so as to find bit errors.
    result_data = dst.data()

    bit_errors = 0
    for i in range(len(result_data)):
      # print bin(result_data[i])
      bit_errors = bit_errors + (bin(result_data[i]).count('1'))

    # print len(result_data)

    # return 1

    return float(bit_errors) / num_bits
    
    
  def start ( self ):
    
    # for i in range(1,9):
    #   test_symbol_src( i )
    
    N = 2**20 #!! we take this as number of samples, not bits.
    
    ber_curves = dict()
    
    narity_range = [2, 4, 6, 8]
    
    for arity in narity_range:
      min_ber = 0
      # min_ber = 100. / (N*arity)
      ber_arr = []
      snr_range = range(-20, 36, 1)
      for snr_db in snr_range:
        ber = self.sim( arity, snr_db, N )
        ber_arr.append( ber )
        
        print "For n-arity %d and SNR = %.1f dB, BER is ~%g" \
               % ( arity, snr_db , ber )
  
        if ber <= min_ber:
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
    
    print "semilogy(snr,ber,'--x')"
    print "hold on"
    print "semilogy(snr,ber_ref,'--o')"
    print "legend('QPSK','16QAM','64QAM','256QAM')"
    print "grid on"
    print "xlabel 'SNR (dB)'"
    print "ylabel 'approximate BER'"
    print "title 'BER over SNR for FBMC system, N=%d window size'" % ( N )


if __name__ == '__main__':
  t = test_demapper_fbmc()
  t.start()
  
