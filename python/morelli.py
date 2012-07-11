#!/usr/bin/env python

from gnuradio import gr

from numpy import concatenate
from math import pi

from ofdm.ofdm_swig import vector_sampler ,vector_sum_vcc,complex_to_arg
from ofdm.ofdm_swig import mm_frequency_estimator
from gnuradio.gr import delay

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

