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
import math
from time import strftime, gmtime, sleep

class OFDMRxGUI(QtGui.QMainWindow):
    """ All of this controls the actual GUI. """
    def __init__(self, options, parent=None):
        QtGui.QMainWindow.__init__(self, parent)

        self.options = options

        # load and uic the file right away, no additional step necessary
        self.gui = uic.loadUi(os.path.join(os.path.dirname(__file__),'ofdm_rx_gui_window.ui'), self)

        # GUI update timer
        self.update_timer = Qt.QTimer()

        # ZeroMQ
        self.probe_manager = zeromq.probe_manager()
        self.probe_manager.add_socket("tcp://"+self.options.rx_hostname+":5555", 'float32', self.plot_snr)
        self.probe_manager.add_socket("tcp://"+self.options.rx_hostname+":5556", 'float32', self.plot_ber)
        if options.measurement:
            self.probe_manager.add_socket("tcp://"+self.options.rx_hostname+":5556", 'float32', self.take_measurement)
        self.probe_manager.add_socket("tcp://"+self.options.rx_hostname+":5557", 'float32', self.plot_freqoffset)
        self.probe_manager.add_socket("tcp://"+self.options.tx_hostname+":4445", 'uint8', self.plot_rate)
        self.probe_manager.add_socket("tcp://"+self.options.rx_hostname+":5559", 'float32', self.plot_csi)
        self.probe_manager.add_socket("tcp://"+self.options.rx_hostname+":5560", 'complex64', self.plot_scatter)
        self.rpc_mgr_tx = zeromq.rpc_manager()
        self.rpc_mgr_tx.set_request_socket("tcp://"+self.options.tx_hostname+":6660")
        self.rpc_mgr_rx = zeromq.rpc_manager()
        self.rpc_mgr_rx.set_request_socket("tcp://"+self.options.rx_hostname+":5550")


        # Window Title
        self.gui.setWindowTitle("Receiver")

        #Plots
        self.gui.qwtPlotSNR.setAxisTitle(Qwt.QwtPlot.yLeft, "SNR[dB]")
        self.gui.qwtPlotSNR.setAxisScale(Qwt.QwtPlot.xBottom, 0, 127)
        self.gui.qwtPlotSNR.enableAxis(Qwt.QwtPlot.xBottom, False)
        self.gui.qwtPlotSNR.setAxisScale(Qwt.QwtPlot.yLeft, 0, 30)
        self.snr_x = range(0,128)
        self.snr_y = [0.0]
        self.curve_snr = Qwt.QwtPlotCurve()
        self.curve_snr.setPen(Qt.QPen(Qt.Qt.red, 1))
        self.curve_snr.setBrush(Qt.Qt.red)
        self.curve_snr.setStyle(Qwt.QwtPlotCurve.Steps)
        self.curve_snr.attach(self.gui.qwtPlotSNR)

        self.gui.qwtPlotBER.setAxisTitle(Qwt.QwtPlot.yLeft, "BER")
        self.gui.qwtPlotBER.setAxisScale(Qwt.QwtPlot.xBottom, 0, 127)
        self.gui.qwtPlotBER.enableAxis(Qwt.QwtPlot.xBottom, False)
        self.gui.qwtPlotBER.setAxisScale(Qwt.QwtPlot.yLeft, 0.0001, 0.5)
        scale_engine = Qwt.QwtLog10ScaleEngine()
        self.gui.qwtPlotBER.setAxisScaleEngine(Qwt.QwtPlot.yLeft, scale_engine)
        self.ber_x = range(0,128)
        self.ber_y = [0.0]
        self.curve_ber = Qwt.QwtPlotCurve()
        self.curve_ber.setBaseline(1e-100)
        self.curve_ber.setPen(Qt.QPen(Qt.Qt.green, 1))
        self.curve_ber.setBrush(Qt.Qt.green)
        self.curve_ber.setStyle(Qwt.QwtPlotCurve.Steps)
        self.curve_ber.attach(self.gui.qwtPlotBER)

        self.gui.qwtPlotFreqoffset.setAxisTitle(Qwt.QwtPlot.yLeft, "Frequency Offset")
        self.gui.qwtPlotFreqoffset.setAxisScale(Qwt.QwtPlot.xBottom, 0, 127)
        self.gui.qwtPlotFreqoffset.enableAxis(Qwt.QwtPlot.xBottom, False)
        self.gui.qwtPlotFreqoffset.setAxisScale(Qwt.QwtPlot.yLeft, -1, 1)
        self.freqoffset_x = range(0,128)
        self.freqoffset_y = [0.0]
        self.curve_freqoffset = Qwt.QwtPlotCurve()
        self.curve_freqoffset.setPen(Qt.QPen(Qt.Qt.black, 1))
        self.curve_freqoffset.attach(self.gui.qwtPlotFreqoffset)

        self.gui.qwtPlotRate.setAxisTitle(Qwt.QwtPlot.yLeft, "Datarate[Mbits/s]")
        self.gui.qwtPlotRate.setAxisScale(Qwt.QwtPlot.xBottom, 0, 127)
        self.gui.qwtPlotRate.enableAxis(Qwt.QwtPlot.xBottom, False)
        self.gui.qwtPlotRate.setAxisScale(Qwt.QwtPlot.yLeft, 0, 10)
        self.rate_x = range(0,128)
        self.rate_y = [0]*len(self.rate_x)
        self.curve_rate = Qwt.QwtPlotCurve()
        self.curve_rate.setPen(Qt.QPen(Qt.Qt.lightGray, 1))
        self.curve_rate.setBrush(Qt.Qt.lightGray)
        self.curve_rate.setStyle(Qwt.QwtPlotCurve.Steps)
        self.curve_rate.attach(self.gui.qwtPlotRate)

        self.gui.qwtPlotCSI.setTitle("Normalized Channel State Information")
        self.gui.qwtPlotCSI.setAxisTitle(Qwt.QwtPlot.xBottom, "Subcarrier")
        self.gui.qwtPlotCSI.setAxisScale(Qwt.QwtPlot.xBottom, -99, 100)
        self.gui.qwtPlotCSI.setAxisScale(Qwt.QwtPlot.yLeft, 0, 2)
        self.csi_x = range(-99,101)
        self.csi_y = [0]*len(self.csi_x)
        self.curve_csi = Qwt.QwtPlotCurve()
        self.curve_csi.setPen(Qt.QPen(Qt.Qt.blue, 1))
        self.curve_csi.setBrush(Qt.Qt.blue)
        self.curve_csi.setStyle(Qwt.QwtPlotCurve.Steps)
        self.curve_csi.attach(self.gui.qwtPlotCSI)

        self.gui.qwtPlotScatter.setTitle("Scatterplot (Subcarrier -99)")
        self.gui.qwtPlotScatter.setAxisTitle(Qwt.QwtPlot.xBottom, "I")
        self.gui.qwtPlotScatter.setAxisTitle(Qwt.QwtPlot.yLeft, "Q")
        self.gui.qwtPlotScatter.setAxisScale(Qwt.QwtPlot.xBottom, -1.5, 1.5)
        self.gui.qwtPlotScatter.setAxisScale(Qwt.QwtPlot.yLeft, -1.5, 1.5)
        self.scatter_buffer = numpy.complex64([0+0j])
        self.curve_scatter = Qwt.QwtPlotCurve()
        self.curve_scatter.setPen(Qt.QPen(Qt.Qt.blue, 1))
        self.curve_scatter.setStyle(Qwt.QwtPlotCurve.Dots)
        self.curve_scatter.attach(self.gui.qwtPlotScatter)
        self.marker = Qwt.QwtSymbol()
        self.marker.setStyle(Qwt.QwtSymbol.XCross)
        self.marker.setSize(Qt.QSize(3,3))
        self.curve_scatter.setSymbol(self.marker)


        # plot picker
        self.plot_picker = Qwt.QwtPlotPicker(Qwt.QwtPlot.xBottom,
                               Qwt.QwtPlot.yLeft,
                               Qwt.QwtPicker.PointSelection,
                               Qwt.QwtPlotPicker.VLineRubberBand,
                               Qwt.QwtPicker.AlwaysOff,
                               self.gui.qwtPlotCSI.canvas())

        #Signals
        self.connect(self.update_timer, QtCore.SIGNAL("timeout()"), self.probe_manager.watcher)
        self.connect(self.gui.pushButtonMeasure, QtCore.SIGNAL("clicked()"),  self.measure_average)
        #self.connect(self.gui.pushButtonUpdate, QtCore.SIGNAL("clicked()"), self.update_modulation)
        self.connect(self.gui.horizontalSliderAmplitude, QtCore.SIGNAL("valueChanged(int)"), self.slide_amplitude)
        self.connect(self.gui.lineEditAmplitude, QtCore.SIGNAL("editingFinished()"), self.edit_amplitude)
        self.connect(self.gui.horizontalSliderOffset, QtCore.SIGNAL("valueChanged(int)"), self.slide_freq_offset)
        self.connect(self.gui.lineEditOffset, QtCore.SIGNAL("editingFinished()"), self.edit_freq_offset)
        self.connect(self.plot_picker, QtCore.SIGNAL("selected(const QwtDoublePoint &)"), self.subcarrier_selected)
        self.connect(self.gui.comboBoxChannelModel, QtCore.SIGNAL("currentIndexChanged(QString)"), self.set_channel_profile)
        self.connect(self.gui.horizontalSliderTxGain, QtCore.SIGNAL("valueChanged(int)"), self.slide_tx_gain)
        self.connect(self.gui.horizontalSliderRxGain, QtCore.SIGNAL("valueChanged(int)"), self.slide_rx_gain)
        self.connect(self.gui.comboBoxScheme, QtCore.SIGNAL("currentIndexChanged(QString)"), self.set_allocation_scheme)
        self.connect(self.gui.horizontalSliderDataRate, QtCore.SIGNAL("valueChanged(int)"), self.slide_data_rate)
        self.connect(self.gui.lineEditDataRate, QtCore.SIGNAL("editingFinished()"), self.edit_data_rate)
        self.connect(self.gui.horizontalSliderGap, QtCore.SIGNAL("valueChanged(int)"), self.slide_target_ber)
        self.connect(self.gui.lineEditGap, QtCore.SIGNAL("editingFinished()"), self.edit_target_ber)
        self.connect(self.gui.horizontalSliderResourceBlockSize, QtCore.SIGNAL("valueChanged(int)"), self.slide_resource_block_size)
        self.connect(self.gui.lineEditResourceBlockSize, QtCore.SIGNAL("editingFinished()"), self.edit_resource_block_size)
        self.connect(self.gui.comboBoxResourceBlocksScheme, QtCore.SIGNAL("currentIndexChanged(QString)"), self.set_resource_block_scheme)
        self.connect(self.gui.comboBoxModulation, QtCore.SIGNAL("currentIndexChanged(QString)"), self.set_modulation_scheme)

        if options.measurement:
            self.rpc_mgr_tx.request("set_amplitude",[0.018])
            self.rpc_mgr_tx.request("set_amplitude_ideal",[0.018])
            self.i = 0
            self.ii = 0
            self.iii = 1
            self.ber=0.0
            self.snr=0.0
            self.snrsum=0.0
            self.datarate=0.0
            self.ratesum=0.0
            self.dirname = "Simulation_"+strftime("%Y_%m_%d_%H_%M_%S",gmtime())+"/"
            print self.dirname
            if not os.path.isdir("./" + self.dirname):
                os.mkdir("./" + self.dirname + "/")
            self.iter_points = 60
            self.snr_points = 30
            amp_min_log = numpy.log10(0.018**2)
            amp_max_log = numpy.log10(0.7**2)
            self.txpow_range = numpy.logspace(amp_min_log,amp_max_log,self.snr_points)
            self.meas_ber = 0.5
            self.change_mod = 1

        # start GUI update timer (33ms for 30 FPS)
        self.update_timer.start(33)

        # get transmitter settings
        self.update_tx_params()

    def update_tx_params(self):
        self.tx_params = self.rpc_mgr_tx.request("get_tx_parameters")
        if self.tx_params != None:
            self.data_subcarriers = self.tx_params.get('data_subcarriers')
            self.frame_length = self.tx_params.get('frame_length')
            self.symbol_time = self.tx_params.get('symbol_time')
        else:
            print "Failed to update TX_params."

    def measure_average(self):
        avg_snr = float(sum(self.snr_y))/len(self.snr_y)
        avg_ber = float(sum(self.ber_y))/len(self.ber_y)
        self.gui.labelSNRAverage.setText(QtCore.QString.number(avg_snr,'f',3))
        self.gui.labelBERAverage.setText(QtCore.QString.number(avg_ber,'e',3))

    def update_modulation(self):
        modulation_str = str(self.gui.comboBoxModulation.currentText())
        bitloading = {'BPSK'    : 1,
                      'QPSK'    : 2,
                      '8-PSK'   : 3,
                      '16-QAM'  : 4,
                      '32-QAM'  : 5,
                      '64-QAM'  : 6,
                      '128-QAM' : 7,
                      '256-QAM' : 8,
                     }[modulation_str]
        self.rpc_mgr_tx.request("set_modulation",[[bitloading]*self.data_subcarriers,[1]*self.data_subcarriers])
        self.update_tx_params()

    def slide_amplitude(self, amplitude):
        # slider should go from 0.001 to 1.0
        displayed_amplitude = pow(10,amplitude/5000.-3)
        self.gui.lineEditAmplitude.setText(QtCore.QString.number(displayed_amplitude,'f',4))
        self.amplitude = amplitude
        self.rpc_mgr_tx.request("set_amplitude",[displayed_amplitude])
        self.rpc_mgr_tx.request("set_amplitude_ideal",[displayed_amplitude])

    def edit_amplitude(self):
        amplitude = self.lineEditAmplitude.text().toFloat()[0]
        amplitude = min(amplitude,1.0)
        amplitude = max(amplitude,1e-6)
        self.gui.lineEditAmplitude.setText(QtCore.QString("%1").arg(amplitude))
        self.amplitude = amplitude
        # block signals to avoid feedback loop
        self.gui.horizontalSliderAmplitude.blockSignals(True)
        # note slider positions are int (!)
        self.gui.horizontalSliderAmplitude.setValue((math.log(amplitude,10)+3)*5000.0)
        self.gui.horizontalSliderAmplitude.blockSignals(False)
        self.rpc_mgr_tx.request("set_amplitude",[self.amplitude])
        self.rpc_mgr_tx.request("set_amplitude_ideal",[self.amplitude])

    def slide_tx_gain(self, gain):
        # note slider positions are int (!)
        tx_gain = gain/1000.0
        self.tx_gain = tx_gain
        gain_db = self.rpc_mgr_tx.request("set_tx_gain",[self.tx_gain])
        if gain_db is not None:
            self.gui.lineEditTxGain.setText(QtCore.QString.number(gain_db))

    def slide_rx_gain(self, gain):
        # note slider positions are int (!)
        rx_gain = gain/1000.0
        self.rx_gain = rx_gain
        gain_db = self.rpc_mgr_rx.request("set_rx_gain",[self.rx_gain])
        if gain_db is not None:
            self.gui.lineEditRxGain.setText(QtCore.QString.number(gain_db))

    def slide_freq_offset(self, offset):
        # note slider positions are int (!)
        freq_offset = offset/100.0
        self.gui.lineEditOffset.setText(QtCore.QString.number(freq_offset,'f',3))
        self.freq_offset = freq_offset
        self.rpc_mgr_tx.request("set_freq_offset",[self.freq_offset])

    def edit_freq_offset(self):
        freq_offset = self.lineEditOffset.text().toFloat()[0]
        freq_offset = min(freq_offset,1.0)
        freq_offset = max(freq_offset,-1.0)
        self.gui.lineEditOffset.setText(QtCore.QString("%1").arg(freq_offset))
        self.freq_offset = freq_offset
        # block signals to avoid feedback loop
        self.gui.horizontalSliderOffset.blockSignals(True)
        # note slider positions are int (!)
        self.gui.horizontalSliderOffset.setValue(freq_offset*100.0)
        self.gui.horizontalSliderOffset.blockSignals(False)
        self.rpc_mgr_tx.request("set_freq_offset",[self.freq_offset])

    def subcarrier_selected(self, point):
        subcarrier = int(point.x())
        titlestring = "Scatterplot (Subcarrier " + str(subcarrier) + ")"
        self.gui.qwtPlotScatter.setTitle(titlestring)
        # Don't send negative subcarrier number!
        self.rpc_mgr_rx.request("set_observed_subcarrier",[subcarrier+100])

    def set_channel_profile(self, profile):
        self.rpc_mgr_tx.request("set_channel_profile",[str(profile)])

    def plot_snr(self, samples):
        self.snr_y = numpy.append(samples,self.snr_y)
        self.snr_y = self.snr_y[:len(self.snr_x)]
        self.curve_snr.setData(self.snr_x, self.snr_y)
        self.gui.qwtPlotSNR.replot()
        self.gui.labelSNREstimate.setText(QtCore.QString.number(self.snr_y[0],'f',3))
        self.snr = samples

    def plot_ber(self, samples):
        # clip samples to some low value
        samples[numpy.where(samples == 0)] = 1e-10
        self.ber_y = numpy.append(samples,self.ber_y)
        self.ber_y = self.ber_y[:len(self.ber_x)]
        self.curve_ber.setData(self.ber_x, self.ber_y)
        self.gui.qwtPlotBER.replot()
        self.gui.labelBEREstimate.setText(QtCore.QString.number(self.ber_y[0],'e',3))

    def take_measurement(self, samples):
        while self.tx_params == None:
            self.update_tx_params()
            return
        if self.iii != 9:
            #print "SET MODULATION"
            if self.change_mod == 1:
                #self.rpc_mgr_tx.request("set_modulation",[[self.iii]*self.data_subcarriers,[1]*self.data_subcarriers])
                #self.rpc_mgr_tx.request("set_allocation_scheme",[0])
                #print "self.ii: ", self.ii
                #self.rpc_mgr_tx.request("set_amplitude",[numpy.sqrt(self.txpow_range[self.ii])])
                print "SET MODULATION: ", self.iii
                self.rpc_mgr_tx.request("set_modulation",[[self.iii]*self.data_subcarriers,[1]*self.data_subcarriers])
                self.update_tx_params()
                self.change_mod = 0
                sleep(1)
            filename_prefix = "M_"+str(int(self.iii))
            if not os.path.isfile("./" + self.dirname+filename_prefix+'_ber.dat'):
                self.testfile = open(self.dirname+filename_prefix+'_ber.dat','w')
            if not os.path.isfile("./" + self.dirname+filename_prefix+'_datarate.dat'):
                self.testfile2 = open(self.dirname+filename_prefix+'_datarate.dat','w')        
            if not ((not self.ii != self.snr_points-1) or (not self.meas_ber > 1e-7 and self.iii<7) ) :
            #if self.ii != self.snr_points:
                #if self.ii==0 and self.i == 0:
                    # self.rpc_mgr_tx.request("set_modulation",[[1]*self.data_subcarriers,[1]*self.data_subcarriers])
                    #self.rpc_mgr_tx.request("set_allocation_scheme",[2])
                    #self.update_tx_params()
                #self.rpc_mgr_tx.request("set_amplitude",[numpy.sqrt(self.txpow_range[self.ii])])
                if self.i != self.iter_points:
                    if self.i>=20:
                        self.ber=self.ber+samples
                        self.snrsum=self.snrsum + self.snr
                        self.ratesum=self.ratesum + self.datarate
                    self.i=self.i+1
                else:
                    self.i=0
                    print "WRITING"
                    self.testfile.write(str(float(self.snrsum/(self.iter_points-20)))+' '+str(float(self.ber/(self.iter_points-20)))+'\n')
                    self.testfile2.write(str(float(self.snrsum/(self.iter_points-20)))+' '+str(float(self.ratesum/(self.iter_points-20)))+'\n')
                    #self.meas_ber_prev = self.meas_ber
                    self.meas_ber = self.ber/(self.iter_points-20)
                    self.ii=self.ii+1
                    #self.rpc_mgr_tx.request("set_power_limit",[10])
                    #self.rpc_mgr_tx.request("set_amplitude",[numpy.sqrt(self.txpow_range[self.ii])])
                    #self.rpc_mgr_tx.request("set_amplitude",[(pow(10,self.ii/10.)*0.01)])
                    self.snrsum=0
                    self.ber=0
                    self.ratesum=0
                    print "self.ii: ", self.ii
                    if not self.ii == self.snr_points:
                        self.rpc_mgr_tx.request("set_amplitude",[numpy.sqrt(self.txpow_range[self.ii])])
                        self.rpc_mgr_tx.request("set_amplitude_ideal",[numpy.sqrt(self.txpow_range[self.ii])])
                    #if self.meas_ber < 1e-7:# and self.ii>4:
                        #self.testfile.close()
                        #self.testfile2.close()
                        #print "self.ii: ", self.ii
                        #print "Modulation: "+str(int(self.iii))+" done!"
                        #self.meas_ber = 0.5
                        ##self.meas_ber_prev = 0.5
                        #self.iii = self.iii + 1
                        #self.i = 0
                        #self.ii = 0
                        #print"hi"
                        #print"self.ii: ", self.ii
            else:
                self.testfile.close()
                self.testfile2.close()
                print "Modulation: "+str(int(self.iii))+" done!"
                self.meas_ber = 0.5
                self.iii = self.iii + 1
                self.change_mod = 1
                self.i = 0
                self.ii = 0
                self.rpc_mgr_tx.request("set_amplitude",[numpy.sqrt(self.txpow_range[self.ii])])
                self.rpc_mgr_tx.request("set_amplitude_ideal",[numpy.sqrt(self.txpow_range[self.ii])])
        else:
            print"done!"

    def plot_freqoffset(self, samples):
        self.freqoffset_y = numpy.append(samples,self.freqoffset_y)
        self.freqoffset_y = self.freqoffset_y[:len(self.freqoffset_x)]
        self.curve_freqoffset.setData(self.freqoffset_x, self.freqoffset_y)
        self.gui.qwtPlotFreqoffset.replot()
        self.gui.labelFreqoffsetEstimate.setText(QtCore.QString.number(self.freqoffset_y[0],'f',3))

    def plot_rate(self, samples):
        if self.tx_params != None:
            rate = sum(samples[:self.data_subcarriers])/self.symbol_time*(self.frame_length-3)/self.frame_length
            self.rate_y = numpy.append(rate,self.rate_y)
            self.rate_y = self.rate_y[:len(self.rate_x)]
            self.curve_rate.setData(self.rate_x, self.rate_y)
            self.gui.qwtPlotRate.replot()
            self.datarate=rate
        else:
            self.update_tx_params()

    def plot_csi(self, samples):
        self.csi_x = range(-99,101)
        self.csi_y = samples
        self.curve_csi.setData(self.csi_x, self.csi_y)
        self.gui.qwtPlotCSI.replot()

    def plot_scatter(self, samples):
        self.scatter_buffer = numpy.append(samples,self.scatter_buffer)
        self.scatter_buffer = self.scatter_buffer[:200]
        self.curve_scatter.setData(self.scatter_buffer.real,self.scatter_buffer.imag)
        self.gui.qwtPlotScatter.replot()

    def set_allocation_scheme(self, scheme_str):
        scheme = {'Uniform'                            : 0,
                  'Rate Adaptive (Bitloading, Power)'  : 1,
                  'Margin Adaptive (Bitloading, Power)': 2,
                  'Rate Adaptive (Bitloading)'         : 3,
                 }[str(scheme_str)]
        if scheme == 0:
            self.rpc_mgr_tx.request("set_modulation",[[1]*self.data_subcarriers,[1]*self.data_subcarriers])
            self.update_tx_params()

        self.rpc_mgr_tx.request("set_allocation_scheme",[scheme])
        self.update_tx_params()

    def slide_data_rate(self, data_rate):
        bit_data_rate = int( ((data_rate/100.)*(self.frame_length)*self.symbol_time/(self.frame_length-3)) )
        self.gui.lineEditDataRate.setText(QtCore.QString("%1").number(data_rate/100.))
        self.rpc_mgr_tx.request("set_data_rate",[bit_data_rate])

    def edit_data_rate(self):
        data_rate = self.lineEditDataRate.text().toFloat()[0]
        bit_data_rate = (data_rate)*(self.frame_length)*self.symbol_time/(self.frame_length-3)
        bit_data_rate = min(data_rate,1600)
        bit_data_rate = max(data_rate,0)
        # bit rate should be integer -> explicit cast
        bit_data_rate = int(bit_data_rate)
        self.gui.lineEditDataRate.setText(QtCore.QString("%1").arg(data_rate))
        # block signals to avoid feedback loop
        self.gui.horizontalSliderDataRate.blockSignals(True)
        # note slider positions are int (!)
        self.gui.horizontalSliderDataRate.setValue(data_rate*100)
        self.gui.horizontalSliderDataRate.blockSignals(False)
        self.rpc_mgr_tx.request("set_data_rate",[bit_data_rate])

    def slide_target_ber(self, target_ber):
        displayed_target_ber = pow(10, target_ber/5000.0-5)
        self.gui.lineEditGap.setText(QtCore.QString.number(displayed_target_ber,'f',4))
        self.target_ber = target_ber
        self.rpc_mgr_tx.request("set_gap",[displayed_target_ber])

    def edit_target_ber(self):
        target_ber = self.lineEditGap.text().toFloat()[0]
        target_ber = max(target_ber,1e-9)
        target_ber = min(target_ber,0.5)
        self.gui.lineEditGap.setText(QtCore.QString("%1").arg(target_ber))
        self.target_ber = target_ber
        # block signals to avoid feedback loop
        self.gui.horizontalSliderGap.blockSignals(True)
        # note slider positions are int (!)
        self.gui.horizontalSliderGap.setValue((math.log(target_ber,10)+5)*5000)
        self.gui.horizontalSliderGap.blockSignals(False)
        self.rpc_mgr_tx.request("set_gap",[self.target_ber])

    def slide_resource_block_size(self, ResourceBlockSize):
        displayed_ResourceBlockSize = ResourceBlockSize
        self.gui.lineEditResourceBlockSize.setText(QtCore.QString("%1").number(ResourceBlockSize))
        self.ResourceBlockSize = ResourceBlockSize
        if self.gui.comboBoxResourceBlocksScheme.currentText() == "Size":
            self.rpc_mgr_tx.request("set_resource_block_size",[ResourceBlockSize])
        else:
            if self.gui.comboBoxResourceBlocksScheme.currentText() == "Number":
                self.rpc_mgr_tx.request("set_resource_block_number",[ResourceBlockSize])
            else:
                print "Error"

    def edit_resource_block_size(self):
        ResourceBlockSize = self.lineEditResourceBlockSize.text().toInt()[0]
        ResourceBlockSize = min(ResourceBlockSize,200)
        ResourceBlockSize = max(ResourceBlockSize, 1)
        self.gui.lineEditResourceBlockSize.setText(QtCore.QString("%1").arg(ResourceBlockSize))
        self.ResourceBlockSize = ResourceBlockSize
        # block signals to avoid feedback loop
        self.gui.horizontalSliderResourceBlockSize.blockSignals(True)
        # note slider positions are int (!)
        self.gui.horizontalSliderResourceBlockSize.setValue(ResourceBlockSize)
        self.gui.horizontalSliderResourceBlockSize.blockSignals(False)
        if self.gui.comboBoxResourceBlocksScheme.currentText() == "Size":
            self.rpc_mgr_tx.request("set_resource_block_size",[ResourceBlockSize])
        else:
            if self.gui.comboBoxResourceBlocksScheme.currentText() == "Number":
                self.rpc_mgr_tx.request("set_resource_block_number",[ResourceBlockSize])
            else:
                print "Error"

    def set_resource_block_scheme(self, scheme):
        if self.gui.comboBoxResourceBlocksScheme.currentText() == "Size":
            self.rpc_mgr_tx.request("set_resource_block_size",[self.lineEditResourceBlockSize.text().toInt()[0]])
        else:
            if self.gui.comboBoxResourceBlocksScheme.currentText() == "Number":
                self.rpc_mgr_tx.request("set_resource_block_number",[self.lineEditResourceBlockSize.text().toInt()[0]])
            else:
                print "Error"

    def set_modulation_scheme(self, scheme):
        bitloading = {'BPSK'    : 1,
                      'QPSK'    : 2,
                      '8-PSK'   : 3,
                      '16-QAM'  : 4,
                      '32-QAM'  : 5,
                      '64-QAM'  : 6,
                      '128-QAM' : 7,
                      '256-QAM' : 8,
                     }[str(scheme)]
        self.rpc_mgr_tx.request("set_modulation",[[bitloading]*self.data_subcarriers,[1]*self.data_subcarriers])
        self.update_tx_params()





def parse_options():
    """ Options parser. """
    parser = OptionParser(option_class=eng_option, usage="%prog: [options]")
    parser.add_option("-t", "--tx-hostname", type="string", default="localhost",
                      help="Transmitter hostname")
    parser.add_option("-r", "--rx-hostname", type="string", default="localhost",
                      help="Transmitter hostname")
    parser.add_option("-m", "--measurement", action="store_true",
                      default=False,
                      help="BER measurement -> set fixed noise power ")
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

