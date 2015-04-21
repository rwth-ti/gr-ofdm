#!/usr/bin/env python
##################################################
# Gnuradio Python Flow Graph
# Title: Top Block
# Generated: Tue Apr 21 12:24:16 2015
##################################################

execfile("/home/zivkovic/.grc_gnuradio/tigr_ber_measurement.py")
execfile("/home/zivkovic/.grc_gnuradio/tigr_fbmc_inner_receiver.py")
execfile("/home/zivkovic/.grc_gnuradio/tigr_fbmc_snr_estimator.py")
execfile("/home/zivkovic/.grc_gnuradio/tigr_scatterplot.py")
execfile("/home/zivkovic/.grc_gnuradio/tigr_transmit_control.py")
from PyQt4 import Qt
from PyQt4.QtCore import QObject, pyqtSlot
from gnuradio import blocks
from gnuradio import channels
from gnuradio import eng_notation
from gnuradio import fft
from gnuradio import filter
from gnuradio import gr
from gnuradio import trellis
from gnuradio import zeromq
from gnuradio.eng_option import eng_option
from gnuradio.fft import window
from gnuradio.filter import firdes
from grc_gnuradio import blks2 as grc_blks2
from ofdm.fbmc_frame_sampler_grc import fbmc_frame_sampler
from ofdm.fbmc_rms_amplifier_grc import fbmc_rms_amplifier
from ofdm.preambles_grc import default_block_header
from ofdm.preambles_grc import fbmc_pilot_block_filter
from ofdm.preambles_grc import fbmc_pilot_block_inserter
from ofdm.rx_rpc_manager_grc import rx_rpc_manager
from ofdm.tx_rpc_manager_grc import tx_rpc_manager
from optparse import OptionParser
from random import seed,randint, getrandbits
import PyQt4.Qwt5 as Qwt
import math, numpy, copy
import ofdm
import sys
import threading
import time

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
        self.used_id_bits = used_id_bits = 8
        self.subcarriers = subcarriers = 208
        self.id_blocks = id_blocks = 1
        self.fft_length = fft_length = 256
        self.fbmc = fbmc = 1
        self.estimation_preamble = estimation_preamble = 0
        self.data_blocks = data_blocks = 10
        self.training_data = training_data = default_block_header(subcarriers,fft_length,fbmc,estimation_preamble,[])
        self.repeated_id_bits = repeated_id_bits = subcarriers/used_id_bits
        self.data_part = data_part = data_blocks + id_blocks
        self.whitener_seed = whitener_seed = seed(1)
        self.whitener_pn = whitener_pn = [randint(0,1) for i in range(used_id_bits*repeated_id_bits)]
        self.variable_function_probe_2 = variable_function_probe_2 = 0
        self.variable_function_probe_1 = variable_function_probe_1 = 0
        self.variable_function_probe_0 = variable_function_probe_0 = 0
        self.tx_hostname = tx_hostname = "neat"
        self.samp_rate = samp_rate = 4*250000
        self.interleaver = interleaver = trellis.interleaver(2000,666)
        self.frame_length = frame_length = 2*data_part + training_data.fbmc_no_preambles
        self.filter_length = filter_length = 4
        self.disable_freq_sync = disable_freq_sync = 1
        self.coding = coding = 1
        self.chunkdivisor = chunkdivisor = int(numpy.ceil(data_blocks/5.0))
        self.ber_window = ber_window = 100000
        self.amplitude = amplitude = 1
        self.SNR = SNR = -2

        ##################################################
        # Blocks
        ##################################################
        self._amplitude_layout = Qt.QVBoxLayout()
        self._amplitude_tool_bar = Qt.QToolBar(self)
        self._amplitude_layout.addWidget(self._amplitude_tool_bar)
        self._amplitude_tool_bar.addWidget(Qt.QLabel("amplitude"+": "))
        class qwt_counter_pyslot(Qwt.QwtCounter):
            def __init__(self, parent=None):
                Qwt.QwtCounter.__init__(self, parent)
            @pyqtSlot('double')
            def setValue(self, value):
                super(Qwt.QwtCounter, self).setValue(value)
        self._amplitude_counter = qwt_counter_pyslot()
        self._amplitude_counter.setRange(0, 1, 0.02)
        self._amplitude_counter.setNumButtons(2)
        self._amplitude_counter.setValue(self.amplitude)
        self._amplitude_tool_bar.addWidget(self._amplitude_counter)
        self._amplitude_counter.valueChanged.connect(self.set_amplitude)
        self._amplitude_slider = Qwt.QwtSlider(None, Qt.Qt.Horizontal, Qwt.QwtSlider.BottomScale, Qwt.QwtSlider.BgSlot)
        self._amplitude_slider.setRange(0, 1, 0.02)
        self._amplitude_slider.setValue(self.amplitude)
        self._amplitude_slider.setMinimumWidth(200)
        self._amplitude_slider.valueChanged.connect(self.set_amplitude)
        self._amplitude_layout.addWidget(self._amplitude_slider)
        self.top_layout.addLayout(self._amplitude_layout)
        self.tx_rpc_manager_0 = tx_rpc_manager(fft_length, subcarriers, data_blocks, frame_length, 0, 0.0, samp_rate)
        self.tigr_transmit_control_0 = tigr_transmit_control(
            subcarriers=subcarriers,
            fft_length=fft_length,
            used_id_bits=used_id_bits,
            estimation_preamble=estimation_preamble,
            filter_length=filter_length,
            fbmc=fbmc,
            data_blocks=data_blocks,
            data_part=data_part,
            coding=coding,
            repeated_id_bits=repeated_id_bits,
        )
        self.tigr_scatterplot_0 = tigr_scatterplot(
            subcarriers=subcarriers,
            fbmc=fbmc,
            fft_length=fft_length,
            estimation_preamble=estimation_preamble,
            data_blocks=data_blocks,
            data_part=11,
            frame_length=frame_length,
        )
        self.rx_rpc_manager_0 = rx_rpc_manager()
        self.rms = fbmc_rms_amplifier(amplitude, subcarriers)
        self.zeromq_pub_sink_1 = zeromq.pub_sink(gr.sizeof_float, subcarriers, "tcp://*:5559", 100)
        self.zeromq_pub_sink_0 = zeromq.pub_sink(gr.sizeof_float, 1, "tcp://*:5557", 100)
        def _variable_function_probe_2_probe():
            while True:
                val = self.rx_rpc_manager_0.add_set_scatter_subcarrier_interface(self.tigr_scatterplot_0.ofdm_vector_element_0.set_element)
                try:
                    self.set_variable_function_probe_2(val)
                except AttributeError:
                    pass
                time.sleep(1.0 / (0.000000001))
        _variable_function_probe_2_thread = threading.Thread(target=_variable_function_probe_2_probe)
        _variable_function_probe_2_thread.daemon = True
        _variable_function_probe_2_thread.start()
        def _variable_function_probe_1_probe():
            while True:
                val = self.tx_rpc_manager_0.add_tx_modulation_interface(self.tigr_transmit_control_0.ofdm_allocation_src_0.set_allocation)
                try:
                    self.set_variable_function_probe_1(val)
                except AttributeError:
                    pass
                time.sleep(1.0 / (0.000000001))
        _variable_function_probe_1_thread = threading.Thread(target=_variable_function_probe_1_probe)
        _variable_function_probe_1_thread.daemon = True
        _variable_function_probe_1_thread.start()
        def _variable_function_probe_0_probe():
            while True:
                val = self.tx_rpc_manager_0.add_tx_ampl_interface(self.rms.set_rms_amplitude)
                try:
                    self.set_variable_function_probe_0(val)
                except AttributeError:
                    pass
                time.sleep(1.0 / (0.000000001))
        _variable_function_probe_0_thread = threading.Thread(target=_variable_function_probe_0_probe)
        _variable_function_probe_0_thread.daemon = True
        _variable_function_probe_0_thread.start()
        self.trellis_permutation_0 = trellis.permutation(interleaver.K(), (interleaver.DEINTER()), 1, gr.sizeof_float*1)
        self.tigr_fbmc_snr_estimator_0 = tigr_fbmc_snr_estimator(
            subcarriers=subcarriers,
            fbmc=fbmc,
            fft_length=fft_length,
            estimation_preamble=estimation_preamble,
            frame_length=frame_length,
        )
        self.tigr_fbmc_inner_receiver_0 = tigr_fbmc_inner_receiver(
            subcarriers=subcarriers,
            fft_length=fft_length,
            data_blocks=data_blocks,
            estimation_preamble=estimation_preamble,
            filter_length=filter_length,
            frame_length=frame_length,
            disable_freq_sync=disable_freq_sync,
        )
        self.tigr_ber_measurement_0 = tigr_ber_measurement(
            subcarriers=subcarriers,
            fbmc=fbmc,
            fft_length=fft_length,
            estimation_preamble=estimation_preamble,
            ber_window=ber_window,
            data_blocks=data_blocks,
        )
        self.single_pole_iir_filter_xx_0 = filter.single_pole_iir_filter_ff(0.1, subcarriers)
        self.ofdm_viterbi_combined_fb_0 = ofdm.viterbi_combined_fb(ofdm.fsm(ofdm.fsm(1,2,[91,121])), subcarriers, -1, -1, 2, chunkdivisor, ([-1,-1,-1,1,1,-1,1,1]), ofdm.TRELLIS_EUCLIDEAN)
        self.ofdm_vector_sampler_0 = ofdm.vector_sampler(gr.sizeof_gr_complex*subcarriers, 1)
        self.ofdm_vector_padding_0 = ofdm.vector_padding(subcarriers, fft_length,  -1)
        self.ofdm_multiply_const_ii_0 = ofdm.multiply_const_ii(1./int(numpy.ceil(data_blocks/5.0)))
        self.ofdm_generic_softdemapper_vcf_0 = ofdm.generic_softdemapper_vcf(subcarriers, data_part, 1)
        self.ofdm_fbmc_separate_vcvc_1 = ofdm.fbmc_separate_vcvc(fft_length, 2)
        self.ofdm_fbmc_polyphase_network_vcvc_1 = ofdm.fbmc_polyphase_network_vcvc(fft_length, filter_length, filter_length*fft_length-1, False)
        self.ofdm_fbmc_polyphase_network_vcvc_0 = ofdm.fbmc_polyphase_network_vcvc(fft_length, filter_length, filter_length*fft_length-1, False)
        self.ofdm_fbmc_pilot_block_inserter_0 = fbmc_pilot_block_inserter(subcarriers, data_part, training_data, 5)
        self.ofdm_fbmc_pilot_block_filter_0 = fbmc_pilot_block_filter(subcarriers, frame_length, data_part, training_data)
        self.ofdm_fbmc_overlapping_parallel_to_serial_vcc_0 = ofdm.fbmc_overlapping_parallel_to_serial_vcc(fft_length)
        self.ofdm_fbmc_oqam_preprocessing_vcvc_0 = ofdm.fbmc_oqam_preprocessing_vcvc(subcarriers, 0, 0)
        self.ofdm_fbmc_frame_sampler_0 = fbmc_frame_sampler(subcarriers, frame_length, data_part, training_data)
        self.ofdm_fbmc_beta_multiplier_vcvc_0 = ofdm.fbmc_beta_multiplier_vcvc(fft_length, filter_length, fft_length*fft_length-1, 0)
        self.ofdm_dynamic_trigger_ib_0 = ofdm.dynamic_trigger_ib(0)
        self.ofdm_divide_frame_fc_0 = ofdm.divide_frame_fc(data_part, subcarriers)
        self.ofdm_depuncture_ff_0 = ofdm.depuncture_ff(subcarriers, 0)
        self.ofdm_coded_bpsk_soft_decoder_0 = ofdm.coded_bpsk_soft_decoder(subcarriers, used_id_bits, (whitener_pn))
        self.ofdm_allocation_buffer_0 = ofdm.allocation_buffer(subcarriers, data_blocks, "tcp://"+tx_hostname+":3333", 1)
        self.fft_vxx_1 = fft.fft_vcc(fft_length, False, ([]), True, 1)
        self.channels_channel_model_0 = channels.channel_model(
            noise_voltage=math.sqrt(1.0*fft_length/subcarriers)*math.sqrt(0.5)*10**(-SNR/20.0),
            frequency_offset=0.0,
            epsilon=1,
            taps=((1.0 ), ),
            noise_seed=0,
            block_tags=False
        )
        self.blocks_vector_source_x_0 = blocks.vector_source_b([1] + [0]*(data_blocks/2-1), True, 1, [])
        self.blocks_throttle_0 = blocks.throttle(gr.sizeof_gr_complex*1, samp_rate,True)
        self.blocks_keep_one_in_n_1 = blocks.keep_one_in_n(gr.sizeof_float*subcarriers, 20)
        self.blks2_selector_0 = grc_blks2.selector(
            item_size=gr.sizeof_float*1,
            num_inputs=2,
            num_outputs=1,
            input_index=0,
            output_index=0,
        )

        ##################################################
        # Connections
        ##################################################
        self.connect((self.ofdm_fbmc_polyphase_network_vcvc_0, 0), (self.ofdm_fbmc_overlapping_parallel_to_serial_vcc_0, 0))
        self.connect((self.ofdm_fbmc_polyphase_network_vcvc_1, 0), (self.ofdm_fbmc_overlapping_parallel_to_serial_vcc_0, 1))
        self.connect((self.ofdm_fbmc_separate_vcvc_1, 1), (self.ofdm_fbmc_polyphase_network_vcvc_1, 0))
        self.connect((self.ofdm_fbmc_oqam_preprocessing_vcvc_0, 0), (self.ofdm_fbmc_pilot_block_inserter_0, 0))
        self.connect((self.ofdm_fbmc_pilot_block_inserter_0, 0), (self.ofdm_vector_padding_0, 0))
        self.connect((self.ofdm_fbmc_beta_multiplier_vcvc_0, 0), (self.fft_vxx_1, 0))
        self.connect((self.fft_vxx_1, 0), (self.ofdm_fbmc_separate_vcvc_1, 0))
        self.connect((self.tigr_transmit_control_0, 0), (self.ofdm_fbmc_oqam_preprocessing_vcvc_0, 0))
        self.connect((self.single_pole_iir_filter_xx_0, 0), (self.blocks_keep_one_in_n_1, 0))
        self.connect((self.ofdm_fbmc_frame_sampler_0, 1), (self.ofdm_fbmc_pilot_block_filter_0, 1))
        self.connect((self.ofdm_fbmc_frame_sampler_0, 0), (self.ofdm_fbmc_pilot_block_filter_0, 0))
        self.connect((self.ofdm_divide_frame_fc_0, 0), (self.tigr_scatterplot_0, 0))
        self.connect((self.ofdm_fbmc_pilot_block_filter_0, 1), (self.ofdm_vector_sampler_0, 1))
        self.connect((self.ofdm_vector_sampler_0, 0), (self.ofdm_coded_bpsk_soft_decoder_0, 0))
        self.connect((self.ofdm_coded_bpsk_soft_decoder_0, 0), (self.ofdm_allocation_buffer_0, 0))
        self.connect((self.ofdm_allocation_buffer_0, 2), (self.ofdm_divide_frame_fc_0, 1))
        self.connect((self.ofdm_divide_frame_fc_0, 0), (self.ofdm_generic_softdemapper_vcf_0, 0))
        self.connect((self.ofdm_allocation_buffer_0, 1), (self.ofdm_generic_softdemapper_vcf_0, 1))
        self.connect((self.single_pole_iir_filter_xx_0, 0), (self.ofdm_generic_softdemapper_vcf_0, 2))
        self.connect((self.ofdm_generic_softdemapper_vcf_0, 0), (self.trellis_permutation_0, 0))
        self.connect((self.ofdm_depuncture_ff_0, 0), (self.ofdm_viterbi_combined_fb_0, 0))
        self.connect((self.ofdm_allocation_buffer_0, 1), (self.ofdm_depuncture_ff_0, 1))
        self.connect((self.blocks_vector_source_x_0, 0), (self.ofdm_depuncture_ff_0, 2))
        self.connect((self.ofdm_allocation_buffer_0, 0), (self.ofdm_multiply_const_ii_0, 0))
        self.connect((self.ofdm_multiply_const_ii_0, 0), (self.ofdm_viterbi_combined_fb_0, 1))
        self.connect((self.ofdm_fbmc_separate_vcvc_1, 0), (self.ofdm_fbmc_polyphase_network_vcvc_0, 0))
        self.connect((self.ofdm_viterbi_combined_fb_0, 0), (self.tigr_ber_measurement_0, 2))
        self.connect((self.ofdm_dynamic_trigger_ib_0, 0), (self.tigr_ber_measurement_0, 3))
        self.connect((self.ofdm_fbmc_frame_sampler_0, 0), (self.tigr_fbmc_snr_estimator_0, 0))
        self.connect((self.ofdm_fbmc_frame_sampler_0, 1), (self.tigr_fbmc_snr_estimator_0, 1))
        self.connect((self.tigr_fbmc_inner_receiver_0, 1), (self.ofdm_fbmc_frame_sampler_0, 1))
        self.connect((self.tigr_fbmc_inner_receiver_0, 2), (self.ofdm_fbmc_frame_sampler_0, 0))
        self.connect((self.ofdm_fbmc_pilot_block_filter_0, 0), (self.ofdm_divide_frame_fc_0, 0))
        self.connect((self.rms, 0), (self.blocks_throttle_0, 0))
        self.connect((self.ofdm_fbmc_pilot_block_filter_0, 0), (self.ofdm_vector_sampler_0, 0))
        self.connect((self.tigr_fbmc_inner_receiver_0, 3), (self.zeromq_pub_sink_0, 0))
        self.connect((self.blocks_keep_one_in_n_1, 0), (self.zeromq_pub_sink_1, 0))
        self.connect((self.ofdm_vector_padding_0, 0), (self.ofdm_fbmc_beta_multiplier_vcvc_0, 0))
        self.connect((self.tigr_fbmc_inner_receiver_0, 0), (self.single_pole_iir_filter_xx_0, 0))
        self.connect((self.ofdm_fbmc_overlapping_parallel_to_serial_vcc_0, 0), (self.rms, 0))
        self.connect((self.ofdm_allocation_buffer_0, 0), (self.ofdm_dynamic_trigger_ib_0, 0))
        self.connect((self.ofdm_coded_bpsk_soft_decoder_0, 0), (self.tigr_ber_measurement_0, 0))
        self.connect((self.ofdm_allocation_buffer_0, 0), (self.tigr_ber_measurement_0, 1))
        self.connect((self.blks2_selector_0, 0), (self.ofdm_depuncture_ff_0, 0))
        self.connect((self.trellis_permutation_0, 0), (self.blks2_selector_0, 1))
        self.connect((self.ofdm_generic_softdemapper_vcf_0, 0), (self.blks2_selector_0, 0))
        self.connect((self.blocks_throttle_0, 0), (self.channels_channel_model_0, 0))
        self.connect((self.channels_channel_model_0, 0), (self.tigr_fbmc_inner_receiver_0, 0))


    def closeEvent(self, event):
        self.settings = Qt.QSettings("GNU Radio", "top_block")
        self.settings.setValue("geometry", self.saveGeometry())
        event.accept()

    def get_used_id_bits(self):
        return self.used_id_bits

    def set_used_id_bits(self, used_id_bits):
        self.used_id_bits = used_id_bits
        self.set_whitener_pn([randint(0,1) for i in range(self.used_id_bits*self.repeated_id_bits)])
        self.set_repeated_id_bits(self.subcarriers/self.used_id_bits)
        self.tigr_transmit_control_0.set_used_id_bits(self.used_id_bits)

    def get_subcarriers(self):
        return self.subcarriers

    def set_subcarriers(self, subcarriers):
        self.subcarriers = subcarriers
        self.set_training_data(default_block_header(self.subcarriers,self.fft_length,self.fbmc,self.estimation_preamble,[]))
        self.set_repeated_id_bits(self.subcarriers/self.used_id_bits)
        self.tigr_ber_measurement_0.set_subcarriers(self.subcarriers)
        self.tigr_scatterplot_0.set_subcarriers(self.subcarriers)
        self.tigr_fbmc_snr_estimator_0.set_subcarriers(self.subcarriers)
        self.tigr_transmit_control_0.set_subcarriers(self.subcarriers)
        self.channels_channel_model_0.set_noise_voltage(math.sqrt(1.0*self.fft_length/self.subcarriers)*math.sqrt(0.5)*10**(-self.SNR/20.0))
        self.tigr_fbmc_inner_receiver_0.set_subcarriers(self.subcarriers)

    def get_id_blocks(self):
        return self.id_blocks

    def set_id_blocks(self, id_blocks):
        self.id_blocks = id_blocks
        self.set_data_part(self.data_blocks + self.id_blocks)

    def get_fft_length(self):
        return self.fft_length

    def set_fft_length(self, fft_length):
        self.fft_length = fft_length
        self.set_training_data(default_block_header(self.subcarriers,self.fft_length,self.fbmc,self.estimation_preamble,[]))
        self.tigr_ber_measurement_0.set_fft_length(self.fft_length)
        self.tigr_scatterplot_0.set_fft_length(self.fft_length)
        self.tigr_fbmc_snr_estimator_0.set_fft_length(self.fft_length)
        self.tigr_transmit_control_0.set_fft_length(self.fft_length)
        self.channels_channel_model_0.set_noise_voltage(math.sqrt(1.0*self.fft_length/self.subcarriers)*math.sqrt(0.5)*10**(-self.SNR/20.0))
        self.tigr_fbmc_inner_receiver_0.set_fft_length(self.fft_length)

    def get_fbmc(self):
        return self.fbmc

    def set_fbmc(self, fbmc):
        self.fbmc = fbmc
        self.set_training_data(default_block_header(self.subcarriers,self.fft_length,self.fbmc,self.estimation_preamble,[]))
        self.tigr_ber_measurement_0.set_fbmc(self.fbmc)
        self.tigr_scatterplot_0.set_fbmc(self.fbmc)
        self.tigr_fbmc_snr_estimator_0.set_fbmc(self.fbmc)
        self.tigr_transmit_control_0.set_fbmc(self.fbmc)

    def get_estimation_preamble(self):
        return self.estimation_preamble

    def set_estimation_preamble(self, estimation_preamble):
        self.estimation_preamble = estimation_preamble
        self.set_training_data(default_block_header(self.subcarriers,self.fft_length,self.fbmc,self.estimation_preamble,[]))
        self.tigr_ber_measurement_0.set_estimation_preamble(self.estimation_preamble)
        self.tigr_scatterplot_0.set_estimation_preamble(self.estimation_preamble)
        self.tigr_fbmc_snr_estimator_0.set_estimation_preamble(self.estimation_preamble)
        self.tigr_transmit_control_0.set_estimation_preamble(self.estimation_preamble)
        self.tigr_fbmc_inner_receiver_0.set_estimation_preamble(self.estimation_preamble)

    def get_data_blocks(self):
        return self.data_blocks

    def set_data_blocks(self, data_blocks):
        self.data_blocks = data_blocks
        self.set_data_part(self.data_blocks + self.id_blocks)
        self.set_chunkdivisor(int(numpy.ceil(self.data_blocks/5.0)))
        self.tigr_ber_measurement_0.set_data_blocks(self.data_blocks)
        self.tigr_scatterplot_0.set_data_blocks(self.data_blocks)
        self.tigr_transmit_control_0.set_data_blocks(self.data_blocks)
        self.tigr_fbmc_inner_receiver_0.set_data_blocks(self.data_blocks)

    def get_training_data(self):
        return self.training_data

    def set_training_data(self, training_data):
        self.training_data = training_data
        self.set_frame_length(2*self.data_part + self.training_data.fbmc_no_preambles)

    def get_repeated_id_bits(self):
        return self.repeated_id_bits

    def set_repeated_id_bits(self, repeated_id_bits):
        self.repeated_id_bits = repeated_id_bits
        self.set_whitener_pn([randint(0,1) for i in range(self.used_id_bits*self.repeated_id_bits)])
        self.tigr_transmit_control_0.set_repeated_id_bits(self.repeated_id_bits)

    def get_data_part(self):
        return self.data_part

    def set_data_part(self, data_part):
        self.data_part = data_part
        self.set_frame_length(2*self.data_part + self.training_data.fbmc_no_preambles)
        self.tigr_transmit_control_0.set_data_part(self.data_part)

    def get_whitener_seed(self):
        return self.whitener_seed

    def set_whitener_seed(self, whitener_seed):
        self.whitener_seed = whitener_seed

    def get_whitener_pn(self):
        return self.whitener_pn

    def set_whitener_pn(self, whitener_pn):
        self.whitener_pn = whitener_pn

    def get_variable_function_probe_2(self):
        return self.variable_function_probe_2

    def set_variable_function_probe_2(self, variable_function_probe_2):
        self.variable_function_probe_2 = variable_function_probe_2

    def get_variable_function_probe_1(self):
        return self.variable_function_probe_1

    def set_variable_function_probe_1(self, variable_function_probe_1):
        self.variable_function_probe_1 = variable_function_probe_1

    def get_variable_function_probe_0(self):
        return self.variable_function_probe_0

    def set_variable_function_probe_0(self, variable_function_probe_0):
        self.variable_function_probe_0 = variable_function_probe_0

    def get_tx_hostname(self):
        return self.tx_hostname

    def set_tx_hostname(self, tx_hostname):
        self.tx_hostname = tx_hostname

    def get_samp_rate(self):
        return self.samp_rate

    def set_samp_rate(self, samp_rate):
        self.samp_rate = samp_rate
        self.blocks_throttle_0.set_sample_rate(self.samp_rate)

    def get_interleaver(self):
        return self.interleaver

    def set_interleaver(self, interleaver):
        self.interleaver = interleaver
        self.set_interleaver(trellis.self.interleaver(2000,666))

    def get_frame_length(self):
        return self.frame_length

    def set_frame_length(self, frame_length):
        self.frame_length = frame_length
        self.tigr_scatterplot_0.set_frame_length(self.frame_length)
        self.tigr_fbmc_snr_estimator_0.set_frame_length(self.frame_length)
        self.tigr_fbmc_inner_receiver_0.set_frame_length(self.frame_length)

    def get_filter_length(self):
        return self.filter_length

    def set_filter_length(self, filter_length):
        self.filter_length = filter_length
        self.tigr_transmit_control_0.set_filter_length(self.filter_length)
        self.tigr_fbmc_inner_receiver_0.set_filter_length(self.filter_length)

    def get_disable_freq_sync(self):
        return self.disable_freq_sync

    def set_disable_freq_sync(self, disable_freq_sync):
        self.disable_freq_sync = disable_freq_sync
        self.tigr_fbmc_inner_receiver_0.set_disable_freq_sync(self.disable_freq_sync)

    def get_coding(self):
        return self.coding

    def set_coding(self, coding):
        self.coding = coding
        self.tigr_transmit_control_0.set_coding(self.coding)

    def get_chunkdivisor(self):
        return self.chunkdivisor

    def set_chunkdivisor(self, chunkdivisor):
        self.chunkdivisor = chunkdivisor

    def get_ber_window(self):
        return self.ber_window

    def set_ber_window(self, ber_window):
        self.ber_window = ber_window
        self.tigr_ber_measurement_0.set_ber_window(self.ber_window)

    def get_amplitude(self):
        return self.amplitude

    def set_amplitude(self, amplitude):
        self.amplitude = amplitude
        Qt.QMetaObject.invokeMethod(self._amplitude_counter, "setValue", Qt.Q_ARG("double", self.amplitude))
        Qt.QMetaObject.invokeMethod(self._amplitude_slider, "setValue", Qt.Q_ARG("double", self.amplitude))
        self.rms.set_rms_amplitude(self.amplitude)

    def get_SNR(self):
        return self.SNR

    def set_SNR(self, SNR):
        self.SNR = SNR
        self.channels_channel_model_0.set_noise_voltage(math.sqrt(1.0*self.fft_length/self.subcarriers)*math.sqrt(0.5)*10**(-self.SNR/20.0))

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
