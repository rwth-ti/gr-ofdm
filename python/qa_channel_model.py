#!/usr/bin/env python

from gnuradio import gr, gr_unittest, eng_notation
from moms import moms
import ofdm as ofdm
import numpy
from snr_estimator import milans_snr_estimator
from math import sqrt

import os

class qa_snr_estimator(gr_unittest.TestCase):
  def setUp (self):
    self.tb = gr.top_block()
    
  def tearDown(self):
    self.tb = None
    

   
#  def test_001(self):
#      
#      
#    vlen = 256
#    L = 8
#    N = int( 4e6 )
#    #u = range (vlen/L*(L-1))
#    #zeros_ind= map(lambda z: z+1+z/(L-1),u)
#    #data = [(1.0-0.2/numpy.sqrt(L))*numpy.sqrt(L)+ 0.1] * vlen
#    data = [1] * vlen
#    
##    for x in zeros_ind:
##     data[x]=0.1
#    limit = gr.head( gr.sizeof_gr_complex * vlen, N )
#
#
#    
#    src = gr.vector_source_c( data, True, vlen )
#    dst = gr.vector_sink_f()
#    dst1 = gr.vector_sink_f()
#
#    
#    
#    uut = ofdm.snr_estimator( vlen, L )
#    snrm= gr.single_pole_iir_filter_ff(0.1)
#    self.tb.connect( src, limit, uut,snrm, dst )
#    self.tb.connect( (uut,1), dst1)
#    
#    self.tb.run()
#    
#    d = dst.data()[0]
#    d1 = dst1.data()[0]
#     
#    self.assertAlmostEqual(d,0.0)
#    self.assertAlmostEqual(d1,1.0)
    
  
  def test_100(self):
    vlen = 256
    N = int( 5e5 )
    soff=40
    taps = [1.0,0.0,2e-1+0.1j,1e-4-0.04j]
    freqoff = 0.0
    snr_db = 10
    rms_amplitude = 8000
    
    
    data = [1 + 1j] * vlen
    #data2 = [2] * vlen
    
    src = gr.vector_source_c( data, True, vlen )
    v2s = gr.vector_to_stream(gr.sizeof_gr_complex,vlen)
    
    
    #interp = gr.fractional_interpolator_cc(0.0,soff)
    interp = moms(1000000,1000000+soff)
    
    fad_chan = gr.fir_filter_ccc(1,taps)
    
    freq_shift = gr.multiply_cc()
    norm_freq = freqoff / vlen
    freq_off_src = gr.sig_source_c(1.0, gr.GR_SIN_WAVE, norm_freq, 1.0, 0.0 )
    
    snr = 10.0**(snr_db/10.0)
    noise_sigma = sqrt( rms_amplitude**2 / snr)
    awgn_chan = gr.add_cc()
    awgn_noise_src = ofdm.complex_white_noise( 0.0, noise_sigma )
    
    dst = gr.null_sink( gr.sizeof_gr_complex )

    limit = gr.head( gr.sizeof_gr_complex * vlen, N )
    
    
    self.tb.connect( src, limit, v2s, interp, fad_chan,freq_shift, awgn_chan, dst )
    self.tb.connect( freq_off_src,(freq_shift,1))
    self.tb.connect( awgn_noise_src,(awgn_chan,1))
    
    r = time_it( self.tb )
    
    print "Rate: %s Samples/second" \
      % eng_notation.num_to_str( float(N) * vlen / r ) 

  def test_101(self):
    vlen = 256
    N = int( 5e5 )
    soff=1.0
    taps = [1.0,0.0,2e-1+0.1j,1e-4-0.04j]
    freqoff = 0.0
    norm_freq = freqoff / vlen
    rms_amplitude = 8000
    snr_db = 10
    snr = 10.0**(snr_db/10.0)
    noise_sigma = sqrt( rms_amplitude**2 / snr)
    
    
    
    data = [1 + 1j] * vlen
    #data2 = [2] * vlen
    
    src = gr.vector_source_c( data, True, vlen )
    v2s = gr.vector_to_stream(gr.sizeof_gr_complex,vlen)
    
    
    channel = gr.channel_model(noise_sigma,norm_freq,soff,taps)
    
    dst = gr.null_sink( gr.sizeof_gr_complex )

    limit = gr.head( gr.sizeof_gr_complex * vlen, N )
    
    
    self.tb.connect( src, limit, v2s, channel, dst )
    
    r = time_it( self.tb )
    
    print "Rate: %s Samples/second" \
      % eng_notation.num_to_str( float(N) * vlen / r ) 
      
  def test_102(self):
    vlen = 256
    N = int( 5e5 )
    taps = [1.0,0.0,2e-1+0.1j,1e-4-0.04j]
    freqoff = 0.0
    snr_db = 10
    rms_amplitude = 8000
    
    
    data = [1 + 1j] * vlen
    #data2 = [2] * vlen
    
    src = gr.vector_source_c( data, True, vlen )
    v2s = gr.vector_to_stream(gr.sizeof_gr_complex,vlen)
    
    fad_chan = gr.fir_filter_ccc(1,taps)
    
    freq_shift = gr.multiply_cc()
    norm_freq = freqoff / vlen
    freq_off_src = gr.sig_source_c(1.0, gr.GR_SIN_WAVE, norm_freq, 1.0, 0.0 )
    
    snr = 10.0**(snr_db/10.0)
    noise_sigma = sqrt( rms_amplitude**2 / snr)
    awgn_chan = gr.add_cc()
    awgn_noise_src = ofdm.complex_white_noise( 0.0, noise_sigma )
    
    dst = gr.null_sink( gr.sizeof_gr_complex )

    limit = gr.head( gr.sizeof_gr_complex * vlen, N )
    
    
    self.tb.connect( src, limit, v2s, fad_chan,freq_shift, awgn_chan, dst )
    self.tb.connect( freq_off_src,(freq_shift,1))
    self.tb.connect( awgn_noise_src,(awgn_chan,1))
    
    r = time_it( self.tb )
    
    print "Rate: %s Samples/second" \
      % eng_notation.num_to_str( float(N) * vlen / r ) 
    
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
    
    return real

    
if __name__ == '__main__':
  gr_unittest.main()
