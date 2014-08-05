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

from PyQt4 import QtCore, QtGui, uic
import PyQt4.Qt as Qt
import PyQt4.Qwt5 as Qwt
from gnuradio import eng_notation
from gnuradio import gr
from gnuradio import zeromq
from gnuradio.eng_option import eng_option
from optparse import OptionParser
import sys
import os
import signal
import numpy


class OFDMRxGUI(QtGui.QMainWindow):
    """ All of this controls the actual GUI. """
    def __init__(self, options, parent=None):
        QtGui.QMainWindow.__init__(self, parent)

        self.options = options

        # load and uic the file right away, no additional step necessary
        self.gui = uic.loadUi(os.path.join(os.path.dirname(__file__),'ofdm_tx_gui_window.ui'), self)

        # GUI update timer
        self.plot_timer = Qt.QTimer()

        # ZeroMQ
        self.probe_manager = zeromq.probe_manager()
        self.probe_manager.add_socket("tcp://"+self.options.tx_hostname+":4444", 'f', self.plot_powerallocation)
        self.probe_manager.add_socket("tcp://"+self.options.tx_hostname+":4445", 'B', self.plot_bitloading)
        self.rpc_mgr_tx = zeromq.rpc_manager()
        self.rpc_mgr_tx.set_request_socket("tcp://"+self.options.tx_hostname+":6660")


        # Window Title
        self.gui.setWindowTitle("Transmitter")

        #Plots
        self.gui.qwtPlotPowerallocation.setTitle("Subcarrier Powerallocation")
        self.gui.qwtPlotPowerallocation.setAxisTitle(Qwt.QwtPlot.xBottom, "Subcarrier Index")
        self.gui.qwtPlotPowerallocation.setAxisScale(Qwt.QwtPlot.xBottom, -99, 100)
        self.gui.qwtPlotPowerallocation.setAxisScale(Qwt.QwtPlot.yLeft, 0, 3)
        self.powerallocation_x = range(-99,101)
        self.powerallocation_y = [0]*len(self.powerallocation_x)
        self.curve_powerallocation = Qwt.QwtPlotCurve()
        self.curve_powerallocation.setPen(Qt.QPen(Qt.Qt.green, 1))
        self.curve_powerallocation.setBrush(Qt.Qt.green)
        self.curve_powerallocation.setStyle(Qwt.QwtPlotCurve.Steps)
        self.curve_powerallocation.attach(self.gui.qwtPlotPowerallocation)

        self.gui.qwtPlotBitloading.setTitle("Subcarrier Bitloading")
        self.gui.qwtPlotBitloading.setAxisTitle(Qwt.QwtPlot.xBottom, "Subcarrier Index")
        self.gui.qwtPlotBitloading.setAxisScale(Qwt.QwtPlot.xBottom, -99, 100)
        self.gui.qwtPlotBitloading.setAxisScale(Qwt.QwtPlot.yLeft, 0, 8)
        self.bitloading_x = range(-99,101)
        self.bitloading_y = [0]*len(self.bitloading_x)
        self.curve_bitloading = Qwt.QwtPlotCurve()
        self.curve_bitloading.setPen(Qt.QPen(Qt.Qt.magenta, 1))
        self.curve_bitloading.setBrush(Qt.Qt.magenta)
        self.curve_bitloading.setStyle(Qwt.QwtPlotCurve.Steps)
        self.curve_bitloading.attach(self.gui.qwtPlotBitloading)

        #Signals
        self.connect(self.plot_timer, QtCore.SIGNAL("timeout()"), self.probe_manager.watcher)
        self.connect(self.gui.pushButtonUpdate, QtCore.SIGNAL("clicked()"), self.update_tx_parameters)

        # start GUI update timer
        self.plot_timer.start(100)


    def plot_powerallocation(self, samples):
        self.powerallocation_x = range(-99,101)
        self.powerallocation_y = samples
        self.curve_powerallocation.setData(self.powerallocation_x, self.powerallocation_y)
        self.gui.qwtPlotPowerallocation.replot()

    def plot_bitloading(self, samples):
        self.bitloading_x = range(-99,101)
        self.bitloading_y = samples
        self.curve_bitloading.setData(self.bitloading_x, self.bitloading_y)
        self.gui.qwtPlotBitloading.replot()

    def update_tx_parameters(self):
        self.tx_params = self.rpc_mgr_tx.request("get_tx_parameters")
        if self.tx_params:
            self.gui.labelCarrierFrequency.setText(QtCore.QString("%1").arg(self.tx_params.get('carrier_frequency')))
            self.gui.labelFFTSize.setText(QtCore.QString("%1").arg(int(self.tx_params.get('fft_size'))))
            self.gui.labelCPSize.setText(QtCore.QString("%1").arg(int(self.tx_params.get('cp_size'))))
            self.gui.labelSubcarrierSpacing.setText(QtCore.QString("%1").arg(self.tx_params.get('subcarrier_spacing')))
            self.gui.labelDataSubcarriers.setText(QtCore.QString("%1").arg(int(self.tx_params.get('data_subcarriers'))))
            self.gui.labelBandwidth.setText(QtCore.QString("%1").arg(self.tx_params.get('bandwidth')))
            self.gui.labelFrameLength.setText(QtCore.QString("%1").arg(int(self.tx_params.get('frame_length'))))
            self.gui.labelSymbolTime.setText(QtCore.QString("%1").arg(self.tx_params.get('symbol_time')))
            self.gui.labelMaxDataRate.setText(QtCore.QString("%1").arg(self.tx_params.get('max_data_rate')))


def parse_options():
    """ Options parser. """
    parser = OptionParser(option_class=eng_option, usage="%prog: [options]")
    parser.add_option("-t", "--tx-hostname", type="string", default="localhost",
                      help="Transmitter hostname")
    (options, args) = parser.parse_args()
    return options

if __name__ == '__main__':
    # parse options
    options = parse_options()
    # give ctrl+c back to system
    signal.signal(signal.SIGINT, signal.SIG_DFL)
    # start the Qt app
    qapp = Qt.QApplication(sys.argv)
    qapp.main_box = OFDMRxGUI(options)
    qapp.main_box.show()
    qapp.exec_()

