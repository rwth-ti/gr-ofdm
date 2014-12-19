#!/usr/bin/env python

from gnuradio import gr
from gnuradio import gr, blocks, analog, filter
# import ofdm
import numpy
from transmitter_hier_bc import transmitter_hier_bc
from receiver_hier_cb import receiver_hier_cb
from channel_hier_cc import channel_hier_cc

from numpy import sqrt
import math
# from fbmc_swig


class test_demapper_fbmc_multiuser:
	def __init__ ( self ):
		pass
		
	# def test_symbol_src ( self, arity ):
	# 	vlen = 1
	# 	N = int( 1e7 )
		
	# 	demapper = ofdm.generic_demapper_vcb( vlen )
	# 	const = demapper.get_constellation( arity )
	# 	assert( len( const ) == 2**arity )
		
	# 	symsrc = ofdm.symbol_random_src( const, vlen )
	# 	acc = ofdm.accumulator_cc()
	# 	skiphead = blocks.skiphead( gr.sizeof_gr_complex, N-1 )
	# 	limit = blocks.head( gr.sizeof_gr_complex, 1 )
	# 	dst = blocks.vector_sink_c()
		
	# 	c2mag = blocks.complex_to_mag_squared()
	# 	acc_c2m = ofdm.accumulator_ff()
	# 	skiphead_c2m = blocks.skiphead( gr.sizeof_float, N-1 )
	# 	limit_c2m = blocks.head( gr.sizeof_float, 1 )
	# 	dst_c2m = blocks.vector_sink_f()
		
	# 	tb = gr.top_block ( "test__block" )
	# 	tb.connect( symsrc, acc, skiphead, limit, dst )
	# 	tb.connect( symsrc, c2mag, acc_c2m, skiphead_c2m, limit_c2m, dst_c2m )
	# 	tb.run()
		
	# 	data = numpy.array( dst.data() )
	# 	data_c2m = numpy.array( dst_c2m.data() )
		
	# 	m = data / N
	# 	av_pow = data_c2m / N
		
	# 	assert( abs( m ) < 0.01 )
	# 	assert( abs( 1.0 - av_pow ) < 0.5  )
		
	# 	print "Uniform distributed random symbol source has"
	# 	print "\tno offset for N=%d, relative error: %f" % (arity, abs( m ) )
	# 	print "\tAverage signal power equal 1.0, relative error: %f\t\tOK" \
	# 				 % ( abs( 1.0 - av_pow ) )
		
		
		
		
	def sim ( self, arity, snr_db, N ):
		M = 1024
		theta_sel = 0
		syms_per_frame = 10
		zero_pads = 1
		center_preamble = [1, -1j, -1, 1j] # assumed to be normalized to 1
		qam_size = 2**arity
		preamble = [0]*M*zero_pads+center_preamble*((int)(M/len(center_preamble)))+[0]*M*zero_pads
		# num_symbols = 2**12
		exclude_preamble = 0
		exclude_multipath =0
		sel_taps = 0 # epa=0, eva = 1, etu=3
		freq_offset=0
		exclude_noise = 0
		sel_noise_type =0 # gaussian
		eq_select = 3
		# SNR = 20
		K = 4
		N = int( N ) # num of !samples!
		num_bits = N*arity
		# amp = math.sqrt(M/(10**(float(snr_db)/10)))/math.sqrt(2)
		# amp = math.sqrt((10**(float(-1*snr_db)/20))*(2*K*M+(2*syms_per_frame-1)*M)/(4*syms_per_frame))/math.sqrt(2)
		if exclude_preamble:
			amp = math.sqrt((10**(float(-1*snr_db)/10))*(2*K*M+(2*syms_per_frame-1)*M)/(4*syms_per_frame))/math.sqrt(2)
		else:
			amp = math.sqrt((10**(float(-1*snr_db)/10))*(M*(syms_per_frame+1)/(syms_per_frame+1+2*zero_pads))*((K*M+(2*syms_per_frame-1)*M/2)/(M*syms_per_frame)))/math.sqrt(2)
		# print amp
		# print amp2
		tx = transmitter_hier_bc(M, K, qam_size, syms_per_frame, theta_sel, exclude_preamble, center_preamble,1)
		rx = receiver_hier_cb(M, K, qam_size, syms_per_frame, theta_sel, eq_select, exclude_preamble, center_preamble,1)
		ch = channel_hier_cc(M, K, syms_per_frame, exclude_multipath, sel_taps, freq_offset, exclude_noise, sel_noise_type, snr_db, exclude_preamble, zero_pads)

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
			# min_ber = 0
			min_ber = 100. / (N*arity)
			ber_arr = []
			snr_range = range(0, 30, 1)
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
	
