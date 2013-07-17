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

from gnuradio import gr, gr_unittest
import ofdm as ofdm
from vector_equalizer import vector_equalizer

import sys, numpy, random, math
from numpy import conjugate, concatenate

def pn_seq(len):
  return [random.randint(0,1)*2-1 for i in range(len)]

def pn_preamble(len):
  pn = pn_seq(len/2)
  return numpy.concatenate([[pn[i],0.0] for i in range(len/2)])

def pn_symbol(len,carriers):
  l1 = int(numpy.ceil((len-carriers)/2.0))
  l2 = len-carriers-l1
  return numpy.concatenate([[0.0]*l1,pn_preamble(carriers),[0.0]*l2])

def extend_symbol(sym,l,r):
  return numpy.concatenate([[0.0]*l,sym,[0.0]*r])

def join_syms(s1,s2):
  return numpy.concatenate([s1,s2])



class qa_ofdm (gr_unittest.TestCase):
  def setUp (self):		
    self.fg = gr.top_block ("test_block")

  def tearDown (self):
    self.fg = None

  def test_001(self):
    fft_length = 260
    carriers = 100
    shift = 20

    # select maximum estimation range
    estim_range = (fft_length-carriers)/2
    l = estim_range+shift
    r = estim_range-shift

    # create preambles
    pn1 = pn_preamble(carriers)
    pn2 = pn_preamble(carriers)
    diff_pn = concatenate([[conjugate(math.sqrt(2)*pn2[2*i]/pn1[2*i]),0.0j] for i in range(carriers/2)])	
    pn1_sym = extend_symbol(pn1,l,r)
    pn2_sym = extend_symbol(pn2,l,r)

    # block under tests
    cfo_estimator = ofdm.schmidl_cfo_estimator(fft_length,carriers,estim_range,diff_pn)

    # source, conversion, sink
    src_1 = gr.vector_source_c(pn1_sym)
    src_2 = gr.vector_source_c(pn2_sym)
    s2v_1 = gr.stream_to_vector(gr.sizeof_gr_complex,fft_length)
    s2v_2 = gr.stream_to_vector(gr.sizeof_gr_complex,fft_length)
    v2s = gr.vector_to_stream(gr.sizeof_float,2*estim_range+1)
    dst = gr.vector_sink_f()

    self.fg.connect(src_1, s2v_1, (cfo_estimator,0))
    self.fg.connect(src_2, s2v_2, (cfo_estimator,1))
    self.fg.connect(cfo_estimator,v2s,dst)

    # file output
    filesink = gr.file_sink(gr.sizeof_float,"test_cfo.float")
    vec_equ = vector_equalizer(2*estim_range+1)
    self.fg.connect(v2s,gr.float_to_complex(),
      gr.stream_to_vector(gr.sizeof_gr_complex,2*estim_range+1),
      vec_equ,gr.vector_to_stream(gr.sizeof_gr_complex,2*estim_range+1),
      gr.complex_to_float(),filesink)

    runtime=self.fg
    runtime.run()

if __name__ == '__main__':
  random.seed()
  gr_unittest.main()

