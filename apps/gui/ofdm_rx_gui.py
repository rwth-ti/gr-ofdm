#!/usr/bin/env python
##################################################
# PyQt GUI
# Title: OFDM RX GUI
# Generated: Thu Jan 31 14:16:08 2013
##################################################

from PyQt4 import QtCore, QtGui, uic
import PyQt4.Qt as Qt
import PyQt4.Qwt5 as Qwt
from gnuradio import eng_notation
from gnuradio import gr
from gnuradio.eng_option import eng_option
from optparse import OptionParser
import sys
import os
import signal
import numpy
import zmqblocks

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
        self.probe_manager = zmqblocks.probe_manager()
        self.probe_manager.add_socket("tcp://"+self.options.rxhostname+":5555", 'float32', self.plot_snr)
        self.probe_manager.add_socket("tcp://"+self.options.rxhostname+":5556", 'float32', self.plot_ber)
        self.probe_manager.add_socket("tcp://"+self.options.rxhostname+":5557", 'float32', self.plot_freqoffset)
        self.probe_manager.add_socket("tcp://"+self.options.txhostname+":4445", 'uint8', self.plot_rate)
        self.probe_manager.add_socket("tcp://"+self.options.rxhostname+":5559", 'float32', self.plot_csi)
        self.probe_manager.add_socket("tcp://"+self.options.rxhostname+":5560", 'complex64', self.plot_scatter)
        self.rpc_manager = zmqblocks.rpc_manager()
        self.rpc_manager.set_request_socket("tcp://"+self.options.txhostname+":6666")

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

        self.gui.qwtPlotScatter.setTitle("Scatterplot")
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
        self.connect(self.gui.pushButtonUpdate, QtCore.SIGNAL("clicked()"), self.update_modulation)
        self.connect(self.gui.horizontalSliderAmplitude, QtCore.SIGNAL("valueChanged(int)"), self.slide_amplitude)
        self.connect(self.gui.lineEditAmplitude, QtCore.SIGNAL("editingFinished()"), self.edit_amplitude)
        self.connect(self.gui.horizontalSliderOffset, QtCore.SIGNAL("valueChanged(int)"), self.slide_freq_offset)
        self.connect(self.gui.lineEditOffset, QtCore.SIGNAL("editingFinished()"), self.edit_freq_offset)
        self.connect(self.plot_picker, QtCore.SIGNAL("selected(const QwtDoublePoint &)"), self.subcarrier_selected)
        self.connect(self.gui.comboBoxChannelModel, QtCore.SIGNAL("currentIndexChanged(QString)"), self.set_channel_profile)

        # start GUI update timer
        self.update_timer.start(33)

        # get transmitter settings
        self.tx_params = self.rpc_manager.request("get_tx_parameters")

    def measure_average(self):
        avg_snr = float(sum(self.snr_y))/len(self.snr_y)
        avg_ber = float(sum(self.ber_y))/len(self.ber_y)
        self.gui.labelSNRAverage.setText(QtCore.QString.number(avg_snr,'f',3))
        self.gui.labelBERAverage.setText(QtCore.QString.number(avg_ber,'e',3))

    def update_modulation(self):
        modulation_str = str(self.gui.comboBoxModulation.currentText())
        self.rpc_manager.request("set_modulation",modulation_str)

    def slide_amplitude(self, amplitude):
        self.gui.lineEditAmplitude.setText(QtCore.QString("%1").arg(amplitude))
        self.amplitude = amplitude
        self.rpc_manager.request("set_amplitude",self.amplitude)

    def edit_amplitude(self):
        amplitude = self.lineEditAmplitude.text().toInt()[0]
        amplitude = min(amplitude,10000)
        amplitude = max(amplitude,0)
        self.gui.lineEditAmplitude.setText(QtCore.QString("%1").arg(amplitude))
        # block signals to avoid feedback loop
        self.gui.horizontalSliderAmplitude.blockSignals(True)
        self.gui.horizontalSliderAmplitude.setValue(amplitude)
        self.gui.horizontalSliderAmplitude.blockSignals(False)
        self.amplitude = amplitude
        self.rpc_manager.request("set_amplitude",self.amplitude)

    def slide_freq_offset(self, offset):
        # note slider positions are int (!)
        freq_offset = offset/100.0
        self.gui.lineEditOffset.setText(QtCore.QString.number(freq_offset,'f',3))
        self.freq_offset = freq_offset
        self.rpc_manager.request("set_freq_offset",self.freq_offset)

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
        self.rpc_manager.request("set_freq_offset",self.freq_offset)

    def subcarrier_selected(self, point):
        subcarrier = int(point.x()+99)
        titlestring = "Scatterplot (Subcarrier " + str(subcarrier) + ")"
        self.gui.qwtPlotScatter.setTitle(titlestring)
        self.rpc_manager.request("set_scatter_subcarrier",subcarrier)

    def set_channel_profile(self, profile):
        self.rpc_manager.request("set_channel_profile",str(profile))

    def plot_snr(self, samples):
        self.snr_y = numpy.append(samples,self.snr_y)
        self.snr_y = self.snr_y[:len(self.snr_x)]
        self.curve_snr.setData(self.snr_x, self.snr_y)
        self.gui.qwtPlotSNR.replot()
        self.gui.labelSNREstimate.setText(QtCore.QString.number(self.snr_y[0],'f',3))

    def plot_ber(self, samples):
        # clip samples to some low value
        samples[numpy.where(samples == 0)] = 1e-100
        self.ber_y = numpy.append(samples,self.ber_y)
        self.ber_y = self.ber_y[:len(self.ber_x)]
        self.curve_ber.setData(self.ber_x, self.ber_y)
        self.gui.qwtPlotBER.replot()
        self.gui.labelBEREstimate.setText(QtCore.QString.number(self.ber_y[0],'e',3))

    def plot_freqoffset(self, samples):
        self.freqoffset_y = numpy.append(samples,self.freqoffset_y)
        self.freqoffset_y = self.freqoffset_y[:len(self.freqoffset_x)]
        self.curve_freqoffset.setData(self.freqoffset_x, self.freqoffset_y)
        self.gui.qwtPlotFreqoffset.replot()
        self.gui.labelFreqoffsetEstimate.setText(QtCore.QString.number(self.freqoffset_y[0],'f',3))

    def plot_rate(self, samples):
        if self.tx_params:
            self.data_subcarriers = self.tx_params.get('data_subcarriers')
            self.frame_length = self.tx_params.get('frame_length')
            self.symbol_time = self.tx_params.get('symbol_time')
        else:
            self.tx_params = self.rpc_manager.request("get_tx_parameters")
        rate = sum(samples[:self.data_subcarriers])/self.symbol_time*(self.frame_length-3)/self.frame_length
        self.rate_y = numpy.append(rate,self.rate_y)
        self.rate_y = self.rate_y[:len(self.rate_x)]
        self.curve_rate.setData(self.rate_x, self.rate_y)
        self.gui.qwtPlotRate.replot()

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


def parse_options():
    """ Options parser. """
    parser = OptionParser(option_class=eng_option, usage="%prog: [options]")
    parser.add_option("-t", "--txhostname", type="string", default="localhost",
                      help="Transmitter hostname")
    parser.add_option("-r", "--rxhostname", type="string", default="localhost",
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

