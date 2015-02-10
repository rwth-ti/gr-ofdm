#!/usr/bin/env python
##################################################
# Gnuradio Python Flow Graph
# Title: Top Block
# Generated: Tue Feb 10 16:17:57 2015
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
        self.samp_rate = samp_rate = 32000
        self.modulation = modulation = 256
        self.indices = indices = [0,60,150,220]
        self.cp_ratio = cp_ratio = 0.25
        self.N = N = 12
        self.M = M = 256

        ##################################################
        # Blocks
        ##################################################
        self.wxgui_numbersink2_0_1 = numbersink2.number_sink_f(
        	self.GetWin(),
        	unit="%",
        	minval=0,
        	maxval=100,
        	factor=100,
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
        self.Add(self.wxgui_numbersink2_0_1.win)
        self.wxgui_numbersink2_0_0_0 = numbersink2.number_sink_f(
        	self.GetWin(),
        	unit="%",
        	minval=0,
        	maxval=100,
        	factor=100,
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
        self.Add(self.wxgui_numbersink2_0_0_0.win)
        self.wxgui_numbersink2_0_0 = numbersink2.number_sink_f(
        	self.GetWin(),
        	unit="%",
        	minval=0,
        	maxval=100,
        	factor=100,
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
        	factor=100,
        	decimal_places=10,
        	ref_level=0,
        	sample_rate=samp_rate,
        	number_rate=15,
        	average=False,
        	avg_alpha=None,
        	label="User0",
        	peak_hold=False,
        	show_gauge=True,
        )
        self.Add(self.wxgui_numbersink2_0.win)
        self.ofdm_scfdma_transmitter_bc_0_2 = ofdm.scfdma_transmitter_bc(N, M, indices[1], 0, modulation, cp_ratio)
        self.ofdm_scfdma_transmitter_bc_0_1 = ofdm.scfdma_transmitter_bc(N, M, indices[0], 0, modulation, cp_ratio)
        self.ofdm_scfdma_transmitter_bc_0_0 = ofdm.scfdma_transmitter_bc(N, M, indices[3], 0, modulation, cp_ratio)
        self.ofdm_scfdma_transmitter_bc_0 = ofdm.scfdma_transmitter_bc(N, M, indices[2], 0, modulation, cp_ratio)
        self.ofdm_scfdma_receiver_cb_0 = ofdm.scfdma_receiver_cb(N, M, indices, 0, modulation, cp_ratio)
        self.blocks_throttle_0_2 = blocks.throttle(gr.sizeof_char*1, samp_rate,True)
        self.blocks_throttle_0_1 = blocks.throttle(gr.sizeof_char*1, samp_rate,True)
        self.blocks_throttle_0_0 = blocks.throttle(gr.sizeof_char*1, samp_rate,True)
        self.blocks_throttle_0 = blocks.throttle(gr.sizeof_char*1, samp_rate,True)
        self.blocks_add_xx_0 = blocks.add_vcc(1)
        self.blks2_error_rate_0_1 = grc_blks2.error_rate(
        	type='BER',
        	win_size=1000,
        	bits_per_symbol=int(math.log(modulation)/math.log(2)),
        )
        self.blks2_error_rate_0_0_0 = grc_blks2.error_rate(
        	type='BER',
        	win_size=1000,
        	bits_per_symbol=int(math.log(modulation)/math.log(2)),
        )
        self.blks2_error_rate_0_0 = grc_blks2.error_rate(
        	type='BER',
        	win_size=1000,
        	bits_per_symbol=int(math.log(modulation)/math.log(2)),
        )
        self.blks2_error_rate_0 = grc_blks2.error_rate(
        	type='BER',
        	win_size=1000,
        	bits_per_symbol=int(math.log(modulation)/math.log(2)),
        )
        self.analog_random_source_x_0_2 = blocks.vector_source_b(map(int, numpy.random.randint(0, modulation, 10000)), True)
        self.analog_random_source_x_0_1 = blocks.vector_source_b(map(int, numpy.random.randint(0, modulation, 10000)), True)
        self.analog_random_source_x_0_0 = blocks.vector_source_b(map(int, numpy.random.randint(0, modulation, 10000)), True)
        self.analog_random_source_x_0 = blocks.vector_source_b(map(int, numpy.random.randint(0, modulation, 10000)), True)

        ##################################################
        # Connections
        ##################################################
        self.connect((self.analog_random_source_x_0, 0), (self.blocks_throttle_0, 0))    
        self.connect((self.analog_random_source_x_0_0, 0), (self.blocks_throttle_0_0, 0))    
        self.connect((self.analog_random_source_x_0_1, 0), (self.blocks_throttle_0_1, 0))    
        self.connect((self.analog_random_source_x_0_2, 0), (self.blocks_throttle_0_2, 0))    
        self.connect((self.blks2_error_rate_0, 0), (self.wxgui_numbersink2_0, 0))    
        self.connect((self.blks2_error_rate_0_0, 0), (self.wxgui_numbersink2_0_0, 0))    
        self.connect((self.blks2_error_rate_0_0_0, 0), (self.wxgui_numbersink2_0_0_0, 0))    
        self.connect((self.blks2_error_rate_0_1, 0), (self.wxgui_numbersink2_0_1, 0))    
        self.connect((self.blocks_add_xx_0, 0), (self.ofdm_scfdma_receiver_cb_0, 0))    
        self.connect((self.blocks_throttle_0, 0), (self.blks2_error_rate_0_0_0, 0))    
        self.connect((self.blocks_throttle_0, 0), (self.ofdm_scfdma_transmitter_bc_0, 0))    
        self.connect((self.blocks_throttle_0_0, 0), (self.blks2_error_rate_0_1, 0))    
        self.connect((self.blocks_throttle_0_0, 0), (self.ofdm_scfdma_transmitter_bc_0_0, 0))    
        self.connect((self.blocks_throttle_0_1, 0), (self.blks2_error_rate_0, 0))    
        self.connect((self.blocks_throttle_0_1, 0), (self.ofdm_scfdma_transmitter_bc_0_1, 0))    
        self.connect((self.blocks_throttle_0_2, 0), (self.blks2_error_rate_0_0, 0))    
        self.connect((self.blocks_throttle_0_2, 0), (self.ofdm_scfdma_transmitter_bc_0_2, 0))    
        self.connect((self.ofdm_scfdma_receiver_cb_0, 0), (self.blks2_error_rate_0, 1))    
        self.connect((self.ofdm_scfdma_receiver_cb_0, 1), (self.blks2_error_rate_0_0, 1))    
        self.connect((self.ofdm_scfdma_receiver_cb_0, 2), (self.blks2_error_rate_0_0_0, 1))    
        self.connect((self.ofdm_scfdma_receiver_cb_0, 3), (self.blks2_error_rate_0_1, 1))    
        self.connect((self.ofdm_scfdma_transmitter_bc_0, 0), (self.blocks_add_xx_0, 2))    
        self.connect((self.ofdm_scfdma_transmitter_bc_0_0, 0), (self.blocks_add_xx_0, 3))    
        self.connect((self.ofdm_scfdma_transmitter_bc_0_1, 0), (self.blocks_add_xx_0, 0))    
        self.connect((self.ofdm_scfdma_transmitter_bc_0_2, 0), (self.blocks_add_xx_0, 1))    


    def get_samp_rate(self):
        return self.samp_rate

    def set_samp_rate(self, samp_rate):
        self.samp_rate = samp_rate
        self.blocks_throttle_0_1.set_sample_rate(self.samp_rate)
        self.blocks_throttle_0_2.set_sample_rate(self.samp_rate)
        self.blocks_throttle_0_0.set_sample_rate(self.samp_rate)
        self.blocks_throttle_0.set_sample_rate(self.samp_rate)

    def get_modulation(self):
        return self.modulation

    def set_modulation(self, modulation):
        self.modulation = modulation

    def get_indices(self):
        return self.indices

    def set_indices(self, indices):
        self.indices = indices

    def get_cp_ratio(self):
        return self.cp_ratio

    def set_cp_ratio(self, cp_ratio):
        self.cp_ratio = cp_ratio

    def get_N(self):
        return self.N

    def set_N(self, N):
        self.N = N

    def get_M(self):
        return self.M

    def set_M(self, M):
        self.M = M

if __name__ == '__main__':
    parser = OptionParser(option_class=eng_option, usage="%prog: [options]")
    (options, args) = parser.parse_args()
    tb = top_block()
    tb.Start(True)
    tb.Wait()
