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

from numpy import absolute
from cmath import exp
from gnuradio import eng_notation
from gnuradio import gr, gru
from gnuradio.eng_option import eng_option
from math import pi, log10, sqrt, log
import numpy
import random

import ofdm as ofdm
import numpy, scipy

from gr_tools import log_to_file

class awgn_channel(gr.hier_block2):
  def __init__(self, noise_voltage, frequency_offset):
    gr.hier_block2.__init__(self, "awgn_channel", 
        gr.io_signature(1,1,gr.sizeof_gr_complex),
        gr.io_signature(1,1,gr.sizeof_gr_complex))

    self.noise_adder = gr.add_cc()
    self.noise = gr.noise_source_c(gr.GR_GAUSSIAN,noise_voltage)
    self.offset = gr.sig_source_c(1, gr.GR_SIN_WAVE, frequency_offset, 1.0, 0.0)
    self.mixer_offset = gr.multiply_cc()

    self.connect(self, (self.mixer_offset,0))
    self.connect(self.offset,(self.mixer_offset,1))
    self.connect(self.mixer_offset, (self.noise_adder,1))
    self.connect(self.noise, (self.noise_adder,0))
    self.connect(self.noise_adder, self)

    try:
        gr.hier_block.update_var_names(self, "awgn_channel", vars())
        gr.hier_block.update_var_names(self, "awgn_channel", vars(self))
    except:
        pass


class variable_awgn_channel(gr.hier_block2):
  def __init__(self, noise_voltage, sensitivity):
    gr.hier_block2.__init__(self, "variable_awgn_channel", 
        gr.io_signature(1,1,gr.sizeof_gr_complex),
        gr.io_signature(1,1,gr.sizeof_gr_complex))

    self.noise_adder = gr.add_cc()
    self.noise = gr.noise_source_c(gr.GR_GAUSSIAN,noise_voltage)
    self.noise_amp = gr.multiply_cc()
    self.offset = gr.frequency_modulator_fc(sensitivity)
    self.mixer_offset = gr.multiply_cc()

    self.connect(self, (self.mixer_offset,0))
    self.connect(self.offset,(self.mixer_offset,1))
    self.connect(self.mixer_offset, (self.noise_adder,1))
    self.connect(self.noise, (self.noise_amp,0))
    self.connect(self.noise_amp, (self.noise_adder,0))
    self.connect(self.noise_adder, self)

    try:
        gr.hier_block.update_var_names(self, "var_awgn_channel", vars())
        gr.hier_block.update_var_names(self, "var_awgn_channel", vars(self))
    except:
        pass


class multipath_channel(gr.hier_block2):
  def __init__(self):
    gr.hier_block2.__init__(self, "multipath_channel", 
        gr.io_signature(1,1,gr.sizeof_gr_complex),
        gr.io_signature(1,1,gr.sizeof_gr_complex))

    #self.taps = [1.0, .2, 0.0, .1, .08, -.4, .12, -.2, 0, 0, 0, .3]

    self.length = 8
    a = 24.0/10 / (8-1) * log(10.0)
    x = [exp(-a*i) for i in range(self.length)]

    # i.i.d. in [0.0,1.0)
    y = [0.27599478430000000,  0.34303317230500000, 0.24911284691022517,
         0.19471409268935069,  0.98794533144803298, 0.36772813703828844,
         0.008240459082489604, 0.26629172049386607, 0.3308407474924715,
         0.17198856343625069,  0.30433761100062451, 0.55081856590567013,
         0.41045093976820779,  0.28842125692731335, 0.54050922175406835,
         0.419704078137786185, 0.23368258618886051, 0.78509149901607134,
         0.29433609371058278,  0.60536839932433595]

    tapsize = 4
 
    self.taps = numpy.array([0.0j]*(self.length*tapsize))
    for i in range(self.length):
      self.taps[i*tapsize] = x[i]  * exp(1j*2*pi*y[i])

    gain = sqrt(sum(absolute(self.taps)**2))
    self.taps /= gain

    self.chan = gr.fir_filter_ccc(1, self.taps)
    self.connect(self, self.chan, self)

    try:
        gr.hier_block.update_var_names(self, "multipath_channel", vars())
        gr.hier_block.update_var_names(self, "multipath_channel", vars(self))
    except:
        pass


class fading_channel(gr.hier_block2):
  def __init__(self, noise_voltage, frequency_offset):
    gr.hier_block2.__init__(self, "fading_channel", 
        gr.io_signature(1,1,gr.sizeof_gr_complex),
        gr.io_signature(1,1,gr.sizeof_gr_complex))

    self.awgn = awgn_channel(noise_voltage, frequency_offset)
    self.multipath = multipath_channel()
    self.connect(self,self.awgn,self.multipath,self)



class time_variant_rayleigh_channel ( gr.hier_block2 ):
  def __init__ ( self, noise_power, coherence_time, taps ):
    gr.hier_block2.__init__(self,
      "fading_channel", 
      gr.io_signature( 1, 1, gr.sizeof_gr_complex ),
      gr.io_signature( 1, 1, gr.sizeof_gr_complex ) )

    inp = gr.kludge_copy( gr.sizeof_gr_complex )
    self.connect( self, inp )
    
 
    
    tap1_delay = gr.delay( gr.sizeof_gr_complex, 1 )
    tap2_delay = gr.delay( gr.sizeof_gr_complex, 2 )
    self.connect( inp, tap1_delay )
    self.connect( inp, tap2_delay )
    
    
    fd = 100
    z = numpy.arange(-fd+0.1,fd,0.1)
    t = numpy.sqrt(1. / ( pi * fd * numpy.sqrt( 1. - (z/fd)**2 ) ) )

    
    tap1_noise = ofdm.complex_white_noise( 0.0, taps[0] )
    tap1_filter = gr.fft_filter_ccc(1, t)
    self.connect( tap1_noise, tap1_filter )
    
    tap1_mult = gr.multiply_cc()
    self.connect( tap1_filter, (tap1_mult,0) )
    self.connect( tap1_delay, (tap1_mult,1) )
    
    
    tap2_noise = ofdm.complex_white_noise( 0.0, taps[1] )
    tap2_filter = gr.fft_filter_ccc(1, t)
    
    self.connect( tap2_noise, tap2_filter )
    
    tap2_mult = gr.multiply_cc()
    self.connect( tap2_filter, (tap2_mult,0) )
    self.connect( tap2_delay, (tap2_mult,1) )
    
    noise_src = ofdm.complex_white_noise( 0.0, sqrt( noise_power ) )
    chan = gr.add_cc()
    
    self.connect( inp, (chan,0) )
    self.connect( tap1_mult, (chan,1) )
    self.connect( tap2_mult, (chan,2) )
    self.connect( noise_src, (chan,3) )
    
    self.connect( chan, self )
    
    log_to_file( self, tap1_filter, "data/tap1_filter.compl")
    log_to_file( self, tap1_filter, "data/tap1_filter.float", mag=True)
    log_to_file( self, tap2_filter, "data/tap2_filter.compl")
    log_to_file( self, tap2_filter, "data/tap2_filter.float", mag=True)
    
    
    
    
    
    
    
