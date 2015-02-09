#!/usr/bin/env python
##################################################
# Gnuradio Python Flow Graph
# Title: Top Block
# Generated: Mon Feb  9 15:08:05 2015
##################################################

# Call XInitThreads as the _very_ first thing.
# After some Qt import, it's too late
import ctypes
import sys
if sys.platform.startswith('linux'):
    try:
        x11 = ctypes.cdll.LoadLibrary('libX11.so')
        x11.XInitThreads()
    except:
        print "Warning: failed to XInitThreads()"

from gnuradio import blocks
from gnuradio import eng_notation
from gnuradio import filter
from gnuradio import gr
from gnuradio import wxgui
from gnuradio.eng_option import eng_option
from gnuradio.filter import firdes
from gnuradio.wxgui import numbersink2
from grc_gnuradio import blks2 as grc_blks2
from grc_gnuradio import wxgui as grc_wxgui
from optparse import OptionParser
import math
import numpy
import ofdm
import wx

class top_block(grc_wxgui.top_block_gui):

    def __init__(self):
        grc_wxgui.top_block_gui.__init__(self, title="Top Block")

        ##################################################
        # Variables
        ##################################################
        self.boundaries = boundaries = [10,35,60,85,130,155,200,235]
        self.zero_pad = zero_pad = 1
        self.theta_sel = theta_sel = 0
        self.syms_per_frame = syms_per_frame = 20
        self.samp_rate = samp_rate = 3.125e6*2/100
        self.qam_size = qam_size = 64
        self.exclude_preamble = exclude_preamble = 0
        self.carriers = carriers = [boundaries[1]-boundaries[0]+1,boundaries[3]-boundaries[2]+1,boundaries[5]-boundaries[4]+1,boundaries[7]-boundaries[6]+1]
        self.M = M = 256
        self.K = K = 4

        ##################################################
        # Blocks
        ##################################################
        self.wxgui_numbersink2_0_1 = numbersink2.number_sink_f(
        	self.GetWin(),
        	unit="%",
        	minval=0,
        	maxval=100,
        	factor=100.0,
        	decimal_places=10,
        	ref_level=0,
        	sample_rate=samp_rate,
        	number_rate=15,
        	average=False,
        	avg_alpha=None,
        	label="User4",
        	peak_hold=False,
        	show_gauge=True,
        )
        self.Add(self.wxgui_numbersink2_0_1.win)
        self.wxgui_numbersink2_0_0_0 = numbersink2.number_sink_f(
        	self.GetWin(),
        	unit="%",
        	minval=0,
        	maxval=100,
        	factor=100.0,
        	decimal_places=10,
        	ref_level=0,
        	sample_rate=samp_rate,
        	number_rate=15,
        	average=False,
        	avg_alpha=None,
        	label="User3",
        	peak_hold=False,
        	show_gauge=True,
        )
        self.Add(self.wxgui_numbersink2_0_0_0.win)
        self.wxgui_numbersink2_0_0 = numbersink2.number_sink_f(
        	self.GetWin(),
        	unit="%",
        	minval=0,
        	maxval=100,
        	factor=100.0,
        	decimal_places=10,
        	ref_level=0,
        	sample_rate=samp_rate,
        	number_rate=15,
        	average=False,
        	avg_alpha=None,
        	label="User1",
        	peak_hold=False,
        	show_gauge=True,
        )
        self.Add(self.wxgui_numbersink2_0_0.win)
        self.wxgui_numbersink2_0 = numbersink2.number_sink_f(
        	self.GetWin(),
        	unit="%",
        	minval=0,
        	maxval=100,
        	factor=100.0,
        	decimal_places=10,
        	ref_level=0,
        	sample_rate=samp_rate,
        	number_rate=15,
        	average=False,
        	avg_alpha=None,
        	label="User2",
        	peak_hold=False,
        	show_gauge=True,
        )
        self.Add(self.wxgui_numbersink2_0.win)
        self.single_pole_iir_filter_xx_0_0_0 = filter.single_pole_iir_filter_ff(0.000001, 1)
        self.single_pole_iir_filter_xx_0_0 = filter.single_pole_iir_filter_ff(0.000001, 1)
        self.single_pole_iir_filter_xx_0 = filter.single_pole_iir_filter_ff(0.000001, 1)
        self.ofdm_fbmc_transmitter_multiuser_bc_3 = ofdm.fbmc_transmitter_multiuser_bc(M, K, qam_size, syms_per_frame, boundaries[6], boundaries[7], theta_sel, exclude_preamble, 0, 1, 0)
        self.ofdm_fbmc_transmitter_multiuser_bc_2 = ofdm.fbmc_transmitter_multiuser_bc(M, K, qam_size, syms_per_frame, boundaries[4], boundaries[5], theta_sel, exclude_preamble, 0, 1, 0)
        self.ofdm_fbmc_transmitter_multiuser_bc_1 = ofdm.fbmc_transmitter_multiuser_bc(M, K, qam_size, syms_per_frame, boundaries[2], boundaries[3], theta_sel, exclude_preamble, 0, 1, 0)
        self.ofdm_fbmc_transmitter_multiuser_bc_0 = ofdm.fbmc_transmitter_multiuser_bc(M, K, qam_size, syms_per_frame, boundaries[0], boundaries[1], theta_sel, exclude_preamble, 0, 1, 0)
        self.ofdm_fbmc_symbol_estimation_vcb_0_2 = ofdm.fbmc_symbol_estimation_vcb(carriers[3], qam_size)
        self.ofdm_fbmc_symbol_estimation_vcb_0_1 = ofdm.fbmc_symbol_estimation_vcb(carriers[2], qam_size)
        self.ofdm_fbmc_symbol_estimation_vcb_0_0 = ofdm.fbmc_symbol_estimation_vcb(carriers[1], qam_size)
        self.ofdm_fbmc_symbol_estimation_vcb_0 = ofdm.fbmc_symbol_estimation_vcb(carriers[0], qam_size)
        self.ofdm_fbmc_receiver_multiuser_cb_0 = ofdm.fbmc_receiver_multiuser_cb(M, K, qam_size, syms_per_frame, boundaries, theta_sel, 0, exclude_preamble, 0, 1, 0)
        self.blocks_throttle_0_0_0_2 = blocks.throttle(gr.sizeof_char*1, samp_rate,True)
        self.blocks_throttle_0_0_0_1 = blocks.throttle(gr.sizeof_char*1, samp_rate,True)
        self.blocks_throttle_0_0_0_0 = blocks.throttle(gr.sizeof_char*1, samp_rate,True)
        self.blocks_throttle_0_0_0 = blocks.throttle(gr.sizeof_char*1, samp_rate,True)
        self.blocks_add_xx_0 = blocks.add_vcc(1)
        self.blks2_error_rate_0_0_1 = grc_blks2.error_rate(
        	type='BER',
        	win_size=1000,
        	bits_per_symbol=(int)(math.log(qam_size)/math.log(2)),
        )
        self.blks2_error_rate_0_0_0 = grc_blks2.error_rate(
        	type='BER',
        	win_size=1000,
        	bits_per_symbol=(int)(math.log(qam_size)/math.log(2)),
        )
        self.blks2_error_rate_0_0 = grc_blks2.error_rate(
        	type='BER',
        	win_size=1000,
        	bits_per_symbol=(int)(math.log(qam_size)/math.log(2)),
        )
        self.blks2_error_rate_0 = grc_blks2.error_rate(
        	type='BER',
        	win_size=1000,
        	bits_per_symbol=(int)(math.log(qam_size)/math.log(2)),
        )
        self.analog_random_source_x_0_0_0_2 = blocks.vector_source_b(map(int, numpy.random.randint(0, qam_size, 10000000)), True)
        self.analog_random_source_x_0_0_0_1 = blocks.vector_source_b(map(int, numpy.random.randint(0, qam_size, 10000000)), True)
        self.analog_random_source_x_0_0_0_0 = blocks.vector_source_b(map(int, numpy.random.randint(0, qam_size, 10000000)), True)
        self.analog_random_source_x_0_0_0 = blocks.vector_source_b(map(int, numpy.random.randint(0, qam_size, 10000000)), True)

        ##################################################
        # Connections
        ##################################################
        self.connect((self.analog_random_source_x_0_0_0, 0), (self.blocks_throttle_0_0_0, 0))    
        self.connect((self.analog_random_source_x_0_0_0_0, 0), (self.blocks_throttle_0_0_0_0, 0))    
        self.connect((self.analog_random_source_x_0_0_0_1, 0), (self.blocks_throttle_0_0_0_1, 0))    
        self.connect((self.analog_random_source_x_0_0_0_2, 0), (self.blocks_throttle_0_0_0_2, 0))    
        self.connect((self.blks2_error_rate_0, 0), (self.single_pole_iir_filter_xx_0, 0))    
        self.connect((self.blks2_error_rate_0_0, 0), (self.single_pole_iir_filter_xx_0_0, 0))    
        self.connect((self.blks2_error_rate_0_0_0, 0), (self.wxgui_numbersink2_0_0, 0))    
        self.connect((self.blks2_error_rate_0_0_1, 0), (self.single_pole_iir_filter_xx_0_0_0, 0))    
        self.connect((self.blocks_add_xx_0, 0), (self.ofdm_fbmc_receiver_multiuser_cb_0, 0))    
        self.connect((self.blocks_throttle_0_0_0, 0), (self.blks2_error_rate_0_0_0, 0))    
        self.connect((self.blocks_throttle_0_0_0, 0), (self.ofdm_fbmc_transmitter_multiuser_bc_2, 0))    
        self.connect((self.blocks_throttle_0_0_0_0, 0), (self.blks2_error_rate_0_0_1, 0))    
        self.connect((self.blocks_throttle_0_0_0_0, 0), (self.ofdm_fbmc_transmitter_multiuser_bc_3, 0))    
        self.connect((self.blocks_throttle_0_0_0_1, 0), (self.blks2_error_rate_0_0, 0))    
        self.connect((self.blocks_throttle_0_0_0_1, 0), (self.ofdm_fbmc_transmitter_multiuser_bc_1, 0))    
        self.connect((self.blocks_throttle_0_0_0_2, 0), (self.blks2_error_rate_0, 0))    
        self.connect((self.blocks_throttle_0_0_0_2, 0), (self.ofdm_fbmc_transmitter_multiuser_bc_0, 0))    
        self.connect((self.ofdm_fbmc_receiver_multiuser_cb_0, 0), (self.ofdm_fbmc_symbol_estimation_vcb_0, 0))    
        self.connect((self.ofdm_fbmc_receiver_multiuser_cb_0, 1), (self.ofdm_fbmc_symbol_estimation_vcb_0_0, 0))    
        self.connect((self.ofdm_fbmc_receiver_multiuser_cb_0, 2), (self.ofdm_fbmc_symbol_estimation_vcb_0_1, 0))    
        self.connect((self.ofdm_fbmc_receiver_multiuser_cb_0, 3), (self.ofdm_fbmc_symbol_estimation_vcb_0_2, 0))    
        self.connect((self.ofdm_fbmc_symbol_estimation_vcb_0, 0), (self.blks2_error_rate_0, 1))    
        self.connect((self.ofdm_fbmc_symbol_estimation_vcb_0_0, 0), (self.blks2_error_rate_0_0, 1))    
        self.connect((self.ofdm_fbmc_symbol_estimation_vcb_0_1, 0), (self.blks2_error_rate_0_0_0, 1))    
        self.connect((self.ofdm_fbmc_symbol_estimation_vcb_0_2, 0), (self.blks2_error_rate_0_0_1, 1))    
        self.connect((self.ofdm_fbmc_transmitter_multiuser_bc_0, 0), (self.blocks_add_xx_0, 0))    
        self.connect((self.ofdm_fbmc_transmitter_multiuser_bc_1, 0), (self.blocks_add_xx_0, 1))    
        self.connect((self.ofdm_fbmc_transmitter_multiuser_bc_2, 0), (self.blocks_add_xx_0, 2))    
        self.connect((self.ofdm_fbmc_transmitter_multiuser_bc_3, 0), (self.blocks_add_xx_0, 3))    
        self.connect((self.single_pole_iir_filter_xx_0, 0), (self.wxgui_numbersink2_0_0_0, 0))    
        self.connect((self.single_pole_iir_filter_xx_0_0, 0), (self.wxgui_numbersink2_0_1, 0))    
        self.connect((self.single_pole_iir_filter_xx_0_0_0, 0), (self.wxgui_numbersink2_0, 0))    


    def get_boundaries(self):
        return self.boundaries

    def set_boundaries(self, boundaries):
        self.boundaries = boundaries
        self.set_carriers([self.boundaries[1]-self.boundaries[0]+1,self.boundaries[3]-self.boundaries[2]+1,self.boundaries[5]-self.boundaries[4]+1,self.boundaries[7]-self.boundaries[6]+1])

    def get_zero_pad(self):
        return self.zero_pad

    def set_zero_pad(self, zero_pad):
        self.zero_pad = zero_pad

    def get_theta_sel(self):
        return self.theta_sel

    def set_theta_sel(self, theta_sel):
        self.theta_sel = theta_sel

    def get_syms_per_frame(self):
        return self.syms_per_frame

    def set_syms_per_frame(self, syms_per_frame):
        self.syms_per_frame = syms_per_frame

    def get_samp_rate(self):
        return self.samp_rate

    def set_samp_rate(self, samp_rate):
        self.samp_rate = samp_rate
        self.blocks_throttle_0_0_0_0.set_sample_rate(self.samp_rate)
        self.blocks_throttle_0_0_0.set_sample_rate(self.samp_rate)
        self.blocks_throttle_0_0_0_2.set_sample_rate(self.samp_rate)
        self.blocks_throttle_0_0_0_1.set_sample_rate(self.samp_rate)

    def get_qam_size(self):
        return self.qam_size

    def set_qam_size(self, qam_size):
        self.qam_size = qam_size

    def get_exclude_preamble(self):
        return self.exclude_preamble

    def set_exclude_preamble(self, exclude_preamble):
        self.exclude_preamble = exclude_preamble

    def get_carriers(self):
        return self.carriers

    def set_carriers(self, carriers):
        self.carriers = carriers

    def get_M(self):
        return self.M

    def set_M(self, M):
        self.M = M

    def get_K(self):
        return self.K

    def set_K(self, K):
        self.K = K

if __name__ == '__main__':
    parser = OptionParser(option_class=eng_option, usage="%prog: [options]")
    (options, args) = parser.parse_args()
    tb = top_block()
    tb.Start(True)
    tb.Wait()
