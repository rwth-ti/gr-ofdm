#!/usr/bin/env python
##################################################
# Gnuradio Python Flow Graph
# Title: Top Block
# Generated: Sat Aug 30 17:14:53 2014
##################################################

from gnuradio import blocks
from gnuradio import eng_notation
from gnuradio import fft
from gnuradio import gr
from gnuradio import wxgui
from gnuradio.eng_option import eng_option
from gnuradio.fft import window
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
        self.zero_pads = zero_pads = 1
        self.center_preamble = center_preamble = [1, -1j, -1, 1j]
        self.M = M = 1024
        self.theta_sel = theta_sel = 0
        self.syms_per_frame = syms_per_frame = 10
        self.samp_rate = samp_rate = 32000
        self.qam_size = qam_size = 4
        self.preamble = preamble = [0]*M*zero_pads+center_preamble*((int)(M/len(center_preamble)))+[0]*M*zero_pads
        self.exclude_preamble = exclude_preamble = 1
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
        	sample_rate=samp_rate,
        	number_rate=15,
        	average=False,
        	avg_alpha=None,
        	label="BER",
        	peak_hold=False,
        	show_gauge=True,
        )
        self.Add(self.wxgui_numbersink2_0.win)
        self.ofdm_fbmc_weighted_spreading_vcvc_0 = ofdm.fbmc_weighted_spreading_vcvc(M, K)
        self.ofdm_fbmc_weighted_despreading_vcvc_0 = ofdm.fbmc_weighted_despreading_vcvc(M, K)
        self.ofdm_fbmc_vector_reshape_vcvc_1 = ofdm.fbmc_vector_reshape_vcvc(M, K*M)
        self.ofdm_fbmc_vector_reshape_vcvc_0 = ofdm.fbmc_vector_reshape_vcvc(K*M, M)
        self.ofdm_fbmc_symbol_estimation_vcb_0 = ofdm.fbmc_symbol_estimation_vcb(M, qam_size)
        self.ofdm_fbmc_symbol_creation_bvc_0 = ofdm.fbmc_symbol_creation_bvc(M, qam_size)
        self.ofdm_fbmc_subchannel_processing_vcvc_0 = ofdm.fbmc_subchannel_processing_vcvc(M, syms_per_frame, (preamble), 0)
        self.ofdm_fbmc_separate_vcvc_1 = ofdm.fbmc_separate_vcvc(M, 2)
        self.ofdm_fbmc_remove_preamble_vcvc_0 = ofdm.fbmc_remove_preamble_vcvc(M, syms_per_frame, 3*M)
        self.ofdm_fbmc_overlapping_serial_to_parallel_cvc_0 = ofdm.fbmc_overlapping_serial_to_parallel_cvc(M)
        self.ofdm_fbmc_overlapping_parallel_to_serial_vcc_0 = ofdm.fbmc_overlapping_parallel_to_serial_vcc(M)
        self.ofdm_fbmc_oqam_preprocessing_vcvc_0 = ofdm.fbmc_oqam_preprocessing_vcvc(M, 0, 0)
        self.ofdm_fbmc_oqam_postprocessing_vcvc_0 = ofdm.fbmc_oqam_postprocessing_vcvc(M, 0, 0)
        self.ofdm_fbmc_insert_preamble_vcvc_0 = ofdm.fbmc_insert_preamble_vcvc(M, syms_per_frame, preamble)
        self.ofdm_fbmc_channel_hier_cc_0 = ofdm.fbmc_channel_hier_cc(M, K, syms_per_frame, 0, 0, 0, 1, 201, SNR, exclude_preamble, 1)
        self.fft_vxx_1 = fft.fft_vcc(K*M, True, ([]), True, 1)
        self.fft_vxx_0 = fft.fft_vcc(M*K, False, ([]), True, 1)
        self.blocks_throttle_0 = blocks.throttle(gr.sizeof_char*1, samp_rate,True)
        self.blocks_skiphead_0_0 = blocks.skiphead(gr.sizeof_gr_complex*M, 0)
        self.blocks_multiply_const_vxx_0 = blocks.multiply_const_vcc(([1.0/(M*K*0.6863)]*M*K))
        self.blks2_selector_0_0 = grc_blks2.selector(
        	item_size=gr.sizeof_gr_complex*M,
        	num_inputs=2,
        	num_outputs=1,
        	input_index=exclude_preamble,
        	output_index=0,
        )
        self.blks2_selector_0 = grc_blks2.selector(
        	item_size=gr.sizeof_gr_complex*M,
        	num_inputs=2,
        	num_outputs=1,
        	input_index=exclude_preamble,
        	output_index=0,
        )
        self.blks2_error_rate_0 = grc_blks2.error_rate(
        	type='BER',
        	win_size=1000,
        	bits_per_symbol=(int)(math.log(qam_size)/math.log(2)),
        )
        self.analog_random_source_x_0 = blocks.vector_source_b(map(int, numpy.random.randint(0, qam_size, 1000000)), True)

        ##################################################
        # Connections
        ##################################################
        self.connect((self.blocks_skiphead_0_0, 0), (self.ofdm_fbmc_oqam_postprocessing_vcvc_0, 0))
        self.connect((self.ofdm_fbmc_oqam_postprocessing_vcvc_0, 0), (self.ofdm_fbmc_symbol_estimation_vcb_0, 0))
        self.connect((self.blks2_selector_0_0, 0), (self.blocks_skiphead_0_0, 0))
        self.connect((self.ofdm_fbmc_remove_preamble_vcvc_0, 0), (self.blks2_selector_0_0, 0))
        self.connect((self.ofdm_fbmc_subchannel_processing_vcvc_0, 0), (self.blks2_selector_0_0, 1))
        self.connect((self.ofdm_fbmc_insert_preamble_vcvc_0, 0), (self.blks2_selector_0, 0))
        self.connect((self.ofdm_fbmc_oqam_preprocessing_vcvc_0, 0), (self.blks2_selector_0, 1))
        self.connect((self.blks2_error_rate_0, 0), (self.wxgui_numbersink2_0, 0))
        self.connect((self.ofdm_fbmc_symbol_estimation_vcb_0, 0), (self.blks2_error_rate_0, 1))
        self.connect((self.blocks_throttle_0, 0), (self.blks2_error_rate_0, 0))
        self.connect((self.ofdm_fbmc_oqam_preprocessing_vcvc_0, 0), (self.ofdm_fbmc_insert_preamble_vcvc_0, 0))
        self.connect((self.ofdm_fbmc_subchannel_processing_vcvc_0, 0), (self.ofdm_fbmc_remove_preamble_vcvc_0, 0))
        self.connect((self.fft_vxx_1, 0), (self.blocks_multiply_const_vxx_0, 0))
        self.connect((self.ofdm_fbmc_overlapping_parallel_to_serial_vcc_0, 0), (self.ofdm_fbmc_channel_hier_cc_0, 0))
        self.connect((self.ofdm_fbmc_symbol_creation_bvc_0, 0), (self.ofdm_fbmc_oqam_preprocessing_vcvc_0, 0))
        self.connect((self.blocks_throttle_0, 0), (self.ofdm_fbmc_symbol_creation_bvc_0, 0))
        self.connect((self.analog_random_source_x_0, 0), (self.blocks_throttle_0, 0))
        self.connect((self.blks2_selector_0, 0), (self.ofdm_fbmc_weighted_spreading_vcvc_0, 0))
        self.connect((self.ofdm_fbmc_weighted_spreading_vcvc_0, 0), (self.fft_vxx_0, 0))
        self.connect((self.fft_vxx_0, 0), (self.ofdm_fbmc_vector_reshape_vcvc_0, 0))
        self.connect((self.ofdm_fbmc_vector_reshape_vcvc_0, 0), (self.ofdm_fbmc_separate_vcvc_1, 0))
        self.connect((self.ofdm_fbmc_separate_vcvc_1, 0), (self.ofdm_fbmc_overlapping_parallel_to_serial_vcc_0, 0))
        self.connect((self.ofdm_fbmc_separate_vcvc_1, 1), (self.ofdm_fbmc_overlapping_parallel_to_serial_vcc_0, 1))
        self.connect((self.ofdm_fbmc_overlapping_serial_to_parallel_cvc_0, 0), (self.ofdm_fbmc_vector_reshape_vcvc_1, 0))
        self.connect((self.ofdm_fbmc_vector_reshape_vcvc_1, 0), (self.fft_vxx_1, 0))
        self.connect((self.blocks_multiply_const_vxx_0, 0), (self.ofdm_fbmc_weighted_despreading_vcvc_0, 0))
        self.connect((self.ofdm_fbmc_weighted_despreading_vcvc_0, 0), (self.ofdm_fbmc_subchannel_processing_vcvc_0, 0))
        self.connect((self.ofdm_fbmc_channel_hier_cc_0, 0), (self.ofdm_fbmc_overlapping_serial_to_parallel_cvc_0, 0))



    def get_zero_pads(self):
        return self.zero_pads

    def set_zero_pads(self, zero_pads):
        self.zero_pads = zero_pads
        self.set_preamble([0]*self.M*self.zero_pads+self.center_preamble*((int)(self.M/len(self.center_preamble)))+[0]*self.M*self.zero_pads)

    def get_center_preamble(self):
        return self.center_preamble

    def set_center_preamble(self, center_preamble):
        self.center_preamble = center_preamble
        self.set_preamble([0]*self.M*self.zero_pads+self.center_preamble*((int)(self.M/len(self.center_preamble)))+[0]*self.M*self.zero_pads)

    def get_M(self):
        return self.M

    def set_M(self, M):
        self.M = M
        self.set_preamble([0]*self.M*self.zero_pads+self.center_preamble*((int)(self.M/len(self.center_preamble)))+[0]*self.M*self.zero_pads)
        self.blocks_multiply_const_vxx_0.set_k(([1.0/(self.M*self.K*0.6863)]*self.M*self.K))

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

    def get_preamble(self):
        return self.preamble

    def set_preamble(self, preamble):
        self.preamble = preamble

    def get_exclude_preamble(self):
        return self.exclude_preamble

    def set_exclude_preamble(self, exclude_preamble):
        self.exclude_preamble = exclude_preamble
        self.blks2_selector_0.set_input_index(int(self.exclude_preamble))
        self.blks2_selector_0_0.set_input_index(int(self.exclude_preamble))

    def get_SNR(self):
        return self.SNR

    def set_SNR(self, SNR):
        self.SNR = SNR
        self._SNR_slider.set_value(self.SNR)
        self._SNR_text_box.set_value(self.SNR)
        self.ofdm_fbmc_channel_hier_cc_0.set_SNR(self.SNR)

    def get_K(self):
        return self.K

    def set_K(self, K):
        self.K = K
        self.blocks_multiply_const_vxx_0.set_k(([1.0/(self.M*self.K*0.6863)]*self.M*self.K))

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
