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

from gnuradio import gr, blocks, zeromq
from gnuradio import fft as fft_blocks
from gnuradio.eng_option import eng_option

from optparse import OptionParser
from gr_tools import log_to_file,terminate_stream

import ofdm as ofdm
from preambles import fbmc_inner_pilot_block_filter
import numpy
import math

from autocorrelator import autocorrelator
from station_configuration import station_configuration



class fbmc_inner_receiver( gr.hier_block2 ):
  def __init__( self, options, log = False ):
    
    ## Read configuration
    config = station_configuration()
    
    fft_length    = config.fft_length
    #cp_length     = config.cp_length
    block_header  = config.training_data
    data_subc     = config.data_subcarriers
    virtual_subc  = config.virtual_subcarriers
    total_subc    = config.subcarriers
    block_length  = config.block_length
    frame_length  = config.frame_length
    
    L             = block_header.mm_periodic_parts
    
        
    cp_length     = config.cp_length


    
    print "data_subc: ", config.data_subcarriers
    print "total_subc: ", config.subcarriers
    print "frame_lengthframe_length: ", frame_length
    
    
    ## Set Input/Output signature
    gr.hier_block2.__init__( self, 
        "fbmc_inner_receiver",
        gr.io_signature(
            1, 1,
            gr.sizeof_gr_complex ),
        gr.io_signature3(
            3, 3,
            gr.sizeof_gr_complex * total_subc,    # OFDM blocks
            gr.sizeof_char,                       # Frame start
            gr.sizeof_float * total_subc ) )      # Normalized |CTF|^2 
    
    
    ## Input and output ports
    self.input = rx_input = self
    
    out_ofdm_blocks = ( self, 0 )
    out_frame_start = ( self, 1 )
    out_disp_ctf    = ( self, 2 )
    
    
    ## pre-FFT processing
    
    
    ## Compute autocorrelations for S&C preamble
    ## and cyclic prefix
    
    self._sc_metric = sc_metric = autocorrelator( fft_length/2, fft_length/2 )
    self._gi_metric = gi_metric = autocorrelator( fft_length, cp_length )
    
    self.connect( rx_input, sc_metric )
    self.connect( rx_input, gi_metric )
    
    ## Sync. Output contains OFDM blocks
    sync = ofdm.time_sync( fft_length/2, cp_length)
    self.connect( rx_input, ( sync, 0 ) )
    self.connect( sc_metric, ( sync, 1 ) )
    self.connect( gi_metric, ( sync, 2 ) )
    
    stv_help = blocks.stream_to_vector(gr.sizeof_gr_complex*config.fft_length/2, 1)
    self.connect(( sync, 0 ), stv_help)
    ofdm_blocks = stv_help
    #ofdm_blocks = ( sync, 0 )
    frame_start = ( sync, 1 )
    #log_to_file(self, frame_start, "data/frame_start.compl")
    
    #log_to_file( self, sc_metric, "data/sc_metric.float" )
    #log_to_file( self, gi_metric, "data/gi_metric.float" )
    #log_to_file( self, (sync,1), "data/sync.float" )
    
#    log_to_file(self,ofdm_blocks,"data/ofdm_blocks_original.compl")
    
    if options.disable_time_sync or options.ideal:
      terminate_stream(self, ofdm_blocks)
      terminate_stream(self, frame_start)
      
      serial_to_parallel = blocks.stream_to_vector(gr.sizeof_gr_complex,fft_length/2)
      #discard_cp = ofdm.vector_mask(block_length,cp_length,fft_length,[])
      #serial_to_parallel = blocks.stream_to_vector(gr.sizeof_gr_complex,block_length)
      #discard_cp = ofdm.vector_mask(block_length,cp_length,fft_length,[])
      
      self.connect( rx_input, serial_to_parallel)
      ofdm_blocks = serial_to_parallel
      #self.connect( rx_input, serial_to_parallel, discard_cp )
      
      frame_start = [0]*frame_length
      frame_start[0] = 1
      frame_start = blocks.vector_source_b(frame_start,True)
      
      print "Disabled time synchronization stage"
    
    print"\t\t\t\t\tframe_length = ",frame_length
    
    
    ## Extract preamble, feed to Morelli & Mengali frequency offset estimator
    assert( block_header.mm_preamble_pos == 0 )
    morelli_foe = ofdm.mm_frequency_estimator( fft_length/2, L/2 )
    sampler_preamble = ofdm.vector_sampler( gr.sizeof_gr_complex * fft_length/2,
                                            1 )
    self.connect( ofdm_blocks, ( sampler_preamble, 0 ) )
    self.connect( frame_start, ( sampler_preamble, 1 ) )
    self.connect( sampler_preamble, morelli_foe )
    freq_offset = morelli_foe
    print "FRAME_LENGTH: ", frame_length
    log_to_file( self, sampler_preamble, "data/sampler_preamble.compl" )
    #log_to_file( self, rx_input, "data/rx_input.compl" )
    
    
    ## Adaptive LMS FIR filtering of frequency offset
    lms_fir = ofdm.lms_fir_ff( 20, 1e-3 ) # TODO: verify parameter choice
    self.connect( freq_offset, lms_fir )
    freq_offset = lms_fir
    
    self.zmq_probe_freqoff = zeromq.pub_sink(gr.sizeof_float, 1, "tcp://*:5557")
    self.connect(lms_fir, blocks.keep_one_in_n(gr.sizeof_float,20) ,self.zmq_probe_freqoff)
    
    #log_to_file(self, lms_fir, "data/lms_fir.float")
    
    if options.disable_freq_sync or options.ideal:
      terminate_stream(self, freq_offset)
      freq_offset = blocks.vector_source_f([0.0],True)
      print "Disabled frequency synchronization stage"
    
    ## Correct frequency shift, feed-forward structure
    frequency_shift = ofdm.frequency_shift_vcc( fft_length/2, -2.0/fft_length,
                                                cp_length )
    self.connect( ofdm_blocks, ( frequency_shift, 0 ) )
    self.connect( freq_offset, ( frequency_shift, 1 ) )
    self.connect( frame_start, ( frequency_shift, 2 ) )
    #ofdm_blocks = frequency_shift
    terminate_stream(self, frequency_shift)
    
    
    
    inner_pb_filt = self._inner_pilot_block_filter = fbmc_inner_pilot_block_filter()
    self.connect(ofdm_blocks,inner_pb_filt)
    self.connect(frame_start,(inner_pb_filt,1))
    self.connect((inner_pb_filt,1),blocks.null_sink(gr.sizeof_char))
    
    
    ofdm_blocks = (inner_pb_filt,0)
    
    
    overlap_ser_to_par = ofdm.fbmc_overlapping_serial_to_parallel_cvc(fft_length)
    self.separate_vcvc = ofdm.fbmc_separate_vcvc(fft_length, 2)
    self.polyphase_network_vcvc_1 = ofdm.fbmc_polyphase_network_vcvc(fft_length, 4, 4*fft_length-1, True)
    self.polyphase_network_vcvc_2 = ofdm.fbmc_polyphase_network_vcvc(fft_length, 4, 4*fft_length-1, True)
    self.junction_vcvc = ofdm.fbmc_junction_vcvc(fft_length, 2)
    self.fft_fbmc = fft_blocks.fft_vcc(fft_length, True, [], True)
    
    center_preamble = [1, -1j, -1, 1j]
    self.preamble = preamble = [0]*total_subc + center_preamble*((int)(total_subc/len(center_preamble)))+[0]*total_subc
    self.multiply_const= blocks.multiply_const_vcc(([1.0/(fft_length*0.6863)]*total_subc))    
    self.beta_multiplier_vcvc = ofdm.fbmc_beta_multiplier_vcvc(total_subc, 4, 4*total_subc-1, 0)
    self.skiphead = blocks.skiphead(gr.sizeof_gr_complex*total_subc, 2*4-1-1)
    self.skiphead_1 = blocks.skiphead(gr.sizeof_gr_complex*total_subc, 1)
    self.remove_preamble_vcvc = ofdm.fbmc_remove_preamble_vcvc(total_subc, config.frame_data_part, 3*total_subc)
    self.subchannel_processing_vcvc = ofdm.fbmc_subchannel_processing_vcvc(total_subc, config.frame_data_part, (preamble), 2)
    self.oqam_postprocessing_vcvc = ofdm.fbmc_oqam_postprocessing_vcvc(total_subc, 0, 0)
    
    log_to_file( self, ofdm_blocks, "data/PRE_FBMC.compl" )
    log_to_file( self, self.fft_fbmc, "data/FFT_FBMC.compl" )
    
    help2 = blocks.keep_one_in_n(gr.sizeof_gr_complex*total_subc,23)
    self.connect ((self.subchannel_processing_vcvc,1),help2)

    
    #terminate_stream(self, help2)
    

    self.connect(ofdm_blocks, blocks.vector_to_stream(gr.sizeof_gr_complex, fft_length/2),overlap_ser_to_par)
    self.connect(overlap_ser_to_par, self.separate_vcvc)
    self.connect((self.separate_vcvc, 1), (self.polyphase_network_vcvc_2, 0))
    self.connect((self.separate_vcvc, 0), (self.polyphase_network_vcvc_1, 0))
    self.connect((self.polyphase_network_vcvc_1, 0), (self.junction_vcvc, 0))
    self.connect((self.polyphase_network_vcvc_2, 0), (self.junction_vcvc, 1))
    self.connect(self.junction_vcvc, self.fft_fbmc)
    
    ofdm_blocks = self.fft_fbmc
    
    
    if fft_length > data_subc:
      subcarrier_mask_fbmc = ofdm.vector_mask( fft_length, virtual_subc/2,
                                           total_subc, [] )
      self.connect( self.fft_fbmc, subcarrier_mask_fbmc )
      ofdm_blocks = subcarrier_mask_fbmc
      #log_to_file(self, ofdm_blocks, "data/vec_mask.compl")
       ## Least Squares estimator for channel transfer function (CTF)
      #log_to_file( self, subcarrier_mask, "data/OFDM_Blocks.compl" )
    
    
    self.connect(ofdm_blocks, self.multiply_const)
    self.connect(self.multiply_const, self.beta_multiplier_vcvc)
    self.connect((self.beta_multiplier_vcvc, 0), (self.skiphead, 0))
    self.connect((self.skiphead, 0), (self.subchannel_processing_vcvc, 0))
    self.connect((self.subchannel_processing_vcvc, 0), (self.remove_preamble_vcvc, 0))
    self.connect((self.remove_preamble_vcvc, 0), (self.skiphead_1, 0))
    self.connect((self.skiphead_1, 0), (self.oqam_postprocessing_vcvc, 0))
    
    ofdm_blocks = self.oqam_postprocessing_vcvc
    
    log_to_file( self, self.skiphead, "data/SKIP_HEAD_FBMC.compl" )
    log_to_file( self, self.oqam_postprocessing_vcvc, "data/REC_OUT_FBMC.compl" )
        
    

    
    
    
    
    
    
    #TAKING THE CHANNEL ESTIMATION PREAMBLE
    chest_pre_trigger = blocks.delay( gr.sizeof_char, 3 )
    sampled_chest_preamble = ofdm.vector_sampler( gr.sizeof_gr_complex * fft_length/2, 2 )
      
    self.connect( frame_start,       chest_pre_trigger )
    self.connect( chest_pre_trigger, ( sampled_chest_preamble, 1 ) )
    self.connect( frequency_shift,       ( sampled_chest_preamble, 0 ) )
    #ofdm_blocks = sampled_chest_preamble
    
        
    ## FFT
    fft = fft_blocks.fft_vcc( fft_length, True, [], True )
    self.connect( sampled_chest_preamble, fft )
    ofdm_blocks_est = fft
    log_to_file( self, sampled_chest_preamble, "data/SAMPLED_EST_PREAMBLE.compl" )
    log_to_file( self, ofdm_blocks_est, "data/FFT.compl" )
    
    
    ## Remove virtual subcarriers
    if fft_length > data_subc:
      subcarrier_mask = ofdm.vector_mask( fft_length, virtual_subc/2,
                                           total_subc, [] )
      self.connect( ofdm_blocks_est, subcarrier_mask )
      ofdm_blocks_est = subcarrier_mask
      #log_to_file(self, ofdm_blocks, "data/vec_mask.compl")
       ## Least Squares estimator for channel transfer function (CTF)
      log_to_file( self, subcarrier_mask, "data/OFDM_Blocks.compl" )
    
          
    ## post-FFT processing
      
    
    
    ## extract channel estimation preamble from frame
    ##chest_pre_trigger = blocks.delay( gr.sizeof_char, 
                                  ##1 )
    ##sampled_chest_preamble = \
     ## ofdm.vector_sampler( gr.sizeof_gr_complex * total_subc, 1 )
    ##self.connect( frame_start,       chest_pre_trigger )
    ##self.connect( chest_pre_trigger, ( sampled_chest_preamble, 1 ) )
    ##self.connect( ofdm_blocks,       ( sampled_chest_preamble, 0 ) )
    

    
    ## Least Squares estimator for channel transfer function (CTF)
    inv_preamble_fd = numpy.array( block_header.pilotsym_fd[ 
        block_header.channel_estimation_pilot[0] ] )
    #print "Channel estimation pilot: ", inv_preamble_fd
    inv_preamble_fd = 1. / inv_preamble_fd
    
    LS_channel_estimator = ofdm.multiply_const_vcc( list( inv_preamble_fd ) )
    self.connect( ofdm_blocks_est, LS_channel_estimator )
    estimated_CTF = LS_channel_estimator
    terminate_stream(self,estimated_CTF)
    
    if options.logcir:
         log_to_file( self, sampled_chest_preamble, "data/PREAM.compl" )
     
    
    if not options.disable_ctf_enhancer:
      
      
      if options.logcir:
        ifft1 = fft_blocks.fft_vcc(total_subc,False,[],True)
        self.connect( estimated_CTF, ifft1,gr.null_sink(gr.sizeof_gr_complex*total_subc))
        summ1 = ofdm.vector_sum_vcc(total_subc)
        c2m =gr.complex_to_mag(total_subc)
        self.connect( estimated_CTF,summ1 ,gr.null_sink(gr.sizeof_gr_complex))
        self.connect( estimated_CTF, c2m,gr.null_sink(gr.sizeof_float*total_subc))
        log_to_file( self, ifft1, "data/CIR1.compl" )
        log_to_file( self, summ1, "data/CTFsumm1.compl" )
        log_to_file( self, estimated_CTF, "data/CTF1.compl" )
        log_to_file( self, c2m, "data/CTFmag1.float" )
        
      ## MSE enhancer
      ctf_mse_enhancer = ofdm.CTF_MSE_enhancer( total_subc, cp_length + cp_length)
      self.connect( estimated_CTF, ctf_mse_enhancer )
#      log_to_file( self, ctf_mse_enhancer, "data/ctf_mse_enhancer_original.compl")
      #ifft3 = fft_blocks.fft_vcc(total_subc,False,[],True)
      #null_noise = ofdm.noise_nulling(total_subc, cp_length + cp_length)
      #ctf_mse_enhancer = fft_blocks.fft_vcc(total_subc,True,[],True)
      #ctf_mse_enhancer = ofdm.vector_mask( fft_length, virtual_subc/2,
                                          # total_subc, [] )
      #self.connect( estimated_CTF, ifft3,null_noise,ctf_mse_enhancer )
        
      estimated_CTF = ctf_mse_enhancer 
      print "Disabled CTF MSE enhancer"

      if options.logcir:
         ifft2 = fft_blocks.fft_vcc(total_subc,False,[],True)
         self.connect( estimated_CTF, ifft2,gr.null_sink(gr.sizeof_gr_complex*total_subc))
         summ2 = ofdm.vector_sum_vcc(total_subc)
         c2m2 =gr.complex_to_mag(total_subc)
         self.connect( estimated_CTF,summ2 ,gr.null_sink(gr.sizeof_gr_complex))
         self.connect( estimated_CTF, c2m2,gr.null_sink(gr.sizeof_float*total_subc))
         log_to_file( self, ifft2, "data/CIR2.compl" )
         log_to_file( self, summ2, "data/CTFsumm2.compl" )
         log_to_file( self, estimated_CTF, "data/CTF2.compl" )
         log_to_file( self, c2m2, "data/CTFmag2.float" )
         
    ## Postprocess the CTF estimate
    ## CTF -> inverse CTF (for equalizer)
    ## CTF -> norm |.|^2 (for CTF display)
    ctf_postprocess = ofdm.postprocess_CTF_estimate( total_subc )
    
    self.connect( help2, ctf_postprocess )
    inv_estimated_CTF = ( ctf_postprocess, 0 )
    disp_CTF = ( ctf_postprocess, 1 )
    terminate_stream(self, inv_estimated_CTF)
    
    if options.disable_equalization or options.ideal:
      terminate_stream(self, inv_estimated_CTF)
      inv_estimated_CTF_vec = blocks.vector_source_c([1.0/fft_length*math.sqrt(total_subc)]*total_subc,True,total_subc)
      inv_estimated_CTF_str = blocks.vector_to_stream(gr.sizeof_gr_complex, total_subc)
      self.inv_estimated_CTF_mul = ofdm.multiply_const_ccf( 1.0/config.rms_amplitude )
      #inv_estimated_CTF_mul.set_k(1.0/config.rms_amplitude)
      inv_estimated_CTF = blocks.stream_to_vector(gr.sizeof_gr_complex, total_subc)
      self.connect( inv_estimated_CTF_vec, inv_estimated_CTF_str, self.inv_estimated_CTF_mul, inv_estimated_CTF)
      print "Disabled equalization stage"
      '''
## LMS Phase tracking
    ## Track residual frequency offset and sampling clock frequency offset

    nondata_blocks = []
    for i in range(config.frame_length):
      if i in config.training_data.pilotsym_pos:
        nondata_blocks.append(i)
        
    print"\t\t\t\t\tnondata_blocks=",nondata_blocks
    pilot_subc = block_header.pilot_tones
    pilot_subcarriers = block_header.pilot_subc_sym
    print "PILOT SUBCARRIERS: ", pilot_subcarriers
        
    phase_tracking = ofdm.lms_phase_tracking_03( total_subc, pilot_subc,
                                               nondata_blocks, pilot_subcarriers,0 )
    self.connect( ofdm_blocks, ( phase_tracking, 0 ) )
    self.connect( inv_estimated_CTF, ( phase_tracking, 1 ) )
    self.connect( frame_start, ( phase_tracking, 2 ) ) ##
    
    if options.scatter_plot_before_phase_tracking:
      self.before_phase_tracking = equalizer
      
    
    if options.disable_phase_tracking or options.ideal:
      terminate_stream(self, phase_tracking)
      print "Disabled phase tracking stage"
    else:
      ofdm_blocks = phase_tracking
    '''
    ## Channel Equalizer
    ##equalizer = ofdm.channel_equalizer( total_subc )
    ##self.connect( ofdm_blocks,       ( equalizer, 0 ) )
    ##self.connect( inv_estimated_CTF, ( equalizer, 1 ) )
    ##self.connect( frame_start,       ( equalizer, 2 ) )
    ##ofdm_blocks = equalizer
    #log_to_file(self, equalizer,"data/equalizer_siso.compl")
    
    
    #log_to_file(self, ofdm_blocks, "data/equalizer.compl")

    ## LMS Phase tracking
    ## Track residual frequency offset and sampling clock frequency offset

    nondata_blocks = []
    for i in range(config.frame_length):
      if i in config.training_data.pilotsym_pos:
        nondata_blocks.append(i)
        
    print"\t\t\t\t\tnondata_blocks=",nondata_blocks
    pilot_subc = block_header.pilot_tones
    pilot_subcarriers = block_header.pilot_subc_sym
    print "PILOT SUBCARRIERS: ", pilot_subcarriers
    
    if options.scatter_plot_before_phase_tracking:
      self.before_phase_tracking = equalizer
        

    ## Output connections

    self.connect( ofdm_blocks, out_ofdm_blocks )
    self.connect( frame_start, out_frame_start )
    self.connect( disp_CTF, out_disp_ctf )
    
    

    if log:
      log_to_file( self, sc_metric, "data/sc_metric.float" )
      log_to_file( self, gi_metric, "data/gi_metric.float" )
      log_to_file( self, morelli_foe, "data/morelli_foe.float" )
      log_to_file( self, lms_fir, "data/lms_fir.float" )
      log_to_file( self, sampler_preamble, "data/preamble.compl" )
      log_to_file( self, sync, "data/sync.compl" )
      log_to_file( self, frequency_shift, "data/frequency_shift.compl" )
      log_to_file( self, fft, "data/fft.compl")
      log_to_file( self, fft, "data/fft.float", mag=True )
      
      if vars().has_key( 'subcarrier_mask' ):
        log_to_file( self, subcarrier_mask, "data/subcarrier_mask.compl" )
      
      log_to_file( self, ofdm_blocks, "data/ofdm_blocks_out.compl" )
      log_to_file( self, frame_start, "data/frame_start.float", 
                   char_to_float=True )
      
      log_to_file( self, sampled_chest_preamble, 
                   "data/sampled_chest_preamble.compl" )
      log_to_file( self, LS_channel_estimator, 
                   "data/ls_channel_estimator.compl" )
      log_to_file( self, LS_channel_estimator, 
                   "data/ls_channel_estimator.float", mag=True )
      
      if "ctf_mse_enhancer" in locals(): 
        log_to_file( self, ctf_mse_enhancer, "data/ctf_mse_enhancer.compl" )
        log_to_file( self, ctf_mse_enhancer, "data/ctf_mse_enhancer.float", 
                     mag=True )
      
      log_to_file( self, (ctf_postprocess,0), "data/inc_estimated_ctf.compl" )
      log_to_file( self, (ctf_postprocess,1), "data/disp_ctf.float" )
      
      log_to_file( self, equalizer, "data/equalizer.compl" )
      log_to_file( self, equalizer, "data/equalizer.float", mag=True )
      
      log_to_file( self, phase_tracking, "data/phase_tracking.compl" )
      
    
      
    
  def add_options( normal, expert ):
    
    normal.add_option( "", "--disable-ctf-enhancer",
                       action="store_true",
                       default=False,
                       help="Disable Enhancing the MSE of CTF")
    
    expert.add_option( "", "--disable-freq-sync",
                       action="store_true",
                       default=False,
                       help="Disabling frequency synchronization stage")
    
    expert.add_option( "", "--disable-equalization",
                       action="store_true",
                       default=False,
                       help="Disabling equalization stage")
    
    expert.add_option( "", "--disable-phase-tracking",
                       action="store_true",
                       default=False,
                       help="Disabling phase tracking stage")
    
    expert.add_option( "", "--disable-time-sync",
                       action="store_true",
                       default=False,
                       help="Disabling time synchronization stage")
    expert.add_option( "", "--logcir",
                       action="store_true",
                       default=False,
                       help="CIR log")
    expert.add_option( "", "--ideal",
                       action="store_true",
                       default=False,
                       help="Disabling inner receiver estimations")
    
    
  add_options = staticmethod(add_options)
