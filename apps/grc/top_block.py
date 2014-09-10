#!/usr/bin/env python
##################################################
# Gnuradio Python Flow Graph
# Title: Top Block
# Generated: Wed Sep 10 18:01:54 2014
##################################################

from PyQt4 import Qt
from gnuradio import blocks
from gnuradio import eng_notation
from gnuradio import gr
from gnuradio import qtgui
from gnuradio.eng_option import eng_option
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
        self.M = M = 256
        self.theta_sel = theta_sel = 0
        self.syms_per_frame = syms_per_frame = 10
        self.samp_rate = samp_rate = 3.125e6/10
        self.qam_size = qam_size = 16
        self.exclude_preamble = exclude_preamble = 1
        self.center_preamble = center_preamble = [1, -1j, -1, 1j]
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
            self.qtgui_number_sink_0.set_min(i, -1)
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
        self.ofdm_fbmc_transmitter_hier_bc_0 = ofdm.fbmc_transmitter_hier_bc(M, K, qam_size, syms_per_frame, carriers, theta_sel, exclude_preamble, center_preamble, 1)
        self.ofdm_fbmc_receiver_hier_cb_0 = ofdm.fbmc_receiver_hier_cb(M, K, qam_size, syms_per_frame, carriers, theta_sel, 2, exclude_preamble, center_preamble, 1)
        self.ofdm_fbmc_channel_hier_cc_0 = ofdm.fbmc_channel_hier_cc(M, K, syms_per_frame, 1, 0, 0, 1, 201, SNR, exclude_preamble, 1)
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
        self.connect((self.analog_random_source_x_0, 0), (self.blocks_throttle_0, 0))
        self.connect((self.blocks_throttle_0, 0), (self.ofdm_fbmc_transmitter_hier_bc_0, 0))
        self.connect((self.ofdm_fbmc_channel_hier_cc_0, 0), (self.ofdm_fbmc_receiver_hier_cb_0, 0))
        self.connect((self.ofdm_fbmc_receiver_hier_cb_0, 0), (self.blks2_error_rate_0, 1))
        self.connect((self.blocks_throttle_0, 0), (self.blks2_error_rate_0, 0))
        self.connect((self.ofdm_fbmc_transmitter_hier_bc_0, 0), (self.ofdm_fbmc_channel_hier_cc_0, 0))
        self.connect((self.blks2_error_rate_0, 0), (self.qtgui_number_sink_0, 0))


    def closeEvent(self, event):
        self.settings = Qt.QSettings("GNU Radio", "top_block")
        self.settings.setValue("geometry", self.saveGeometry())
        event.accept()

    def get_M(self):
        return self.M

    def set_M(self, M):
        self.M = M
        self.set_carriers(self.M)

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
