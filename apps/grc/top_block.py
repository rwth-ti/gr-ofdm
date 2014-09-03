#!/usr/bin/env python
##################################################
# Gnuradio Python Flow Graph
# Title: Top Block
# Generated: Wed Sep  3 22:01:39 2014
##################################################

from gnuradio import blocks
from gnuradio import eng_notation
from gnuradio import gr
from gnuradio import uhd
from gnuradio.eng_option import eng_option
from gnuradio.filter import firdes
from gnuradio.wxgui import forms
from grc_gnuradio import wxgui as grc_wxgui
from optparse import OptionParser
import math
import numpy
import ofdm
import time
import wx

class top_block(grc_wxgui.top_block_gui):

    def __init__(self):
        grc_wxgui.top_block_gui.__init__(self, title="Top Block")

        ##################################################
        # Variables
        ##################################################
        self.theta_sel = theta_sel = 0
        self.syms_per_frame = syms_per_frame = 10
        self.samp_rate = samp_rate = 3.125e6
        self.qam_size = qam_size = 4
        self.multi = multi = 1
        self.exclude_preamble = exclude_preamble = 1
        self.center_preamble = center_preamble = [1, -1j, -1, 1j]
        self.carriers = carriers = 100
        self.M = M = 256
        self.K = K = 4

        ##################################################
        # Blocks
        ##################################################
        _multi_sizer = wx.BoxSizer(wx.VERTICAL)
        self._multi_text_box = forms.text_box(
        	parent=self.GetWin(),
        	sizer=_multi_sizer,
        	value=self.multi,
        	callback=self.set_multi,
        	label='multi',
        	converter=forms.float_converter(),
        	proportion=0,
        )
        self._multi_slider = forms.slider(
        	parent=self.GetWin(),
        	sizer=_multi_sizer,
        	value=self.multi,
        	callback=self.set_multi,
        	minimum=0,
        	maximum=40,
        	num_steps=1000,
        	style=wx.SL_HORIZONTAL,
        	cast=float,
        	proportion=1,
        )
        self.Add(_multi_sizer)
        self.uhd_usrp_sink_0 = uhd.usrp_sink(
        	",".join(("", "")),
        	uhd.stream_args(
        		cpu_format="fc32",
        		channels=range(1),
        	),
        )
        self.uhd_usrp_sink_0.set_time_source("external", 0)
        self.uhd_usrp_sink_0.set_samp_rate(samp_rate)
        self.uhd_usrp_sink_0.set_center_freq(2.43e9, 0)
        self.uhd_usrp_sink_0.set_gain(0, 0)
        self.ofdm_fbmc_transmitter_hier_bc_0 = ofdm.fbmc_transmitter_hier_bc(M, K, qam_size, syms_per_frame, carriers, theta_sel, exclude_preamble, center_preamble, 1)
        self.blocks_multiply_const_vxx_1 = blocks.multiply_const_vcc((multi, ))
        self.analog_random_source_x_0 = blocks.vector_source_b(map(int, numpy.random.randint(0, qam_size, 10000000)), True)

        ##################################################
        # Connections
        ##################################################
        self.connect((self.analog_random_source_x_0, 0), (self.ofdm_fbmc_transmitter_hier_bc_0, 0))
        self.connect((self.ofdm_fbmc_transmitter_hier_bc_0, 0), (self.blocks_multiply_const_vxx_1, 0))
        self.connect((self.blocks_multiply_const_vxx_1, 0), (self.uhd_usrp_sink_0, 0))



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
        self.uhd_usrp_sink_0.set_samp_rate(self.samp_rate)

    def get_qam_size(self):
        return self.qam_size

    def set_qam_size(self, qam_size):
        self.qam_size = qam_size

    def get_multi(self):
        return self.multi

    def set_multi(self, multi):
        self.multi = multi
        self.blocks_multiply_const_vxx_1.set_k((self.multi, ))
        self._multi_slider.set_value(self.multi)
        self._multi_text_box.set_value(self.multi)

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

    def get_M(self):
        return self.M

    def set_M(self, M):
        self.M = M

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
