#!/usr/bin/env python
##################################################
# Gnuradio Python Flow Graph
# Title: Top Block
# Generated: Wed Sep  3 19:06:38 2014
##################################################

from gnuradio import blocks
from gnuradio import eng_notation
from gnuradio import gr
from gnuradio import wxgui
from gnuradio.eng_option import eng_option
from gnuradio.filter import firdes
from gnuradio.wxgui import forms
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
        self.M = M = 1024
        self.theta_sel = theta_sel = 0
        self.syms_per_frame = syms_per_frame = 10
        self.samp_rate = samp_rate = 3.125e6
        self.qam_size = qam_size = 4
        self.exclude_preamble = exclude_preamble = 1
        self.center_preamble = center_preamble = [1, -1j, -1, 1j]
        self.carriers = carriers = M-100
        self.SNR = SNR = 10
        self.K = K = 4

        ##################################################
        # Blocks
        ##################################################
        _SNR_sizer = wx.BoxSizer(wx.VERTICAL)
        self._SNR_text_box = forms.text_box(
        	parent=self.GetWin(),
        	sizer=_SNR_sizer,
        	value=self.SNR,
        	callback=self.set_SNR,
        	label='SNR',
        	converter=forms.float_converter(),
        	proportion=0,
        )
        self._SNR_slider = forms.slider(
        	parent=self.GetWin(),
        	sizer=_SNR_sizer,
        	value=self.SNR,
        	callback=self.set_SNR,
        	minimum=-50,
        	maximum=150,
        	num_steps=400,
        	style=wx.SL_HORIZONTAL,
        	cast=float,
        	proportion=1,
        )
        self.Add(_SNR_sizer)
        self.wxgui_numbersink2_0 = numbersink2.number_sink_f(
        	self.GetWin(),
        	unit="%",
        	minval=0,
        	maxval=100,
        	factor=100,
        	decimal_places=10,
        	ref_level=0,
        	sample_rate=2*samp_rate,
        	number_rate=15,
        	average=False,
        	avg_alpha=None,
        	label="BER",
        	peak_hold=False,
        	show_gauge=True,
        )
        self.Add(self.wxgui_numbersink2_0.win)
        self.ofdm_fbmc_transmitter_hier_bc_0 = ofdm.fbmc_transmitter_hier_bc(M, K, qam_size, syms_per_frame, carriers, theta_sel, exclude_preamble, center_preamble, 1)
        self.ofdm_fbmc_receiver_hier_cb_0 = ofdm.fbmc_receiver_hier_cb(M, K, qam_size, syms_per_frame, carriers, theta_sel, 0, exclude_preamble, center_preamble, 1)
        self.ofdm_fbmc_channel_hier_cc_0 = ofdm.fbmc_channel_hier_cc(M, K, syms_per_frame, 1, 0, 0, 0, 201, SNR, exclude_preamble, 1)
        self.blocks_throttle_0 = blocks.throttle(gr.sizeof_char*1, samp_rate,True)
        self.blks2_error_rate_0 = grc_blks2.error_rate(
        	type='BER',
        	win_size=1000,
        	bits_per_symbol=(int)(math.log(qam_size)/math.log(2)),
        )
        self.analog_random_source_x_0 = blocks.vector_source_b(map(int, numpy.random.randint(0, qam_size, 10000000)), True)

        ##################################################
        # Connections
        ##################################################
        self.connect((self.blks2_error_rate_0, 0), (self.wxgui_numbersink2_0, 0))
        self.connect((self.analog_random_source_x_0, 0), (self.blocks_throttle_0, 0))
        self.connect((self.blocks_throttle_0, 0), (self.ofdm_fbmc_transmitter_hier_bc_0, 0))
        self.connect((self.ofdm_fbmc_channel_hier_cc_0, 0), (self.ofdm_fbmc_receiver_hier_cb_0, 0))
        self.connect((self.ofdm_fbmc_receiver_hier_cb_0, 0), (self.blks2_error_rate_0, 1))
        self.connect((self.blocks_throttle_0, 0), (self.blks2_error_rate_0, 0))
        self.connect((self.ofdm_fbmc_transmitter_hier_bc_0, 0), (self.ofdm_fbmc_channel_hier_cc_0, 0))



    def get_M(self):
        return self.M

    def set_M(self, M):
        self.M = M
        self.set_carriers(self.M-100)

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
        self.blocks_throttle_0.set_sample_rate(self.samp_rate)

    def get_qam_size(self):
        return self.qam_size

    def set_qam_size(self, qam_size):
        self.qam_size = qam_size

    def get_exclude_preamble(self):
        return self.exclude_preamble

    def set_exclude_preamble(self, exclude_preamble):
        self.exclude_preamble = exclude_preamble

    def get_center_preamble(self):
        return self.center_preamble

    def set_center_preamble(self, center_preamble):
        self.center_preamble = center_preamble

    def get_carriers(self):
        return self.carriers

    def set_carriers(self, carriers):
        self.carriers = carriers

    def get_SNR(self):
        return self.SNR

    def set_SNR(self, SNR):
        self.SNR = SNR
        self.ofdm_fbmc_channel_hier_cc_0.set_SNR(self.SNR)
        self._SNR_slider.set_value(self.SNR)
        self._SNR_text_box.set_value(self.SNR)

    def get_K(self):
        return self.K

    def set_K(self, K):
        self.K = K

if __name__ == '__main__':
    import ctypes
    import sys
    if sys.platform.startswith('linux'):
        try:
            x11 = ctypes.cdll.LoadLibrary('libX11.so')
            x11.XInitThreads()
        except:
            print "Warning: failed to XInitThreads()"
    parser = OptionParser(option_class=eng_option, usage="%prog: [options]")
    (options, args) = parser.parse_args()
    tb = top_block()
    tb.Start(True)
    tb.Wait()
