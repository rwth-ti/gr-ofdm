#!/usr/bin/env python
#
# Copyright 2004 Free Software Foundation, Inc.
# 
# This file is part of GNU Radio
# 
# GNU Radio is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2, or (at your option)
# any later version.
# 
# GNU Radio is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
# 
# You should have received a copy of the GNU General Public License
# along with GNU Radio; see the file COPYING.  If not, write to
# the Free Software Foundation, Inc., 51 Franklin Street,
# Boston, MA 02110-1301, USA.
# 

from gnuradio import gr, gr_unittest, eng_notation
import ofdm as ofdm
import os

import sys, numpy, random, math, cmath
from numpy import concatenate
import numpy

class qa_ofdm (gr_unittest.TestCase):
  def setUp (self):    
    self.fg = gr.top_block ("test_block")
  
  def tearDown (self):
    self.fg = None
  
  # no shift
  def test_001 (self):
    vlen = 128
    syms = 4
    
    freq_shift = ofdm.frequency_shift_vcc(vlen, 1.0/vlen)
    
    fft = gr.fft_vcc(vlen, True, [], True) # natural order, dc = vlen / 2
    ifft = gr.fft_vcc(vlen, False, [], True)
    fft_scale = gr.multiply_const_vcc([1.0/vlen]*vlen)
        
    vec = numpy.array(numpy.zeros(vlen), numpy.complex)
    vec[vlen/2-vlen/4] = 1.0
    vec = concatenate([vec]*syms)
    
    src = gr.vector_source_c(vec)
    dst = gr.vector_sink_c()
    s2v = gr.stream_to_vector(gr.sizeof_gr_complex, vlen)
    v2s = gr.vector_to_stream(gr.sizeof_gr_complex, vlen)
    
    eps = gr.vector_source_f([0.0]*syms)
    trig = gr.vector_source_b([1]*syms)
    
    self.fg.connect(src, s2v, ifft, (freq_shift,0))
    self.fg.connect(eps, (freq_shift,1))
    self.fg.connect(trig, (freq_shift,2))
    self.fg.connect(freq_shift, fft, fft_scale, v2s, dst)
    self.fg.run()
    
    self.assertComplexTuplesAlmostEqual(vec, numpy.array(dst.data()))
    
  # simple shift by -1.0, one frequency bin
  def test_002 (self):
    vlen = 128
    syms = 4
        
    vec = numpy.array(numpy.zeros(vlen), numpy.complex)
    vec[vlen/2-vlen/4] = 1.0
    vec = concatenate([vec]*syms)
    
    epsilon = [-1]
    frame_trigger = numpy.concatenate([[1],[0]*(syms-1)])    
    
    expec = numpy.array(numpy.zeros(vlen*syms), numpy.complex)
    for i in range(syms):
      expec[vlen/2-vlen/4+i*vlen+epsilon[0]] = 1.0
    
    freq_shift = ofdm.frequency_shift_vcc(vlen, 1.0/vlen)
    
    fft = gr.fft_vcc(vlen, True, [], True) # natural order, dc = vlen / 2
    ifft = gr.fft_vcc(vlen, False, [], True)
    fft_scale = gr.multiply_const_vcc([1.0/vlen]*vlen)    
    
    src = gr.vector_source_c(vec)
    dst = gr.vector_sink_c()
    s2v = gr.stream_to_vector(gr.sizeof_gr_complex, vlen)
    v2s = gr.vector_to_stream(gr.sizeof_gr_complex, vlen)
    
    eps = gr.vector_source_f(epsilon)
    trig = gr.vector_source_b(frame_trigger.tolist())
    
    self.fg.connect(src, s2v, ifft, (freq_shift,0))
    self.fg.connect(eps, (freq_shift,1))
    self.fg.connect(trig, (freq_shift,2))
    self.fg.connect(freq_shift, fft, fft_scale, v2s, dst)
    self.fg.run()

    self.assertComplexTuplesAlmostEqual2(expec, dst.data(), 1e-6)  
    
  # simple shift by -1.0, two frequency bins, asymmetric
  def test_003 (self):
    vlen = 128
    syms = 4
    bin1 = vlen/2-vlen/4
    bin2 = vlen/2+vlen/3
        
    vec = numpy.array(numpy.zeros(vlen), numpy.complex)
    vec[bin1] = 1.0
    vec[bin2] = -1.0
    vec = concatenate([vec]*syms)
    
    epsilon = [-1]*syms
    frame_trigger = [1]*syms    
    
    expec = numpy.array(numpy.zeros(vlen*syms), numpy.complex)
    for i in range(syms):
      expec[bin1+i*vlen+epsilon[i]] =  1.0
      expec[bin2+i*vlen+epsilon[i]] = -1.0
    
    freq_shift = ofdm.frequency_shift_vcc(vlen, 1.0/vlen)
    
    fft = gr.fft_vcc(vlen, True, [], True) # natural order, dc = vlen / 2
    ifft = gr.fft_vcc(vlen, False, [], True)
    fft_scale = gr.multiply_const_vcc([1.0/vlen]*vlen)    
    
    src = gr.vector_source_c(vec)
    dst = gr.vector_sink_c()
    s2v = gr.stream_to_vector(gr.sizeof_gr_complex, vlen)
    v2s = gr.vector_to_stream(gr.sizeof_gr_complex, vlen)
    
    eps = gr.vector_source_f(epsilon)
    trig = gr.vector_source_b(frame_trigger)
    
    self.fg.connect(src, s2v, ifft, (freq_shift,0))
    self.fg.connect(eps, (freq_shift,1))
    self.fg.connect(trig, (freq_shift,2))
    self.fg.connect(freq_shift, fft, fft_scale, v2s, dst)
    self.fg.run()

    self.assertComplexTuplesAlmostEqual2(expec, dst.data(), 1e-6)

  # simple shift by -1.0, two frequency bins, _symmetric_
  def test_004 (self):
    vlen = 128
    syms = 4
    bin1 = vlen/2-vlen/4
    bin2 = vlen/2+vlen/4
        
    vec = numpy.array(numpy.zeros(vlen), numpy.complex)
    vec[bin1] = 1.0
    vec[bin2] = -1.0
    vec = concatenate([vec]*syms)
    
    epsilon = [-1]*syms
    frame_trigger = [1]*syms    
    
    expec = numpy.array(numpy.zeros(vlen*syms), numpy.complex)
    for i in range(syms):
      expec[bin1+i*vlen+epsilon[i]] =  1.0
      expec[bin2+i*vlen+epsilon[i]] = -1.0
    
    freq_shift = ofdm.frequency_shift_vcc(vlen, 1.0/vlen)
    
    fft = gr.fft_vcc(vlen, True, [], True) # natural order, dc = vlen / 2
    ifft = gr.fft_vcc(vlen, False, [], True)
    fft_scale = gr.multiply_const_vcc([1.0/vlen]*vlen)    
    
    src = gr.vector_source_c(vec)
    dst = gr.vector_sink_c()
    s2v = gr.stream_to_vector(gr.sizeof_gr_complex, vlen)
    v2s = gr.vector_to_stream(gr.sizeof_gr_complex, vlen)
    
    eps = gr.vector_source_f(epsilon)
    trig = gr.vector_source_b(frame_trigger)
    
    self.fg.connect(src, s2v, ifft, (freq_shift,0))
    self.fg.connect(eps, (freq_shift,1))
    self.fg.connect(trig, (freq_shift,2))
    self.fg.connect(freq_shift, fft, fft_scale, v2s, dst)
    self.fg.run()

    self.assertComplexTuplesAlmostEqual2(expec, dst.data(), 1e-6)
    
  # simple shift by +10.0, two frequency bins, asymmetric
  def test_005 (self):
    vlen = 128
    syms = 4
    bin1 = vlen/2-vlen/4
    bin2 = vlen/2+vlen/3
    bin1_val = 1.0
    bin2_val = -1.0j
        
    vec = numpy.array(numpy.zeros(vlen), numpy.complex)
    vec[bin1] = bin1_val
    vec[bin2] = bin2_val
    vec = concatenate([vec]*syms)
    
    epsilon = [+10]*syms
    frame_trigger = [1]*syms
    
    expec = numpy.array(numpy.zeros(vlen*syms), numpy.complex)
    for i in range(syms):
      expec[bin1+i*vlen+epsilon[i]] =  bin1_val
      expec[bin2+i*vlen+epsilon[i]] = bin2_val
    
    freq_shift = ofdm.frequency_shift_vcc(vlen, 1.0/vlen)
    
    fft = gr.fft_vcc(vlen, True, [], True) # natural order, dc = vlen / 2
    ifft = gr.fft_vcc(vlen, False, [], True)
    fft_scale = gr.multiply_const_vcc([1.0/vlen]*vlen)    
    
    src = gr.vector_source_c(vec)
    dst = gr.vector_sink_c()
    s2v = gr.stream_to_vector(gr.sizeof_gr_complex, vlen)
    v2s = gr.vector_to_stream(gr.sizeof_gr_complex, vlen)
    
    eps = gr.vector_source_f(epsilon)
    trig = gr.vector_source_b(frame_trigger)
    
    self.fg.connect(src, s2v, ifft, (freq_shift,0))
    self.fg.connect(eps, (freq_shift,1))
    self.fg.connect(trig, (freq_shift,2))
    self.fg.connect(freq_shift, fft, fft_scale, v2s, dst)
    self.fg.run()

    self.assertComplexTuplesAlmostEqual2(expec, dst.data(), 1e-5)  
    
  # different shifts per symbol, two frequency bins, asymmetric
  def test_006 (self):
    vlen = 128
    syms = 4
    bin1 = vlen/2-vlen/4
    bin2 = vlen/2+vlen/3
    bin1_val = 1.0j
    bin2_val = -1.0
        
    vec = numpy.array(numpy.zeros(vlen), numpy.complex)
    vec[bin1] = bin1_val
    vec[bin2] = bin2_val
    vec = concatenate([vec]*syms)
    
    epsilon = [1,-4,5,2]
    frame_trigger = [1]*syms
    
    expec = numpy.array(numpy.zeros(vlen*syms), numpy.complex)
    for i in range(syms):
      expec[bin1+i*vlen+epsilon[i]] =  bin1_val
      expec[bin2+i*vlen+epsilon[i]] = bin2_val
    
    freq_shift = ofdm.frequency_shift_vcc(vlen, 1.0/vlen)
    
    fft = gr.fft_vcc(vlen, True, [], True) # natural order, dc = vlen / 2
    ifft = gr.fft_vcc(vlen, False, [], True)
    fft_scale = gr.multiply_const_vcc([1.0/vlen]*vlen)    
    
    src = gr.vector_source_c(vec)
    dst = gr.vector_sink_c()
    s2v = gr.stream_to_vector(gr.sizeof_gr_complex, vlen)
    v2s = gr.vector_to_stream(gr.sizeof_gr_complex, vlen)
    
    eps = gr.vector_source_f(epsilon)
    trig = gr.vector_source_b(frame_trigger)
    
    self.fg.connect(src, s2v, ifft, (freq_shift,0))
    self.fg.connect(eps, (freq_shift,1))
    self.fg.connect(trig, (freq_shift,2))
    self.fg.connect(freq_shift, fft, fft_scale, v2s, dst)
    self.fg.run()

    self.assertComplexTuplesAlmostEqual2(expec, dst.data(), 1e-5)
    
  # one signal at frequency 1.5 / vlen, shifted to 2.0+vlen/2 bin
  # initial phase offset remains constant through all symbols in one frame
  def test_007 (self):
    vlen = 128
    syms = 4
    bin1 = vlen/2 + 2
    bin1_val = 1.0
        
    expec = numpy.array(numpy.zeros(vlen), numpy.complex)
    expec[bin1] = bin1_val
    expec = concatenate([expec]*syms)
    
    epsilon = [0.5]
    frame_trigger = numpy.concatenate([[1],[0]*(syms-1)])
    
    freq_shift = ofdm.frequency_shift_vcc(vlen, 1.0/vlen)
    
    fft = gr.fft_vcc(vlen, True, [], True) # natural order, dc = vlen / 2
    fft_scale = gr.multiply_const_vcc([1.0/vlen]*vlen)    
    
    src = gr.sig_source_c(vlen, gr.GR_COS_WAVE, 1.5, 1.0, 0.0) 
    # bin vlen/2 + 1.5
    dst = gr.vector_sink_c()
    s2v = gr.stream_to_vector(gr.sizeof_gr_complex, vlen)
    v2s = gr.vector_to_stream(gr.sizeof_gr_complex, vlen)
    
    eps = gr.vector_source_f(epsilon)
    trig = gr.vector_source_b(frame_trigger.tolist())
    
    self.fg.connect(src, s2v, (freq_shift,0))
    self.fg.connect(eps, (freq_shift,1))
    self.fg.connect(trig, (freq_shift,2))
    self.fg.connect(freq_shift, fft, fft_scale, v2s, dst)
    self.fg.run()

    self.assertComplexTuplesAlmostEqual2(expec, dst.data(), 1e-5, 1e-5)  
    
  # one signal at frequency 4.5 / vlen, shifted to 4.0+vlen/2 bin
  # tests phase correction for cyclic prefix
  def test_008 (self):
    vlen = 128
    syms = 4
    bin1 = vlen/2 + 4
    bin1_val = 1.0
    cp_length = vlen/4
        
    expec = numpy.array(numpy.zeros(vlen), numpy.complex)
    expec[bin1] = bin1_val
    expec = concatenate([expec]*syms)
    
    epsilon = [-0.5]
    frame_trigger = numpy.concatenate([[1],[0]*(syms-1)])
    
    freq_shift = ofdm.frequency_shift_vcc(vlen, 1.0/vlen, cp_length)
    
    fft = gr.fft_vcc(vlen, True, [], True) # natural order, dc = vlen / 2
    fft_scale = gr.multiply_const_vcc([1.0/vlen]*vlen)
    
    sampler = ofdm.vector_sampler(gr.sizeof_gr_complex,vlen)
    
    trigger_vec = concatenate([[0]*(vlen+cp_length-1),[1]])
    trigger_vec = concatenate([trigger_vec]*syms)
    trigger = gr.vector_source_b(trigger_vec.tolist())
    
    src = gr.sig_source_c(vlen, gr.GR_COS_WAVE, 4.5, 1.0, 0.0) # bin vlen/2 + 4.5
    dst = gr.vector_sink_c()
    v2s = gr.vector_to_stream(gr.sizeof_gr_complex, vlen)
    
    eps = gr.vector_source_f(epsilon)
    trig = gr.vector_source_b(frame_trigger.tolist())
    
    self.fg.connect(src, (sampler,0))
    self.fg.connect(trigger, (sampler,1))    
    self.fg.connect(sampler, (freq_shift,0))
    self.fg.connect(eps, (freq_shift,1))
    self.fg.connect(trig, (freq_shift,2))
    self.fg.connect(freq_shift, fft, fft_scale, v2s, dst)
    self.fg.run()

    self.assertComplexTuplesAlmostEqual2(expec, dst.data(), 1e-5, 1e-5)  
    
    
    
  def test_100(self):
    vlen = 256
    cp_len = 12
    
    M = 10
    N = int(3e6)
    
    uut = ofdm.frequency_shift_vcc( vlen, 1.0/vlen, cp_len )
    
    trig = [0]*M
    trig[0] = 1
    
    eps = [1.]*M
        
    src1 = gr.vector_source_c( [1.]*(M*vlen), True, vlen )
    src2 = gr.vector_source_f( eps, True )
    src3 = gr.vector_source_b( trig, True )
    dst = gr.null_sink( gr.sizeof_gr_complex * vlen )
    
    limit3 = gr.head( gr.sizeof_char, N )
    
    self.fg.connect( src1, ( uut, 0 ) )
    self.fg.connect( src2, ( uut, 1 ) )
    self.fg.connect( src3, limit3, ( uut, 2 ) )
    self.fg.connect( uut, dst )
    
    r = time_it( self.fg )
    
    print "Rate %s" % \
      ( eng_notation.num_to_str( float( ( vlen + cp_len ) * N ) / r ) )
    
    
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
  
