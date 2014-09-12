#!/usr/bin/env python
##################################################
# Gnuradio Python Flow Graph
# Title: Top Block
# Generated: Thu Sep 11 03:26:14 2014
##################################################

from PyQt4 import Qt
from gnuradio import blocks
from gnuradio import eng_notation
from gnuradio import fft
from gnuradio import gr
from gnuradio import qtgui
from gnuradio.eng_option import eng_option
from gnuradio.fft import window
from gnuradio.filter import firdes
from grc_gnuradio import blks2 as grc_blks2
from optparse import OptionParser
import math
import numpy
import ofdm
import sip
import sys

from distutils.version import StrictVersion
class top_block(gr.top_block, Qt.QWidget):

    def __init__(self):
        gr.top_block.__init__(self, "Top Block")
        Qt.QWidget.__init__(self)
        self.setWindowTitle("Top Block")
        try:
             self.setWindowIcon(Qt.QIcon.fromTheme('gnuradio-grc'))
        except:
             pass
        self.top_scroll_layout = Qt.QVBoxLayout()
        self.setLayout(self.top_scroll_layout)
        self.top_scroll = Qt.QScrollArea()
        self.top_scroll.setFrameStyle(Qt.QFrame.NoFrame)
        self.top_scroll_layout.addWidget(self.top_scroll)
        self.top_scroll.setWidgetResizable(True)
        self.top_widget = Qt.QWidget()
        self.top_scroll.setWidget(self.top_widget)
        self.top_layout = Qt.QVBoxLayout(self.top_widget)
        self.top_grid_layout = Qt.QGridLayout()
        self.top_layout.addLayout(self.top_grid_layout)

        self.settings = Qt.QSettings("GNU Radio", "top_block")
        self.restoreGeometry(self.settings.value("geometry").toByteArray())


        ##################################################
        # Variables
        ##################################################
        self.pr_norm = pr_norm = math.sqrt(5)
        self.zero_pads = zero_pads = 1
        self.right_preamble = right_preamble = [-1j/pr_norm, 1/pr_norm, 1j/pr_norm, -1/pr_norm]
        self.left_preamble = left_preamble = [1j/pr_norm, -1/pr_norm, -1j/pr_norm, 1/pr_norm]
        self.center_preamble_0 = center_preamble_0 = [1, -1j, -1, 1j]
        self.center_preamble = center_preamble = [1/pr_norm, -1j/pr_norm, -1/pr_norm, 1j/pr_norm]
        self.M = M = 256
        self.theta_sel = theta_sel = 0
        self.syms_per_frame = syms_per_frame = 20
        self.samp_rate = samp_rate = 3.125e6*2/10
        self.qam_size = qam_size = 4
        self.preamble_0 = preamble_0 = [0]*M*zero_pads+0*left_preamble*((int)(M/len(left_preamble)))+center_preamble_0*((int)(M/len(center_preamble)))+right_preamble*((int)(M/len(right_preamble)))*0+[0]*M*zero_pads
        self.preamble = preamble = [0]*M*zero_pads+0*left_preamble*((int)(M/len(left_preamble)))+3*center_preamble*((int)(M/len(center_preamble)))+right_preamble*((int)(M/len(right_preamble)))*0+[0]*M*zero_pads
        self.exclude_preamble = exclude_preamble = 0
        self.carriers = carriers = M
        self.SNR = SNR = 10
        self.K = K = 4

        ##################################################
        # Blocks
        ##################################################
        self.qtgui_number_sink_0 = qtgui.number_sink(
                gr.sizeof_float,
                0,
                qtgui.NUM_GRAPH_HORIZ,
        	1
        )
        self.qtgui_number_sink_0.set_update_time(0.10)
        self.qtgui_number_sink_0.set_title("")
        
        labels = ["", "", "", "", "",
                  "", "", "", "", ""]
        units = ["", "", "", "", "",
                  "", "", "", "", ""]
        colors = [("black", "black"), ("black", "black"), ("black", "black"), ("black", "black"), ("black", "black"),
                  ("black", "black"), ("black", "black"), ("black", "black"), ("black", "black"), ("black", "black")]
        factor = [1, 1, 1, 1, 1,
                  1, 1, 1, 1, 1]
        for i in xrange(1):
            self.qtgui_number_sink_0.set_min(i, 0)
            self.qtgui_number_sink_0.set_max(i, 1)
            self.qtgui_number_sink_0.set_color(i, colors[i][0], colors[i][1])
            if len(labels[i]) == 0:
                self.qtgui_number_sink_0.set_label(i, "Data {0}".format(i))
            else:
                self.qtgui_number_sink_0.set_label(i, labels[i])
            self.qtgui_number_sink_0.set_unit(i, units[i])
            self.qtgui_number_sink_0.set_factor(i, factor[i])
        
        self.qtgui_number_sink_0.enable_autoscale(False)
        self._qtgui_number_sink_0_win = sip.wrapinstance(self.qtgui_number_sink_0.pyqwidget(), Qt.QWidget)
        self.top_layout.addWidget(self._qtgui_number_sink_0_win)
        self.qtgui_const_sink_x_0 = qtgui.const_sink_c(
        	1024, #size
        	"", #name
        	2 #number of inputs
        )
        self.qtgui_const_sink_x_0.set_update_time(0.10)
        self.qtgui_const_sink_x_0.set_y_axis(-2, 2)
        self.qtgui_const_sink_x_0.set_x_axis(-2, 2)
        self.qtgui_const_sink_x_0.set_trigger_mode(qtgui.TRIG_MODE_FREE, qtgui.TRIG_SLOPE_POS, 0.0, 0, "")
        self.qtgui_const_sink_x_0.enable_autoscale(False)
        self.qtgui_const_sink_x_0.enable_grid(False)
        
        labels = ["", "", "", "", "",
                  "", "", "", "", ""]
        widths = [1, 1, 1, 1, 1,
                  1, 1, 1, 1, 1]
        colors = ["blue", "red", "red", "red", "red",
                  "red", "red", "red", "red", "red"]
        styles = [0, 0, 0, 0, 0,
                  0, 0, 0, 0, 0]
        markers = [0, 0, 0, 0, 0,
                   0, 0, 0, 0, 0]
        alphas = [1.0, 1.0, 1.0, 1.0, 1.0,
                  1.0, 1.0, 1.0, 1.0, 1.0]
        for i in xrange(2):
            if len(labels[i]) == 0:
                self.qtgui_const_sink_x_0.set_line_label(i, "Data {0}".format(i))
            else:
                self.qtgui_const_sink_x_0.set_line_label(i, labels[i])
            self.qtgui_const_sink_x_0.set_line_width(i, widths[i])
            self.qtgui_const_sink_x_0.set_line_color(i, colors[i])
            self.qtgui_const_sink_x_0.set_line_style(i, styles[i])
            self.qtgui_const_sink_x_0.set_line_marker(i, markers[i])
            self.qtgui_const_sink_x_0.set_line_alpha(i, alphas[i])
        
        self._qtgui_const_sink_x_0_win = sip.wrapinstance(self.qtgui_const_sink_x_0.pyqwidget(), Qt.QWidget)
        self.top_layout.addWidget(self._qtgui_const_sink_x_0_win)
        self.ofdm_vector_padding_0 = ofdm.vector_padding(carriers, M,  -1)
        self.ofdm_vector_mask_0 = ofdm.vector_mask(M, (M-carriers)/2, carriers, [])
        self.ofdm_fbmc_symbol_estimation_vcb_0 = ofdm.fbmc_symbol_estimation_vcb(carriers, qam_size)
        self.ofdm_fbmc_symbol_creation_bvc_0 = ofdm.fbmc_symbol_creation_bvc(carriers, qam_size)
        self.ofdm_fbmc_subchannel_processing_vcvc_0 = ofdm.fbmc_subchannel_processing_vcvc(M, syms_per_frame, (preamble_0), 2)
        self.ofdm_fbmc_separate_vcvc_1 = ofdm.fbmc_separate_vcvc(M, 2)
        self.ofdm_fbmc_separate_vcvc_0 = ofdm.fbmc_separate_vcvc(M, 2)
        self.ofdm_fbmc_remove_preamble_vcvc_0 = ofdm.fbmc_remove_preamble_vcvc(M, syms_per_frame, len(preamble_0))
        self.ofdm_fbmc_polyphase_network_vcvc_3 = ofdm.fbmc_polyphase_network_vcvc(M, K, K*M-1, True)
        self.ofdm_fbmc_polyphase_network_vcvc_2 = ofdm.fbmc_polyphase_network_vcvc(M, K, K*M-1, True)
        self.ofdm_fbmc_polyphase_network_vcvc_1 = ofdm.fbmc_polyphase_network_vcvc(M, K, K*M-1, False)
        self.ofdm_fbmc_polyphase_network_vcvc_0 = ofdm.fbmc_polyphase_network_vcvc(M, K, K*M-1, False)
        self.ofdm_fbmc_overlapping_serial_to_parallel_cvc_0 = ofdm.fbmc_overlapping_serial_to_parallel_cvc(M)
        self.ofdm_fbmc_overlapping_parallel_to_serial_vcc_0 = ofdm.fbmc_overlapping_parallel_to_serial_vcc(M)
        self.ofdm_fbmc_oqam_preprocessing_vcvc_0 = ofdm.fbmc_oqam_preprocessing_vcvc(M, 0, 0)
        self.ofdm_fbmc_oqam_postprocessing_vcvc_0 = ofdm.fbmc_oqam_postprocessing_vcvc(M, 0, 0)
        self.ofdm_fbmc_junction_vcvc_0 = ofdm.fbmc_junction_vcvc(M, 2)
        self.ofdm_fbmc_insert_preamble_vcvc_0 = ofdm.fbmc_insert_preamble_vcvc(M, syms_per_frame, preamble_0)
        self.ofdm_fbmc_channel_hier_cc_0_0 = ofdm.fbmc_channel_hier_cc(M, K, syms_per_frame, 0, 2, 0, 1, 201, SNR, exclude_preamble, 1)
        self.ofdm_fbmc_beta_multiplier_vcvc_1 = ofdm.fbmc_beta_multiplier_vcvc(M, K, K*M-1, 0)
        self.ofdm_fbmc_beta_multiplier_vcvc_0 = ofdm.fbmc_beta_multiplier_vcvc(M, K, K*M-1, 0)
        self.fft_vxx_1 = fft.fft_vcc(M, True, ([]), True, 1)
        self.fft_vxx_0 = fft.fft_vcc(M, False, ([]), True, 1)
        self.blocks_vector_to_stream_0_0 = blocks.vector_to_stream(gr.sizeof_gr_complex*1, carriers)
        self.blocks_vector_to_stream_0 = blocks.vector_to_stream(gr.sizeof_gr_complex*1, carriers)
        self.blocks_throttle_0 = blocks.throttle(gr.sizeof_char*1, samp_rate,True)
        self.blocks_skiphead_0_0 = blocks.skiphead(gr.sizeof_gr_complex*M, 1)
        self.blocks_skiphead_0 = blocks.skiphead(gr.sizeof_gr_complex*M, 2*K-1-1)
        self.blocks_multiply_const_vxx_0 = blocks.multiply_const_vcc(([1.0/(M*0.6863)]*M))
        self.blocks_file_sink_1 = blocks.file_sink(gr.sizeof_gr_complex*M, "estimate.dat", False)
        self.blocks_file_sink_1.set_unbuffered(False)
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
        self.analog_random_source_x_0 = blocks.vector_source_b(map(int, numpy.random.randint(0, qam_size, 10000000)), True)

        ##################################################
        # Connections
        ##################################################
        self.connect((self.analog_random_source_x_0, 0), (self.blocks_throttle_0, 0))
        self.connect((self.blocks_throttle_0, 0), (self.ofdm_fbmc_symbol_creation_bvc_0, 0))
        self.connect((self.blocks_throttle_0, 0), (self.blks2_error_rate_0, 0))
        self.connect((self.ofdm_fbmc_separate_vcvc_0, 0), (self.ofdm_fbmc_polyphase_network_vcvc_2, 0))
        self.connect((self.ofdm_fbmc_separate_vcvc_0, 1), (self.ofdm_fbmc_polyphase_network_vcvc_3, 0))
        self.connect((self.ofdm_fbmc_overlapping_serial_to_parallel_cvc_0, 0), (self.ofdm_fbmc_separate_vcvc_0, 0))
        self.connect((self.ofdm_fbmc_polyphase_network_vcvc_2, 0), (self.ofdm_fbmc_junction_vcvc_0, 0))
        self.connect((self.ofdm_fbmc_polyphase_network_vcvc_3, 0), (self.ofdm_fbmc_junction_vcvc_0, 1))
        self.connect((self.ofdm_fbmc_junction_vcvc_0, 0), (self.fft_vxx_1, 0))
        self.connect((self.blocks_skiphead_0, 0), (self.ofdm_fbmc_subchannel_processing_vcvc_0, 0))
        self.connect((self.ofdm_vector_mask_0, 0), (self.ofdm_fbmc_symbol_estimation_vcb_0, 0))
        self.connect((self.ofdm_fbmc_oqam_postprocessing_vcvc_0, 0), (self.ofdm_vector_mask_0, 0))
        self.connect((self.fft_vxx_1, 0), (self.ofdm_fbmc_beta_multiplier_vcvc_1, 0))
        self.connect((self.ofdm_vector_mask_0, 0), (self.blocks_vector_to_stream_0, 0))
        self.connect((self.blks2_error_rate_0, 0), (self.qtgui_number_sink_0, 0))
        self.connect((self.blocks_vector_to_stream_0, 0), (self.qtgui_const_sink_x_0, 0))
        self.connect((self.ofdm_fbmc_beta_multiplier_vcvc_1, 0), (self.blocks_skiphead_0, 0))
        self.connect((self.ofdm_fbmc_symbol_creation_bvc_0, 0), (self.blocks_vector_to_stream_0_0, 0))
        self.connect((self.blocks_vector_to_stream_0_0, 0), (self.qtgui_const_sink_x_0, 1))
        self.connect((self.fft_vxx_0, 0), (self.blocks_multiply_const_vxx_0, 0))
        self.connect((self.ofdm_vector_padding_0, 0), (self.ofdm_fbmc_oqam_preprocessing_vcvc_0, 0))
        self.connect((self.ofdm_fbmc_symbol_creation_bvc_0, 0), (self.ofdm_vector_padding_0, 0))
        self.connect((self.ofdm_fbmc_polyphase_network_vcvc_0, 0), (self.ofdm_fbmc_overlapping_parallel_to_serial_vcc_0, 0))
        self.connect((self.ofdm_fbmc_polyphase_network_vcvc_1, 0), (self.ofdm_fbmc_overlapping_parallel_to_serial_vcc_0, 1))
        self.connect((self.ofdm_fbmc_separate_vcvc_1, 0), (self.ofdm_fbmc_polyphase_network_vcvc_0, 0))
        self.connect((self.ofdm_fbmc_separate_vcvc_1, 1), (self.ofdm_fbmc_polyphase_network_vcvc_1, 0))
        self.connect((self.blks2_selector_0, 0), (self.ofdm_fbmc_beta_multiplier_vcvc_0, 0))
        self.connect((self.ofdm_fbmc_oqam_preprocessing_vcvc_0, 0), (self.blks2_selector_0, 1))
        self.connect((self.ofdm_fbmc_oqam_preprocessing_vcvc_0, 0), (self.ofdm_fbmc_insert_preamble_vcvc_0, 0))
        self.connect((self.ofdm_fbmc_beta_multiplier_vcvc_0, 0), (self.fft_vxx_0, 0))
        self.connect((self.ofdm_fbmc_insert_preamble_vcvc_0, 0), (self.blks2_selector_0, 0))
        self.connect((self.blocks_multiply_const_vxx_0, 0), (self.ofdm_fbmc_separate_vcvc_1, 0))
        self.connect((self.ofdm_fbmc_subchannel_processing_vcvc_0, 0), (self.blocks_skiphead_0_0, 0))
        self.connect((self.blocks_skiphead_0_0, 0), (self.ofdm_fbmc_remove_preamble_vcvc_0, 0))
        self.connect((self.blocks_skiphead_0_0, 0), (self.blks2_selector_0_0, 1))
        self.connect((self.ofdm_fbmc_remove_preamble_vcvc_0, 0), (self.blks2_selector_0_0, 0))
        self.connect((self.blks2_selector_0_0, 0), (self.ofdm_fbmc_oqam_postprocessing_vcvc_0, 0))
        self.connect((self.ofdm_fbmc_channel_hier_cc_0_0, 0), (self.ofdm_fbmc_overlapping_serial_to_parallel_cvc_0, 0))
        self.connect((self.ofdm_fbmc_overlapping_parallel_to_serial_vcc_0, 0), (self.ofdm_fbmc_channel_hier_cc_0_0, 0))
        self.connect((self.ofdm_fbmc_symbol_estimation_vcb_0, 0), (self.blks2_error_rate_0, 1))
        self.connect((self.ofdm_fbmc_subchannel_processing_vcvc_0, 1), (self.blocks_file_sink_1, 0))


    def closeEvent(self, event):
        self.settings = Qt.QSettings("GNU Radio", "top_block")
        self.settings.setValue("geometry", self.saveGeometry())
        event.accept()

    def get_pr_norm(self):
        return self.pr_norm

    def set_pr_norm(self, pr_norm):
        self.pr_norm = pr_norm
        self.set_right_preamble([-1j/self.pr_norm, 1/self.pr_norm, 1j/self.pr_norm, -1/self.pr_norm])
        self.set_left_preamble([1j/self.pr_norm, -1/self.pr_norm, -1j/self.pr_norm, 1/self.pr_norm])
        self.set_center_preamble([1/self.pr_norm, -1j/self.pr_norm, -1/self.pr_norm, 1j/self.pr_norm])

    def get_zero_pads(self):
        return self.zero_pads

    def set_zero_pads(self, zero_pads):
        self.zero_pads = zero_pads
        self.set_preamble([0]*self.M*self.zero_pads+0*self.left_preamble*((int)(self.M/len(self.left_preamble)))+3*self.center_preamble*((int)(self.M/len(self.center_preamble)))+self.right_preamble*((int)(self.M/len(self.right_preamble)))*0+[0]*self.M*self.zero_pads)
        self.set_preamble_0([0]*self.M*self.zero_pads+0*self.left_preamble*((int)(self.M/len(self.left_preamble)))+self.center_preamble_0*((int)(self.M/len(self.center_preamble)))+self.right_preamble*((int)(self.M/len(self.right_preamble)))*0+[0]*self.M*self.zero_pads)

    def get_right_preamble(self):
        return self.right_preamble

    def set_right_preamble(self, right_preamble):
        self.right_preamble = right_preamble
        self.set_preamble([0]*self.M*self.zero_pads+0*self.left_preamble*((int)(self.M/len(self.left_preamble)))+3*self.center_preamble*((int)(self.M/len(self.center_preamble)))+self.right_preamble*((int)(self.M/len(self.right_preamble)))*0+[0]*self.M*self.zero_pads)
        self.set_preamble_0([0]*self.M*self.zero_pads+0*self.left_preamble*((int)(self.M/len(self.left_preamble)))+self.center_preamble_0*((int)(self.M/len(self.center_preamble)))+self.right_preamble*((int)(self.M/len(self.right_preamble)))*0+[0]*self.M*self.zero_pads)

    def get_left_preamble(self):
        return self.left_preamble

    def set_left_preamble(self, left_preamble):
        self.left_preamble = left_preamble
        self.set_preamble([0]*self.M*self.zero_pads+0*self.left_preamble*((int)(self.M/len(self.left_preamble)))+3*self.center_preamble*((int)(self.M/len(self.center_preamble)))+self.right_preamble*((int)(self.M/len(self.right_preamble)))*0+[0]*self.M*self.zero_pads)
        self.set_preamble_0([0]*self.M*self.zero_pads+0*self.left_preamble*((int)(self.M/len(self.left_preamble)))+self.center_preamble_0*((int)(self.M/len(self.center_preamble)))+self.right_preamble*((int)(self.M/len(self.right_preamble)))*0+[0]*self.M*self.zero_pads)

    def get_center_preamble_0(self):
        return self.center_preamble_0

    def set_center_preamble_0(self, center_preamble_0):
        self.center_preamble_0 = center_preamble_0
        self.set_preamble_0([0]*self.M*self.zero_pads+0*self.left_preamble*((int)(self.M/len(self.left_preamble)))+self.center_preamble_0*((int)(self.M/len(self.center_preamble)))+self.right_preamble*((int)(self.M/len(self.right_preamble)))*0+[0]*self.M*self.zero_pads)

    def get_center_preamble(self):
        return self.center_preamble

    def set_center_preamble(self, center_preamble):
        self.center_preamble = center_preamble
        self.set_preamble([0]*self.M*self.zero_pads+0*self.left_preamble*((int)(self.M/len(self.left_preamble)))+3*self.center_preamble*((int)(self.M/len(self.center_preamble)))+self.right_preamble*((int)(self.M/len(self.right_preamble)))*0+[0]*self.M*self.zero_pads)
        self.set_preamble_0([0]*self.M*self.zero_pads+0*self.left_preamble*((int)(self.M/len(self.left_preamble)))+self.center_preamble_0*((int)(self.M/len(self.center_preamble)))+self.right_preamble*((int)(self.M/len(self.right_preamble)))*0+[0]*self.M*self.zero_pads)

    def get_M(self):
        return self.M

    def set_M(self, M):
        self.M = M
        self.set_preamble([0]*self.M*self.zero_pads+0*self.left_preamble*((int)(self.M/len(self.left_preamble)))+3*self.center_preamble*((int)(self.M/len(self.center_preamble)))+self.right_preamble*((int)(self.M/len(self.right_preamble)))*0+[0]*self.M*self.zero_pads)
        self.set_carriers(self.M)
        self.set_preamble_0([0]*self.M*self.zero_pads+0*self.left_preamble*((int)(self.M/len(self.left_preamble)))+self.center_preamble_0*((int)(self.M/len(self.center_preamble)))+self.right_preamble*((int)(self.M/len(self.right_preamble)))*0+[0]*self.M*self.zero_pads)
        self.blocks_multiply_const_vxx_0.set_k(([1.0/(self.M*0.6863)]*self.M))

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

    def get_preamble_0(self):
        return self.preamble_0

    def set_preamble_0(self, preamble_0):
        self.preamble_0 = preamble_0

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

    def get_carriers(self):
        return self.carriers

    def set_carriers(self, carriers):
        self.carriers = carriers

    def get_SNR(self):
        return self.SNR

    def set_SNR(self, SNR):
        self.SNR = SNR
        self.ofdm_fbmc_channel_hier_cc_0_0.set_SNR(self.SNR)

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
    if(StrictVersion(Qt.qVersion()) >= StrictVersion("4.5.0")):
        Qt.QApplication.setGraphicsSystem(gr.prefs().get_string('qtgui','style','raster'))
    qapp = Qt.QApplication(sys.argv)
    tb = top_block()
    tb.start()
    tb.show()
    def quitting():
        tb.stop()
        tb.wait()
    qapp.connect(qapp, Qt.SIGNAL("aboutToQuit()"), quitting)
    qapp.exec_()
    tb = None #to clean up Qt widgets
