#!/usr/bin/env python
# 
# Copyright 2014 Institute for Theoretical Information Technology,
#                RWTH Aachen University
#                www.ti.rwth-aachen.de
# 
# This is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 3, or (at your option)
# any later version.
# 
# This software is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
# 
# You should have received a copy of the GNU General Public License
# along with this software; see the file COPYING.  If not, write to
# the Free Software Foundation, Inc., 51 Franklin Street,
# Boston, MA 02110-1301, USA.
#

from gnuradio import gr

from numpy import concatenate
from math import pi

from ofdm import vector_sampler ,vector_sum_vcc,complex_to_arg
from ofdm import mm_frequency_estimator
from gnuradio.blocks import delay

from gr_tools import log_to_file

class morelli_foe(gr.hier_block2):
  def __init__(self, fft_length, L):
    gr.hier_block2.__init__(self, "morelli_foe",
        gr.io_signature2(2,2,gr.sizeof_gr_complex,gr.sizeof_char),
        gr.io_signature(1,1,gr.sizeof_float))
    
    data_in = (self,0)
    trig_in = (self,1)
    est_out = (self,0)
    
    #inp = gr.kludge_copy(gr.sizeof_gr_complex)
    #self.connect(data_in,inp)
    inp = data_in

    
    sampler = vector_sampler(gr.sizeof_gr_complex,fft_length)
    self.connect(inp,(sampler,0))
    self.connect(trig_in,(sampler,1))
    
    est = mm_frequency_estimator(fft_length,L)
    self.connect(sampler,est,est_out)

