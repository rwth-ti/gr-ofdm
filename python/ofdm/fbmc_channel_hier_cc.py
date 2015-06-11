#!/usr/bin/env python
# -*- coding: utf-8 -*-
# 
# Copyright 2014 <+YOU OR YOUR COMPANY+>.
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

from gnuradio import analog
from gnuradio import blocks
from gnuradio import channels
from gnuradio import gr
from gnuradio.filter import firdes
from grc_gnuradio import blks2 as grc_blks2
import math

class fbmc_channel_hier_cc(gr.hier_block2):
    """
    docstring for block fbmc_channel_hier_cc
    """
    def __init__(self, M=1024, K=4, syms_per_frame=10, exclude_multipath=0, sel_taps=0, freq_offset=0, exclude_noise=0, sel_noise_type=0, SNR=20, exclude_preamble=0, sel_preamble=0, zero_pads=1, extra_pad=False):
        gr.hier_block2.__init__(self,
            "fbmc_channel_hier_cc",
            gr.io_signature(1, 1, gr.sizeof_gr_complex*1),
            gr.io_signature(1, 1, gr.sizeof_gr_complex*1),
        )

        ##################################################
        # Parameters
        ##################################################
        self.freq_offset = freq_offset
        self.sel_noise_type = sel_noise_type
        self.sel_taps = sel_taps
        self.SNR = SNR
        self.exclude_multipath = exclude_multipath
        self.exclude_noise = exclude_noise
        self.exclude_preamble = exclude_preamble
        self.K = K
        self.M = M
        self.syms_per_frame = syms_per_frame
        self.zero_pads =zero_pads

        ##################################################
        # Variables
        ##################################################
        self.taps = taps = (1)
        if sel_taps == 0: #epa
            self.taps = taps = (0.998160541385960,0.0605566335500750,0.00290305927764350)
        elif sel_taps == 1: #eva
            self.taps = taps = (0.748212004186014,0.317358833370450,0.572776845645705,0,0.0538952624324030,0.0874078808126807,0,0,0,0.0276407988816600,0,0,0,0.00894438719057275)
        elif sel_taps ==2: #etu
            self.taps = taps = (0.463990169152204,0.816124099344485,0,0.292064507384192,0,0,0,0,0.146379002496595,0,0,0,0.0923589067029112,0,0,0,0,0,0,0,0,0,0,0,0,0.0582745305123628)
        
        self.noise_type = analog.GR_GAUSSIAN
        if sel_noise_type == 200:
            self.noise_type = analog.GR_UNIFORM
        elif sel_noise_type ==201:
            self.noise_type = analog.GR_GAUSSIAN
        elif sel_noise_type == 202:
            self.noise_type = analog.GR_LAPLACIAN
        elif sel_noise_type ==203:
            self.noise_type = analog.GR_IMPULSE

        if sel_preamble == 0: # standard one vector center preamble [1,-j,-1,j]
            self.num_center_vectors = num_center_vectors = 1
        elif sel_preamble == 1: # standard preamble with triple repetition
            self.num_center_vectors = num_center_vectors = 3
        elif sel_preamble ==2: # IAM-R preamble [1, -1,-1, 1]
            self.num_center_vectors = num_center_vectors = 1
        else: # standard one vector center preamble [1,-j,-1,j]
            self.num_center_vectors = num_center_vectors = 1

        if extra_pad:
            self.total_zeros = total_zeros = 1+2*zero_pads
        else:
            self.total_zeros = total_zeros = 2*zero_pads

        

        # normalizing factor to be added if normalization takes place in transmitter
        self.normalizing_factor = float(1)/(M*.6863)
        if exclude_preamble:
            self.amp = self.normalizing_factor*math.sqrt((10**(float(-1*SNR)/10))*(2*K*M+(2*syms_per_frame-1)*M)/(4*syms_per_frame))/math.sqrt(2)
        else:
            syms_per_frame_2 = syms_per_frame + (self.num_center_vectors+self.total_zeros)/2
            self.amp = self.normalizing_factor*math.sqrt((10**(float(-1*SNR)/10))*(M*(syms_per_frame+self.num_center_vectors)/(syms_per_frame+self.num_center_vectors+self.total_zeros))*((K*M+(2*syms_per_frame_2-1)*M/2)/(M*syms_per_frame_2)))/math.sqrt(2)
            # self.amp = self.normalizing_factor*math.sqrt((10**(float(-1*SNR)/10))*(M*(syms_per_frame+self.num_center_vectors)/(syms_per_frame+self.num_center_vectors+self.total_zeros))*((K*M+(2*syms_per_frame-1)*M/2)/(M*syms_per_frame)))/math.sqrt(2)

        ##################################################
        # Blocks
        ##################################################
        self.channels_channel_model_0 = channels.channel_model(
            noise_voltage=0.0,
            frequency_offset=freq_offset,
            epsilon=1.0,
            taps=taps,
            noise_seed=0,
            block_tags=False
        )
        self.blocks_null_source_0 = blocks.null_source(gr.sizeof_gr_complex*1)
        self.blocks_add_xx_0 = blocks.add_vcc(1)
        self.blks2_selector_1 = grc_blks2.selector(
            item_size=gr.sizeof_gr_complex*1,
            num_inputs=2,
            num_outputs=1,
            input_index=exclude_noise,
            output_index=0,
        )
        self.blks2_selector_0 = grc_blks2.selector(
            item_size=gr.sizeof_gr_complex*1,
            num_inputs=2,
            num_outputs=1,
            input_index=exclude_multipath,
            output_index=0,
        )
        self.analog_fastnoise_source_x_0 = analog.fastnoise_source_c(self.noise_type, self.amp, 0, 8192)

        ##################################################
        # Connections
        ##################################################
        self.connect((self, 0), (self.channels_channel_model_0, 0))
        self.connect((self, 0), (self.blks2_selector_0, 1))
        self.connect((self.channels_channel_model_0, 0), (self.blks2_selector_0, 0))
        self.connect((self.blks2_selector_0, 0), (self.blocks_add_xx_0, 0))
        self.connect((self.analog_fastnoise_source_x_0, 0), (self.blks2_selector_1, 0))
        self.connect((self.blocks_null_source_0, 0), (self.blks2_selector_1, 1))
        self.connect((self.blks2_selector_1, 0), (self.blocks_add_xx_0, 1))
        self.connect((self.blocks_add_xx_0, 0), (self, 0))

    def set_SNR(self, SNR):
        self.SNR = SNR
        if self.exclude_preamble:
            self.amp = self.normalizing_factor*math.sqrt((10**(float(-1*self.SNR)/10))*(2*self.K*self.M+(2*self.syms_per_frame-1)*self.M)/(4*self.syms_per_frame))/math.sqrt(2)
        else:
            self.amp = self.normalizing_factor*math.sqrt((10**(float(-1*self.SNR)/10))*(self.M*(self.syms_per_frame+self.num_center_vectors)/(self.syms_per_frame+self.num_center_vectors+self.total_zeros))*((self.K*self.M+(2*self.syms_per_frame-1)*self.M/2)/(self.M*self.syms_per_frame)))/math.sqrt(2)
        self.analog_fastnoise_source_x_0.set_amplitude(self.amp)
        # print self.analog_fastnoise_source_x_0
        # ##################################################
        # # Connections
        # ##################################################
        # self.connect((self, 0), (self.channels_channel_model_0, 0))
        # self.connect((self, 0), (self.blks2_selector_0, 1))
        # self.connect((self.channels_channel_model_0, 0), (self.blks2_selector_0, 0))
        # self.connect((self.blks2_selector_0, 0), (self.blocks_add_xx_0, 0))
        # self.connect((self.analog_fastnoise_source_x_0, 0), (self.blks2_selector_1, 0))
        # self.connect((self.blocks_null_source_0, 0), (self.blks2_selector_1, 1))
        # self.connect((self.blks2_selector_1, 0), (self.blocks_add_xx_0, 1))
        # self.connect((self.blocks_add_xx_0, 0), (self, 0))
