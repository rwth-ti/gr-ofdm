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

from numpy import concatenate, log10
from gnuradio import eng_notation
from gnuradio import gr, filter, zeromq
from gnuradio import blocks
from gnuradio import trellis
from gr_tools import log_to_file, terminate_stream

from ofdm import normalize_vcc, lms_phase_tracking,vector_sum_vcc
from ofdm import generic_demapper_vcb, generic_softdemapper_vcf, vector_mask, vector_sampler
from ofdm import skip, channel_estimator_02, scatterplot_sink
from ofdm import trigger_surveillance, ber_measurement, vector_sum_vff
from ofdm import generic_mapper_bcv, dynamic_trigger_ib, snr_estimator_dc_null
from preambles import pilot_subcarrier_filter,pilot_block_filter,default_block_header
from ofdm import depuncture_ff
from ofdm import multiply_const_ii
from ofdm import divide_frame_fc
import ofdm as ofdm

from time import strftime,gmtime

from snr_estimator import milans_snr_estimator, milans_sinr_sc_estimator, milans_sinr_sc_estimator2, milans_sinr_sc_estimator3


from station_configuration import *
from transmit_path import ber_reference_source
import common_options
import gr_tools
import copy
import preambles

from os import getenv
import os


import numpy

from random import seed,randint


from ofdm import repetition_decoder_bs
from gnuradio.blocks import delay


from transmit_path import static_control

from ofdm_receiver2 import ofdm_inner_receiver


class receive_path(gr.hier_block2):
  """
  OFDM Receiver Path

  Input: Baseband signal
  """
  def __init__(self, options):
    gr.hier_block2.__init__(self, "receive_path",
        gr.io_signature(1,1,gr.sizeof_gr_complex),
        gr.io_signature(0,0,0))

    print "This is receive path 2"

    common_options.defaults(options)

    config = self.config = station_configuration()

    config.data_subcarriers     = dsubc = options.subcarriers
    config.cp_length            = options.cp_length
    config.frame_data_blocks    = options.data_blocks
    config._verbose             = options.verbose #TODO: update
    config.fft_length           = options.fft_length
    config.dc_null              = options.dc_null
    config.training_data        = default_block_header(dsubc,
                                          config.fft_length, config.dc_null, options)
    config.coding              = options.coding
    config.ber_window           = options.ber_window
    config.bandwidth            = options.bandwidth
    config.gui_frame_rate       = options.gui_frame_rate

    config.periodic_parts       = 8

    config.frame_id_blocks      = 1 # FIXME

    self._options               = copy.copy(options) #FIXME: do we need this?

    config.block_length = config.fft_length + config.cp_length
    config.frame_data_part = config.frame_data_blocks + config.frame_id_blocks
    config.frame_length = config.frame_data_part + \
                          config.training_data.no_pilotsyms
    config.subcarriers = dsubc + \
                         config.training_data.pilot_subcarriers
    config.virtual_subcarriers = config.fft_length - config.subcarriers - config.dc_null

    total_subc = config.subcarriers

    # check some bounds
    if config.fft_length < config.subcarriers:
      raise SystemError, "Subcarrier number must be less than FFT length"
    if config.fft_length < config.cp_length:
      raise SystemError, "Cyclic prefix length must be less than FFT length"

    # adapt OFDM frame rate and GUI display frame rate
    self.keep_frame_n = int(1.0 / ( config.frame_length * (config.cp_length + config.fft_length) / config.bandwidth ) / config.gui_frame_rate)

    #self.input =  gr.kludge_copy(gr.sizeof_gr_complex)
    #self.connect( self, self.input )
    self.input = self


    ## Inner receiver

    ## Timing & Frequency Synchronization
    ## Channel estimation + Equalization
    ## Phase Tracking for sampling clock frequency offset correction
    inner_receiver = self.inner_receiver = ofdm_inner_receiver( options, options.log )
    self.connect( self.input, inner_receiver )
    ofdm_blocks = ( inner_receiver, 0 )
    frame_start = ( inner_receiver, 1 )
    disp_ctf = ( inner_receiver, 2 )



    # for ID decoder
    used_id_bits = config.used_id_bits = 8 #TODO: constant in source code!
    rep_id_bits = config.rep_id_bits = dsubc/used_id_bits #BPSK
    if options.log:
      print "rep_id_bits %d" % (rep_id_bits)
    if dsubc % used_id_bits <> 0:
      raise SystemError,"Data subcarriers need to be multiple of 10"

    ## Workaround to avoid periodic structure
    seed(1)
    whitener_pn = [randint(0,1) for i in range(used_id_bits*rep_id_bits)]





    ## NOTE!!! BIG HACK!!!
    ## first preamble ain't equalized ....
    ## for Milan's SNR estimator






    ## Outer Receiver

    ## Make new inner receiver compatible with old outer receiver
    ## FIXME: renew outer receiver

    self.ctf = disp_ctf

    frame_sampler = ofdm_frame_sampler(options)

    self.connect( ofdm_blocks, frame_sampler)
    self.connect( frame_start, (frame_sampler,1) )


#
#    ft = [0] * config.frame_length
#    ft[0] = 1
#
#    # The next block ensures that only complete frames find their way into
#    # the old outer receiver. The dynamic frame start trigger is hence
#    # replaced with a static one, fixed to the frame length.
#
#    frame_sampler = ofdm.vector_sampler( gr.sizeof_gr_complex * total_subc,
#                                              config.frame_length )
#    self.symbol_output = blocks.vector_to_stream( gr.sizeof_gr_complex * total_subc,
#                                              config.frame_length )
#    delayed_frame_start = blocks.delay( gr.sizeof_char, config.frame_length - 1 )
#    damn_static_frame_trigger = blocks.vector_source_b( ft, True )
#
#    if options.enable_erasure_decision:
#      frame_gate = vector_sampler(
#        gr.sizeof_gr_complex * total_subc * config.frame_length, 1 )
#      self.connect( ofdm_blocks, frame_sampler, frame_gate,
#                    self.symbol_output )
#    else:
#      self.connect( ofdm_blocks, frame_sampler, self.symbol_output )
#
#    self.connect( frame_start, delayed_frame_start, ( frame_sampler, 1 ) )

    if options.enable_erasure_decision:
      frame_gate = frame_sampler.frame_gate

    self.symbol_output = frame_sampler

    orig_frame_start = frame_start
    frame_start = (frame_sampler,1)
    self.frame_trigger = frame_start








    ## Pilot block filter
    pb_filt = self._pilot_block_filter = pilot_block_filter()
    self.connect(self.symbol_output,pb_filt)
    self.connect(self.frame_trigger,(pb_filt,1))

    self.frame_data_trigger = (pb_filt,1)

    if options.log:
      log_to_file(self, pb_filt, "data/pb_filt_out.compl")





    ## Pilot subcarrier filter
    ps_filt = self._pilot_subcarrier_filter = pilot_subcarrier_filter()
    self.connect(pb_filt,ps_filt)

    if options.log:
      log_to_file(self, ps_filt, "data/ps_filt_out.compl")


    pda_in = ps_filt


    ## Workaround to avoid periodic structure
    # for ID decoder
    seed(1)
    whitener_pn = [randint(0,1) for i in range(used_id_bits*rep_id_bits)]



    if not options.enable_erasure_decision:

      ## ID Block Filter
      # Filter ID block, skip data blocks
      id_bfilt = self._id_block_filter = vector_sampler(
            gr.sizeof_gr_complex * dsubc, 1 )
      if not config.frame_id_blocks == 1:
        raise SystemExit, "# ID Blocks > 1 not supported"

      self.connect(   ps_filt     ,   id_bfilt      )
      self.connect( ( pb_filt, 1 ), ( id_bfilt, 1 ) ) # trigger



      ## ID Demapper and Decoder, soft decision
      self.id_dec = self._id_decoder = ofdm.coded_bpsk_soft_decoder( dsubc,
          used_id_bits, whitener_pn )
      self.connect( id_bfilt, self.id_dec )

      print "Using coded BPSK soft decoder for ID detection"


    else: # options.enable_erasure_decision:

      id_bfilt = self._id_block_filter = vector_sampler(
        gr.sizeof_gr_complex * total_subc, config.frame_id_blocks )

      id_bfilt_trig_delay = 0
      for x in range( config.frame_length ):
        if x in config.training_data.pilotsym_pos:
          id_bfilt_trig_delay += 1
        else:
          break
      print "Position of ID block within complete frame: %d" %(id_bfilt_trig_delay)

      assert( id_bfilt_trig_delay > 0 ) # else not supported

      id_bfilt_trig = blocks.delay( gr.sizeof_char, id_bfilt_trig_delay )

      self.connect( ofdm_blocks, id_bfilt )
      self.connect( orig_frame_start, id_bfilt_trig, ( id_bfilt, 1 ) )

      self.id_dec = self._id_decoder = ofdm.coded_bpsk_soft_decoder( total_subc,
          used_id_bits, whitener_pn, config.training_data.shifted_pilot_tones )
      self.connect( id_bfilt, self.id_dec )

      print "Using coded BPSK soft decoder for ID detection"

      # The threshold block either returns 1.0 if the llr-value from the
      # id decoder is below the threshold, else 0.0. Hence we convert this
      # into chars, 0 and 1, and use it as trigger for the sampler.

      min_llr = ( self.id_dec, 1 )
      erasure_threshold = gr.threshold_ff( 10.0, 10.0, 0 ) # FIXME is it the optimal threshold?
      erasure_dec = gr.float_to_char()
      id_gate = vector_sampler( gr.sizeof_short, 1 )
      ctf_gate = vector_sampler( gr.sizeof_float * total_subc, 1 )


      self.connect( self.id_dec ,       id_gate )
      self.connect( self.ctf,      ctf_gate )

      self.connect( min_llr,       erasure_threshold,  erasure_dec )
      self.connect( erasure_dec, ( frame_gate, 1 ) )
      self.connect( erasure_dec, ( id_gate,    1 ) )
      self.connect( erasure_dec, ( ctf_gate,   1 ) )

      self.id_dec = self._id_decoder = id_gate
      self.ctf = ctf_gate



      print "Erasure decision for IDs is enabled"




    if options.log:
      id_dec_f = gr.short_to_float()
      self.connect(self.id_dec,id_dec_f)
      log_to_file(self, id_dec_f, "data/id_dec_out.float")


    if options.log:
      log_to_file(self, id_bfilt, "data/id_blockfilter_out.compl")


    # TODO: refactor names




    if options.log:
      map_src_f = gr.char_to_float(dsubc)
      self.connect(map_src,map_src_f)
      log_to_file(self, map_src_f, "data/map_src_out.float")

    ## Allocation Control
    if options.static_allocation: #DEBUG
        
        if options.coding:
            mode = 1 # Coding mode 1-9
            bitspermode = [0.5,1,1.5,2,3,4,4.5,5,6] # Information bits per mode
            bitcount_vec = [(int)(config.data_subcarriers*config.frame_data_blocks*bitspermode[mode-1])]
            bitloading = mode
        else:
            bitloading = 1
            bitcount_vec = [config.data_subcarriers*config.frame_data_blocks*bitloading]
        #bitcount_vec = [config.data_subcarriers*config.frame_data_blocks]
        self.bitcount_src = blocks.vector_source_i(bitcount_vec,True,1)
        # 0s for ID block, then data
        #bitloading_vec = [0]*dsubc+[0]*(dsubc/2)+[2]*(dsubc/2)
        bitloading_vec = [0]*dsubc+[bitloading]*dsubc
        bitloading_src = blocks.vector_source_b(bitloading_vec,True,dsubc)
        power_vec = [1]*config.data_subcarriers
        power_src = blocks.vector_source_f(power_vec,True,dsubc)
    else:
        self.allocation_buffer = ofdm.allocation_buffer(config.data_subcarriers, config.frame_data_blocks, "tcp://"+options.tx_hostname+":3333",config.coding)
        self.bitcount_src = (self.allocation_buffer,0)
        bitloading_src = (self.allocation_buffer,1)
        power_src = (self.allocation_buffer,2)
        self.connect(self.id_dec, self.allocation_buffer)

    if options.log:
        log_to_file(self, self.bitcount_src, "data/bitcount_src_rx.int")
        log_to_file(self, bitloading_src, "data/bitloading_src_rx.char")
        log_to_file(self, power_src, "data/power_src_rx.cmplx")
        log_to_file(self, self.id_dec, "data/id_dec_rx.short")

    ## Power Deallocator
    pda = self._power_deallocator = divide_frame_fc(config.frame_data_part, dsubc)
    self.connect(pda_in,(pda,0))
    self.connect(power_src,(pda,1))

    ## Demodulator
#    if 0:
#          ac_vector = [0.0+0.0j]*208
#          ac_vector[0] = (2*10**(-0.452))
#          ac_vector[3] = (10**(-0.651))
#          ac_vector[7] = (10**(-1.151))
#          csi_vector_inv=abs(numpy.fft.fft(numpy.sqrt(ac_vector)))**2
#          dm_csi = numpy.fft.fftshift(csi_vector_inv) # TODO

    dm_csi = [1]*dsubc # TODO
    dm_csi = blocks.vector_source_f(dm_csi,True)
    ## Depuncturer
    dp_trig = [0]*(config.frame_data_blocks/2)
    dp_trig[0] = 1
    dp_trig = blocks.vector_source_b(dp_trig,True) # TODO   


    if(options.coding):
        fo=ofdm.fsm(1,2,[91,121])
        if options.interleave:
            int_object=trellis.interleaver(2000,666)
            deinterlv = trellis.permutation(int_object.K(),int_object.DEINTER(),1,gr.sizeof_float)
        
        demod = self._data_demodulator = generic_softdemapper_vcf(dsubc, config.frame_data_part, config.coding)
        #self.connect(dm_csi,blocks.stream_to_vector(gr.sizeof_float,dsubc),(demod,2))
        if(options.ideal):
            self.connect(dm_csi,blocks.stream_to_vector(gr.sizeof_float,dsubc),(demod,2))
        else:
            dm_csi_filter = self.dm_csi_filter = filter.single_pole_iir_filter_ff(0.01,dsubc)
            self.connect(self.ctf, pilot_subcarrier_filter(complex_value=False), self.dm_csi_filter,(demod,2))
            #log_to_file(self, dm_csi_filter, "data/softs_csi.float")
        #self.connect(dm_trig,(demod,3))
    else:
        demod = self._data_demodulator = generic_demapper_vcb(dsubc, config.frame_data_part)
    if options.benchmarking:
        # Do receiver benchmarking until the number of frames x symbols are collected
        self.connect(pda,blocks.head(gr.sizeof_gr_complex*dsubc, options.N*config.frame_data_blocks),demod)
    else:        
        self.connect(pda,demod)
    self.connect(bitloading_src,(demod,1))

    if(options.coding):
        ## Depuncturing
        if not options.nopunct:
            depuncturing = depuncture_ff(dsubc,0)
            frametrigger_bitmap_filter = blocks.vector_source_b([1,0],True)
            self.connect(bitloading_src,(depuncturing,1))
            self.connect(dp_trig,(depuncturing,2))

        ## Decoding
        chunkdivisor = int(numpy.ceil(config.frame_data_blocks/5.0))
        print "Number of chunks at Viterbi decoder: ", chunkdivisor
        decoding = self._data_decoder = ofdm.viterbi_combined_fb(fo,dsubc,-1,-1,2,chunkdivisor,[-1,-1,-1,1,1,-1,1,1],ofdm.TRELLIS_EUCLIDEAN)

        
        if options.log and options.coding:
            log_to_file(self, decoding, "data/decoded.char")
            if not options.nopunct:
                log_to_file(self, depuncturing, "data/vit_in.float")
                    
        if not options.nopunct:
            if options.interleave:
                self.connect(demod,deinterlv,depuncturing,decoding)
            else:
                self.connect(demod,depuncturing,decoding)
        else:
            self.connect(demod,decoding)
        self.connect(self.bitcount_src, multiply_const_ii(1./chunkdivisor), (decoding,1))
        
    if options.scatterplot or options.scatter_plot_before_phase_tracking:
        scatter_vec_elem = self._scatter_vec_elem = ofdm.vector_element(dsubc,1)
        scatter_s2v = self._scatter_s2v = blocks.stream_to_vector(gr.sizeof_gr_complex,config.frame_data_blocks)

        scatter_id_filt = skip(gr.sizeof_gr_complex*dsubc,config.frame_data_blocks)
        scatter_id_filt.skip_call(0)
        scatter_trig = [0]*config.frame_data_part
        scatter_trig[0] = 1
        scatter_trig = blocks.vector_source_b(scatter_trig,True)
        self.connect(scatter_trig,(scatter_id_filt,1))
        self.connect(scatter_vec_elem,scatter_s2v)

        if not options.scatter_plot_before_phase_tracking:
            print "Enabling Scatterplot for data subcarriers"
            self.connect(pda,scatter_id_filt,scatter_vec_elem)
              # Work on this
              #scatter_sink = ofdm.scatterplot_sink(dsubc)
              #self.connect(pda,scatter_sink)
              #self.connect(map_src,(scatter_sink,1))
              #self.connect(dm_trig,(scatter_sink,2))
              #print "Enabled scatterplot gui interface"
            self.zmq_probe_scatter = zeromq.pub_sink(gr.sizeof_gr_complex,config.frame_data_blocks, "tcp://*:5560")
            self.connect(scatter_s2v, blocks.keep_one_in_n(gr.sizeof_gr_complex*config.frame_data_blocks,self.keep_frame_n), self.zmq_probe_scatter)
        else:
            print "Enabling Scatterplot for data before phase tracking"
            inner_rx = inner_receiver.before_phase_tracking
            #scatter_sink2 = ofdm.scatterplot_sink(dsubc,"phase_tracking")
            op = copy.copy(options)
            op.enable_erasure_decision = False
            new_framesampler = ofdm_frame_sampler(op)
            self.connect( inner_rx, new_framesampler )
            self.connect( orig_frame_start, (new_framesampler,1) )
            new_ps_filter = pilot_subcarrier_filter()
            new_pb_filter = pilot_block_filter()

            self.connect( (new_framesampler,1), (new_pb_filter,1) )
            self.connect( new_framesampler, new_pb_filter,
                         new_ps_filter, scatter_id_filt, scatter_vec_elem )

            #self.connect( new_ps_filter, scatter_sink2 )
            #self.connect( map_src, (scatter_sink2,1))
            #self.connect( dm_trig, (scatter_sink2,2))


    if options.log:
      if(options.coding):
          log_to_file(self, demod, "data/data_stream_out.float")
      else:
          data_f = gr.char_to_float()
          self.connect(demod,data_f)
          log_to_file(self, data_f, "data/data_stream_out.float")



    if options.sfo_feedback:
      used_id_bits = 10
      rep_id_bits = config.data_subcarriers/used_id_bits

      seed(1)
      whitener_pn = [randint(0,1) for i in range(used_id_bits*rep_id_bits)]

      id_enc = ofdm.repetition_encoder_sb(used_id_bits,rep_id_bits,whitener_pn)
      self.connect( self.id_dec, id_enc )

      id_mod = ofdm_bpsk_modulator(dsubc)
      self.connect( id_enc, id_mod )

      id_mod_conj = gr.conjugate_cc(dsubc)
      self.connect( id_mod, id_mod_conj )

      id_mult = blocks.multiply_vcc(dsubc)
      self.connect( id_bfilt, ( id_mult,0) )
      self.connect( id_mod_conj, ( id_mult,1) )

#      id_mult_avg = filter.single_pole_iir_filter_cc(0.01,dsubc)
#      self.connect( id_mult, id_mult_avg )

      id_phase = gr.complex_to_arg(dsubc)
      self.connect( id_mult, id_phase )

      log_to_file( self, id_phase, "data/id_phase.float" )

      est=ofdm.LS_estimator_straight_slope(dsubc)
      self.connect(id_phase,est)

      slope=blocks.multiply_const_ff(1e6/2/3.14159265)
      self.connect( (est,0), slope )

      log_to_file( self, slope, "data/slope.float" )
      log_to_file( self, (est,1), "data/offset.float" )

    # ------------------------------------------------------------------------ #




    # Display some information about the setup
    if config._verbose:
      self._print_verbage()

    ## debug logging ##
    if options.log:
#      log_to_file(self,self.ofdm_symbols,"data/unequalized_rx_ofdm_symbols.compl")
#      log_to_file(self,self.ofdm_symbols,"data/unequalized_rx_ofdm_symbols.float",mag=True)


      fftlen = 256
      my_window = window.hamming(fftlen) #.blackmanharris(fftlen)
      rxs_sampler = vector_sampler(gr.sizeof_gr_complex,fftlen)
      rxs_sampler_vect = concatenate([[1],[0]*49])
      rxs_trigger = blocks.vector_source_b(rxs_sampler_vect.tolist(),True)
      rxs_window = blocks.multiply_const_vcc(my_window)
      rxs_spectrum = gr.fft_vcc(fftlen,True,[],True)
      rxs_mag = gr.complex_to_mag(fftlen)
      rxs_avg = filter.single_pole_iir_filter_ff(0.01,fftlen)
      #rxs_logdb = blocks.nlog10_ff(20.0,fftlen,-20*log10(fftlen))
      rxs_logdb = gr.kludge_copy( gr.sizeof_float * fftlen )
      rxs_decimate_rate = gr.keep_one_in_n(gr.sizeof_float*fftlen,1)
      self.connect(rxs_trigger,(rxs_sampler,1))
      self.connect(self.input,rxs_sampler,rxs_window,
                   rxs_spectrum,rxs_mag,rxs_avg,rxs_logdb, rxs_decimate_rate)
      log_to_file( self, rxs_decimate_rate, "data/psd_input.float" )


    #output branches
    self.publish_rx_performance_measure()


  def filter_constellation_samples_to_file( self ):

    config = self.config

    vlen = config.data_subcarriers



    pda = self._power_deallocator
    bmaptrig_stream = [1, 1]+[0]*(config.frame_data_blocks-1)
    dm_trig = self._bitmap_trigger = blocks.vector_source_b(bmaptrig_stream, True)


    for i in range(8):
      print "pipe",i+1,"to",files[i]
      cfilter = ofdm.constellation_sample_filter( i+1, vlen )
      self.connect( pda, (cfilter,0) )
      self.connect( map_src, (cfilter,1) )
      self.connect( dm_trig, (cfilter,2) )
      log_to_file( self, cfilter, files[i] )
    print "done"
  # ---------------------------------------------------------------------------#
  # RX Performance Measure propagation through corba event channel

  def _rx_performance_measure_initialized(self):
    return self.__dict__.has_key('rx_performance_measure_initialized') \
          and self.rx_performance_measure_initialized

  def publish_rx_performance_measure(self):
    if self._rx_performance_measure_initialized():
      return

    self.rx_performance_measure_initialized = True

    config = station_configuration()
    vlen = config.data_subcarriers
    vlen_sinr_sc = config.subcarriers

    self.setup_ber_measurement()
    self.setup_snr_measurement()

    ber_mst = self._ber_measuring_tool
    if self._options.sinr_est:
        sinr_mst = self._sinr_measurement
    else:
        snr_mst = self._snr_measurement

    ctf = self.filter_ctf()

    self.zmq_probe_ctf = zeromq.pub_sink(gr.sizeof_float,config.data_subcarriers, "tcp://*:5559")
    self.connect(ctf, blocks.keep_one_in_n(gr.sizeof_float*config.data_subcarriers,self.keep_frame_n) ,self.zmq_probe_ctf)
#    self.rx_per_sink = rpsink = corba_rxinfo_sink("himalaya",config.ns_ip,
#                                    config.ns_port,vlen,config.rx_station_id)


    if self.__dict__.has_key('_img_xfer_inprog') is False:

#      print "BER img xfer"
#      self.connect(ber_mst,(rpsink,3))
#      ## no sampling needed
      # 3. SNR


      print "Normal BER measurement"

      trig_src = dynamic_trigger_ib(False)
      self.connect(self.bitcount_src,trig_src)

      ber_sampler = vector_sampler(gr.sizeof_float,1)
      self.connect(ber_mst,(ber_sampler,0))
      self.connect(trig_src,(ber_sampler,1))


      if self._options.log:
          trig_src_float = gr.char_to_float()
          self.connect(trig_src,trig_src_float)
          log_to_file(self, trig_src_float , 'data/dynamic_trigger_out.float')


      if self._options.sinr_est is False:
          self.zmq_probe_ber = zeromq.pub_sink(gr.sizeof_float, 1, "tcp://*:5556")
          self.connect(ber_sampler,blocks.keep_one_in_n(gr.sizeof_float,self.keep_frame_n) ,self.zmq_probe_ber)

          self.zmq_probe_snr = zeromq.pub_sink(gr.sizeof_float, 1, "tcp://*:5555")
          self.connect(snr_mst,blocks.keep_one_in_n(gr.sizeof_float,self.keep_frame_n) ,self.zmq_probe_snr)



  ##############################################################################
  def setup_imgtransfer_sink(self):
    demod = self._data_demodulator

    config = station_configuration()

    port = self._rx_control.add_mobile_station(config.rx_station_id)
    bc_src = (self._rx_control,port)

    UDP_PACKET_SIZE = 4096*8

    imgtransfersink = ofdm.imgtransfer_sink( UDP_PACKET_SIZE,
                                     "localhost", 0, "localhost", 45454,
                                     self._options.img, False )


    #imgtransfersink = ofdm.imgtransfer_sink(UDP_PACKET_SIZE,self._options.img,
    #                                        False)
    #udpsink = gr.udp_sink( 1, "127.0.0.1", 0, "127.0.0.1", 45454,
    #                       UDP_PACKET_SIZE )
    #udpsink = blocks.null_sink( gr.sizeof_char )

    self.connect( bc_src, ( imgtransfersink, 0 ) )
    self.connect( demod,  ( imgtransfersink, 1 ) )
    #self.connect( imgtransfersink, udpsink )

    self._measuring_ber = True
    self._img_xfer_inprog = True

    self.imgxfer_sink = imgtransfersink
    self._ber_measuring_tool = None

#    self._ber_measuring_tool = ofdm.compat_read_ber_from_imgxfer( imgtransfersink )
#
#    if self._options.log:
#      log_to_file( self, self._ber_measuring_tool, "data/ber_imgxfer.float" )
#
#    self.connect( self.frame_trigger, self._ber_measuring_tool )

  # ---------------------------------------------------------------------------#
  # BER Measurement Section

  def setup_ber_measurement(self):
    """
    Setup bit error rate measurement blocks. Using the decoded ID, a reference
    source identical to that in the transmitter reproduces the sent data. A
    measurement block compares the demodulated stream and the reference. It
    counts the bit errors within the given window (specified at the command
    line).
    Access the BER value via get_ber().
    """
    if self.measuring_ber():
      return

    if(self._options.coding):
        decoding = self._data_decoder
    else:
        demod = self._data_demodulator

    config = station_configuration()


    ## Data Reference Source
    dref_src = self._data_reference_source = ber_reference_source(self._options)
    self.connect(self.id_dec,(dref_src,0))
    self.connect(self.bitcount_src,(dref_src,1))

    ## BER Measuring Tool
    ber_mst = self._ber_measuring_tool = ber_measurement(int(config.ber_window))
    if(self._options.coding):
        self.connect(decoding,ber_mst)
    else:
        self.connect(demod,ber_mst)
    self.connect(dref_src,(ber_mst,1))

    self._measuring_ber = True

    if self._options.enable_ber2:
      ber2 = ofdm.bit_position_dependent_ber( "BER2_" + strftime("%Y%m%d%H%M%S",gmtime()) )
      if(self._options.coding):
        self.connect( decoding, ( ber2, 1 ) )
      else:
        self.connect( demod, ( ber2, 1 ) )
      self.connect( dref_src, ( ber2, 0 ) )
      self.connect( bc_src, ( ber2, 2 ) )

    if self._options.log:
      log_to_file(self, ber_mst, "data/ber_out.float")
      data_f = gr.char_to_float()
      self.connect(dref_src,data_f)
      log_to_file(self, data_f, "data/dataref_out.float")


  def publish_ber_measurement(self,unique_id):
    """
    Install CORBA servant to allow remote access to the BER value. The servant
    is identified with the unique_id parameter. It is registered at the
    NameService as "ofdm_ti."+unique_id.
    If not setup previously, the measurement setup is invoked.
    """

    self.setup_ber_measurement()

    config = station_configuration()
    uid = str(unique_id)
    max_buffered_windows = 3000 # FIXME: find better solution
    dist = config.ber_window

    def new_servant(uid):
      ## Message Sink
      sampler = vector_sampler(gr.sizeof_float,1)
      trigsrc = blocks.vector_source_b(concatenate([[0]*(int(dist)-1),[1]]),True)
      msgq = gr.msg_queue(max_buffered_windows)
      msg_sink = gr.message_sink(gr.sizeof_float,msgq,True)
      self.connect(self._ber_measuring_tool,sampler,msg_sink)
      self.connect(trigsrc,(sampler,1))
      self.servants.append(corba_data_buffer_servant(uid,1,msgq))
      print "Publishing BER under id: %s" % (uid)

    try:
      for x in unique_id:
        new_servant(str(x))
    except:
      new_servant(str(unique_id))



  def measuring_ber(self):
    """
    Return if already measuring the BER.
    """
    return self.__dict__.has_key('_measuring_ber') and self._measuring_ber

  # ---------------------------------------------------------------------------#
  # SNR Measurement Section

  def setup_snr_measurement(self):
    """
    Perform SNR measurement.
    It uses the data reference from the BER measurement. I.e. if that is not
    setup, it will be setup. Only data subcarriers that are assigned to the
    station are considered in the measurement. Note that there is no sink
    prepared. You need to setup a sink, e.g. with one or more invocation
    of a "publish.."-function.
    SNR output is in dB.
    """
    if not self.measuring_ber():
      self.setup_ber_measurement()
      print "Warning: Setup BER Measurement forced"

    if self.measuring_snr():
      return

    config = station_configuration()

    vlen = config.subcarriers
    frame_length = config.frame_length
    L = config.periodic_parts

    snr_est_filt = skip(gr.sizeof_gr_complex*vlen,frame_length)
    for x in range(1,frame_length):
      snr_est_filt.skip_call(x)

    ## NOTE HACK!! first preamble is not equalized

    self.connect(self.symbol_output,snr_est_filt)
    self.connect(self.frame_trigger,(snr_est_filt,1))

#    snrm = self._snr_measurement = milans_snr_estimator( vlen, vlen, L )
#
#    self.connect(snr_est_filt,snrm)
#
#    if self._options.log:
#          log_to_file(self, self._snr_measurement, "data/milan_snr.float")

    #Addition for SINR estimation
    if self._options.sinr_est:
        snr_est_filt_2 = skip(gr.sizeof_gr_complex*vlen,frame_length)
        for x in range(frame_length):
          if x != config.training_data.channel_estimation_pilot[0]:
            snr_est_filt_2.skip_call(x)

        self.connect(self.symbol_output,snr_est_filt_2)
        self.connect(self.frame_trigger,(snr_est_filt_2,1))

        sinrm = self._sinr_measurement = milans_sinr_sc_estimator2( vlen, vlen, L )

        self.connect(snr_est_filt,sinrm)
        self.connect(snr_est_filt_2,(sinrm,1))
        if self._options.log:
            log_to_file(self, (self._sinr_measurement,0), "data/milan_sinr_sc.float")
            log_to_file(self, (self._sinr_measurement,1), "data/milan_snr.float")

    else:
        #snrm = self._snr_measurement = milans_snr_estimator( vlen, vlen, L )
        snr_estim = snr_estimator_dc_null(vlen, L, config.dc_null)
        scsnrdb = filter.single_pole_iir_filter_ff(0.1)
        snrm = self._snr_measurement = blocks.nlog10_ff(10,1,0)
        self.connect(snr_est_filt,snr_estim,scsnrdb,snrm)
        self.connect((snr_estim,1),blocks.null_sink(gr.sizeof_float))
        #log_to_file(self, snrm, "data/snrm.float")

        if self._options.log:
            log_to_file(self, self._snr_measurement, "data/milan_snr.float")


  def measuring_snr(self):
    """
    Return if already measuring the SNR.
    """
    return self.__dict__.has_key('_snr_measurement')

  def publish_average_snr(self,unique_id):
    """
    Provide remote access to SNR data.
    We use a CORBA servant providing the data buffer interface to distribute
    the data. It is identified at the NameService with its unique_id. Its name
    is "ofdm_ti"+unique_id.
    The SNR data is low pass filtered. One SNR value per data block (none for
    ids).

    If the parameter unique_id is iterable, several CORBA servants using the
    same signal processing chain are created.
    """

    self.setup_snr_measurement()

    config = station_configuration()

    snrm = self._snr_measurement
    uid = str(unique_id)

    max_buffered_frames = 3000 # FIXME: find better solution

    def new_servant(uid):
      ## Message Sink
      msgq = gr.msg_queue(config.frame_ *max_buffered_frames)
      msg_sink = gr.message_sink(gr.sizeof_float,msgq,True)
      self.connect(snrm,msg_sink)
      self.servants.append(corba_data_buffer_servant(uid,1,msgq))
      print "Publishing SNR under id: %s" % (uid)

    try:
      for x in unique_id:
        new_servant(str(x))
    except:
      new_servant(str(x))

  # ---------------------------------------------------------------------------#


  def change_estim_power(self,val):
    self.inner_receiver.inv_estimated_CTF_mul.set_k(1.0/val[0])
    #print "CHANGE set_k", val[0]
    #self.set_rms_amplitude(val[0])

  def enable_estim_power_adjust(self,unique_id):
    self.servants.append(corba_push_vector_f_servant(str(unique_id),1,
        self.change_estim_power,
        msg="Changing estim power output rms level\n"))

  def publish_estim_power(self,unique_id):
    def dummy_reset():
      pass
    self.servants.append(corba_ndata_buffer_servant(str(unique_id),
        self.get_rms_amplitude,dummy_reset))

  def filter_ctf(self):
    if self.__dict__.has_key('filtered_ctf'):
      return self.filtered_ctf

    config = self.config

    vlen = config.data_subcarriers
    frame_len = config.frame_length

#    # we want the preamble used for channel estimation
#    keep_est_preamble = skip(gr.sizeof_float*config.subcarriers, frame_len)
#    for i in range( frame_len ):
#      if i != config.training_data.channel_estimation_pilot[0]:
#        keep_est_preamble.skip_call(i)
#
#    self.connect( self.ctf, (keep_est_preamble,0) )
#    self.connect( self.frame_trigger, (keep_est_preamble,1) )

    # there is only one CTF estimate (display CTF) per frame ...

    #self.ctf_soft_dem
    psubc_filt = pilot_subcarrier_filter(complex_value=False)
    self.connect( self.ctf, psubc_filt )

    lp_filter = filter.single_pole_iir_filter_ff(0.1,vlen)
    self.connect( psubc_filt, lp_filter )
    #log_to_file(self,lp_filter,"data/filt_ctf.float")

    self.filtered_ctf = lp_filter
    return lp_filter


  def publish_ctf(self,unique_id):
    """
    corbaname: ofdm_ti.unique_id
    """

    config = self.config
    vlen = config.data_subcarriers

    msgq = gr.msg_queue(2)
    msg_sink = gr.message_sink(gr.sizeof_float*vlen,msgq,True)

    ctf = self.filter_ctf()
    self.connect( ctf, msg_sink )

    self.servants.append(corba_data_buffer_servant(str(unique_id),vlen,msgq))

    print "Publishing CTF under id: %s" % (unique_id)


  def publish_sinrsc(self,unique_id):
    """
    corbaname: ofdm_ti.unique_id
    """

    config = self.config
    vlen = config.subcarriers

    msgq = gr.msg_queue(2)
    msg_sink = gr.message_sink(gr.sizeof_float*vlen,msgq,True)

    sinrsc = self._sinr_measurement
    self.connect( sinrsc, msg_sink )

    self.servants.append(corba_data_buffer_servant(str(unique_id),vlen,msgq))

  def publish_tm_window(self,unique_id):
    """
    corbaname: ofdm_ti.unique_id
    """
    raise SystemError,"Bad guy! Obey the gnuradio hierarchy ..."

    config = self.config
    msgq = gr.msg_queue(10)
    msg_sink = gr.message_sink(gr.sizeof_float*config.fft_length,msgq,True)
    sampler = vector_sampler(gr.sizeof_float,config.fft_length)

    self.connect(self.receiver.timing_metric,(sampler,0))
    self.connect(self.receiver.time_sync,delay(gr.sizeof_char,config.fft_length/2-1),(sampler,1))
    self.connect(sampler,msg_sink)

    self.servants.append(corba_data_buffer_servant(str(unique_id),config.fft_length,msgq))

  def publish_packetloss(self,unique_id):
    """
    corbaname: ofdm_ti.unique_id
    """
    self.servants.append(corba_ndata_buffer_servant(str(unique_id),
        self.trigger_watcher.lost_triggers,self.trigger_watcher.reset_counter))

  def set_scatterplot_subc(self, subc):
     return self._scatter_vec_elem.set_element(int(subc))

  def add_options(normal, expert):
    """
    Adds receiver-specific options to the Options Parser
    """
    common_options.add_options(normal,expert)
    preambles.default_block_header.add_options(normal,expert)

    ofdm_inner_receiver.add_options( normal, expert )

    expert.add_option("", "--ber-window",
      type="intx", default=50000,
      help="window size for BER measurement")

    normal.add_option("", "--img",
      type="string", default="ratatouille.bmp",
      help="Input Bitmap .bmp for img transfer sink")

    expert.add_option("", "--enable-erasure-decision", action="store_true",
                      default=False,
                      help="Enables erasure decision for ID data detection")

    expert.add_option( "", "--no-decoding",
                       action="store_true",
                       default=False,
                       help="Disable decoding, no demapper etc., only ID decoding")
    expert.add_option( "", "--enable-ber2",
                       action="store_true",
                       default=False)
    expert.add_option("", "--sinr-est", action="store_true", default=False,
                      help="Enable SINR per subcarrier estimation [default=%default]")

    normal.add_option("", "--scatterplot",
                      action="store_true",
                      default=False,
                      help="Enable the Scatterplot GUI interface")

    expert.add_option("","--sfo-feedback",action="store_true",default=False)

    normal.add_option("", "--scatter-plot-before-phase-tracking",
                      action="store_true", default=False,
                      help="Enable Scatterplot before phase tracking block")
    normal.add_option( "", "--coding",
                       action="store_true",
                       default=False,
                       help="Enable channel coding")
    normal.add_option("", "--nopunct", action="store_true",
              default=False,
              help="Disable puncturing/depuncturing")
    normal.add_option("", "--interleave", action="store_true",
              default=False,
              help="Enable interleaving")
    expert.add_option('', '--benchmarking', action='store_true', default=False,
                      help='Modify transmitter for the benchmarking mode')


  # Make a static method to call before instantiation
  add_options = staticmethod(add_options)

  def _print_verbage(self):
    """
    Prints information about the receive path
    """
    # TODO: update
    print "\nOFDM Demodulator:"
    print "FFT length:      %3d"   % (config.fft_length)
    print "Subcarriers:     %3d"   % (config.data_subcarriers)
    print "CP length:       %3d"   % (config.cp_length)
    print "Preamble count:  %3d"   % (self._preambles)
    print "Syms per block:  %3d"   % (config.frame_data_blocks)
    self.receiver._print_verbage()

  def __del__(self):
    print "del"
    del self.servants

################################################################################
################################################################################

class ofdm_bpsk_demodulator (gr.hier_block2):
  """
  Demodulator with static map. Always demodulates all data subcarriers with BSPK.
  Input: data subcarriers
  Output: data bit stream
  """
  def __init__(self,data_subcarriers):
    gr.hier_block2.__init__(self,
      "ofdm_bpsk_demodulator",
      gr.io_signature( 1, 1, gr.sizeof_gr_complex * data_subcarriers ),
      gr.io_signature( 1, 1, gr.sizeof_char ) )

    modmap = [1]*data_subcarriers
    map_src = blocks.vector_source_b(modmap,True,data_subcarriers)

    trig_src = blocks.vector_source_b([1],True)

    demod = generic_demapper_vcb(data_subcarriers)

    self.connect(self,demod,self)
    self.connect(map_src,(demod,1))
    self.connect(trig_src,(demod,2))

################################################################################
################################################################################

class ofdm_bpsk_modulator (gr.hier_block2):
  def __init__(self,data_subcarriers):
    gr.hier_block2.__init__(self,
      "ofdm_bpsk_demodulator",
      gr.io_signature( 1, 1, gr.sizeof_char ),
      gr.io_signature( 1, 1, gr.sizeof_gr_complex * data_subcarriers ) )

    modmap = [1]*data_subcarriers
    map_src = blocks.vector_source_b(modmap,True,data_subcarriers)

    trig_src = blocks.vector_source_b([1],True)

    mod = ofdm.generic_mapper_bcv(data_subcarriers)

    self.connect(self,mod,self)
    self.connect(map_src,(mod,1))
    self.connect(trig_src,(mod,2))

################################################################################
################################################################################
# Useful for debugging: dummy implementations

# replace rx performance measure sink
class rpsink_dummy ( gr.hier_block2 ):
  def __init__(self):

    gr.hier_block2.__init__(self,"rpsinkdummy",
      gr.io_signature3(4,4,gr.sizeof_short,
                           gr.sizeof_float*vlen,
                           gr.sizeof_float),
      gr.io_signature (0,0,0))

    terminate_stream( self, (self,0) )
    terminate_stream( self, (self,1) )
    terminate_stream( self, (self,2) )
    terminate_stream( self, (self,3) )



class ofdm_frame_sampler( gr.hier_block2 ):
  def __init__(self,options):
    config = station_configuration()

    total_subc = config.subcarriers
    vlen = total_subc

    gr.hier_block2.__init__(self,"ofdm_frame_sampler",
      gr.io_signature2(2,2,gr.sizeof_gr_complex*vlen,
                       gr.sizeof_char),
      gr.io_signature2(2,2,gr.sizeof_gr_complex*vlen,
                 gr.sizeof_char))


    ft = [0] * config.frame_length
    ft[0] = 1

    # The next block ensures that only complete frames find their way into
    # the old outer receiver. The dynamic frame start trigger is hence
    # replaced with a static one, fixed to the frame length.

    frame_sampler = ofdm.vector_sampler( gr.sizeof_gr_complex * total_subc,
                                              config.frame_length )
    symbol_output = blocks.vector_to_stream( gr.sizeof_gr_complex * total_subc,
                                              config.frame_length )
    delayed_frame_start = blocks.delay( gr.sizeof_char, config.frame_length - 1 )
    damn_static_frame_trigger = blocks.vector_source_b( ft, True )

    if options.enable_erasure_decision:
      self.frame_gate = vector_sampler(
        gr.sizeof_gr_complex * total_subc * config.frame_length, 1 )
      self.connect( self, frame_sampler, self.frame_gate,
                    symbol_output )
    else:
      self.connect( self, frame_sampler, symbol_output, self )

    self.connect( (self,1), delayed_frame_start, ( frame_sampler, 1 ) )

    self.connect( damn_static_frame_trigger, (self,1) )

