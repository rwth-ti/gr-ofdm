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

from gnuradio import gr, blocks, zeromq, filter
from gnuradio import fft as fft_blocks
from gnuradio.eng_option import eng_option

from optparse import OptionParser
from gr_tools import log_to_file,terminate_stream

import ofdm as ofdm
from preambles import fbmc_inner_pilot_block_filter
import numpy
import math

import schmidl

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
        gr.io_signaturev(
            4, 4,
            [gr.sizeof_float * total_subc,    # Normalized |CTF|^2 
            gr.sizeof_char,                       # Frame start
            gr.sizeof_gr_complex * total_subc, # OFDM blocks, SNR est
            gr.sizeof_float] ) )      # CFO
    
    
    ## Input and output ports
    self.input = rx_input = self
    
    out_ofdm_blocks = ( self, 2 )
    out_frame_start = ( self, 1 )
    out_disp_ctf    = ( self, 0 )
    out_disp_cfo    = ( self, 3 )
    #out_snr_pream    = ( self, 3 )
    
    
    
    
    ## pre-FFT processing
    
    '''
    ## Compute autocorrelations for S&C preamble
    ## and cyclic prefix
    
    self._sc_metric = sc_metric = autocorrelator( fft_length/2, fft_length/2 )
    self._gi_metric = gi_metric = autocorrelator( fft_length, cp_length )
    
    self.connect( rx_input, sc_metric )
    self.connect( rx_input, gi_metric )
    terminate_stream(self, gi_metric)
    
    ## Sync. Output contains OFDM blocks
    sync = ofdm.time_sync( fft_length/2, 1)
    self.connect( rx_input, ( sync, 0 ) )
    self.connect( sc_metric, ( sync, 1 ) )
    self.connect( sc_metric, ( sync, 2 ) )
    
    ofdm_blocks = ( sync, 0 )
    frame_start = ( sync, 1 )
    log_to_file( self, ( sync, 1 ), "data/fbmc_peak_detector.char" )
    '''
    if options.ideal is False and options.ideal2 is False:
        #Testing old/new metric
        self.tm = schmidl.recursive_timing_metric(2*fft_length)
        self.connect( self.input, self.tm)
        #log_to_file( self, self.tm, "data/fbmc_rec_sc_metric_ofdm.float" )
        
        timingmetric_shift = 0 #-2 #int(-cp_length * 0.8)
        tmfilter = filter.fft_filter_fff(1, [2./fft_length]*(fft_length/2))# ofdm.lms_fir_ff( fft_length, 1e-3 ) #; filter.fir_filter_fff(1, [1./fft_length]*fft_length)
        self.connect( self.tm, tmfilter )
        self.tm = tmfilter
        #log_to_file( self, self.tm, "data/fbmc_rec_sc_metric_ofdm2.float" )
        
        self._pd_thres = 0.6
        self._pd_lookahead = fft_length # empirically chosen
        peak_detector = ofdm.peak_detector_02_fb(self._pd_lookahead, self._pd_thres)
        self.connect(self.tm, peak_detector)
        #log_to_file( self, peak_detector, "data/fbmc_rec_peak_detector.char" )
        
        
        #frame_start = [0]*frame_length
        #frame_start[0] = 1
        #frame_start = blocks.vector_source_b(frame_start,True)
        
        #OLD
        #delayed_timesync = blocks.delay(gr.sizeof_char,
         #                           (frame_length-10)*fft_length/2 - fft_length/4 -1 + timingmetric_shift)
        delayed_timesync = blocks.delay(gr.sizeof_char,
                                    (frame_length-10)*fft_length/2 - fft_length/4  + int(2.5*fft_length)  + timingmetric_shift-1)
        #delayed_timesync = blocks.delay(gr.sizeof_char,
                                    #(frame_length-10)*fft_length/2 - fft_length/4 + int(3.5*fft_length)  + timingmetric_shift-1)
        self.connect( peak_detector, delayed_timesync )
        
        self.block_sampler = ofdm.vector_sampler(gr.sizeof_gr_complex,fft_length/2*frame_length)
        
        self.connect(self.input,self.block_sampler)
        self.connect(delayed_timesync,(self.block_sampler,1))
        #log_to_file( self, self.block_sampler, "data/fbmc_block_sampler.compl" )
        
        vt2s = blocks.vector_to_stream(gr.sizeof_gr_complex*fft_length,
                                                frame_length/2)
        self.connect(self.block_sampler,vt2s)
        #terminate_stream(self,ofdm_blocks)
        
        ofdm_blocks = vt2s
        
        '''
        # TODO: dynamic solution
        vt2s = blocks.vector_to_stream(gr.sizeof_gr_complex*block_length/2,
                                                frame_length)
        self.connect(self.block_sampler,vt2s)
        terminate_stream(self,( sync, 0 ))
        ofdm_blocks = vt2s
        '''
        
        
        
        
        
        ##stv_help = blocks.stream_to_vector(gr.sizeof_gr_complex*config.fft_length/2, 1)
        #stv_help = blocks.vector_to_stream(gr.sizeof_gr_complex*config.fft_length/2, 2)
       ##self.connect(ofdm_blocks, stv_help)
        ##ofdm_blocks = stv_help
        #ofdm_blocks = ( sync, 0 )
        #frame_start = ( sync, 1 )
        #log_to_file(self, frame_start, "data/frame_start.compl")
        
        #log_to_file( self, sc_metric, "data/sc_metric.float" )
        #log_to_file( self, gi_metric, "data/gi_metric.float" )
        #log_to_file( self, (sync,1), "data/sync.float" )
        
    #    log_to_file(self,ofdm_blocks,"data/ofdm_blocks_original.compl")
        frame_start = [0]*int(frame_length/2)
        frame_start[0] = 1
        frame_start = blocks.vector_source_b(frame_start,True)          
        
        #frame_start2 = [0]*int(frame_length/2)
        #frame_start2[0] = 1
        #frame_start2 = blocks.vector_source_b(frame_start2,True)
    
    if options.disable_time_sync or options.ideal or options.ideal2:
      if options.ideal is False and options.ideal2 is False:
        terminate_stream(self, ofdm_blocks)
        terminate_stream(self, frame_start)
      
      serial_to_parallel = blocks.stream_to_vector(gr.sizeof_gr_complex,fft_length)
      #discard_cp = ofdm.vector_mask(block_length,cp_length,fft_length,[])
      #serial_to_parallel = blocks.stream_to_vector(gr.sizeof_gr_complex,block_length)
      #discard_cp = ofdm.vector_mask(block_length,cp_length,fft_length,[])
      #self.connect( rx_input,serial_to_parallel)
      
      #self.connect( rx_input, blocks.delay(gr.sizeof_gr_complex,0),serial_to_parallel)
      initial_skip = blocks.skiphead(gr.sizeof_gr_complex,2*fft_length)
      self.connect( rx_input, initial_skip)
      if options.ideal is False and options.ideal2 is False:          
          self.connect(  initial_skip, serial_to_parallel)
          ofdm_blocks = serial_to_parallel
      else:
          ofdm_blocks = initial_skip
      #self.connect( rx_input, serial_to_parallel, discard_cp )
      
      frame_start = [0]*int(frame_length/2)
      frame_start[0] = 1
      frame_start = blocks.vector_source_b(frame_start,True)
      
      #frame_start2 = [0]*int(frame_length/2)
      #frame_start2[0] = 1
      #frame_start2 = blocks.vector_source_b(frame_start2,True)
      
      print "Disabled time synchronization stage"
    
    print"\t\t\t\t\tframe_length = ",frame_length
    
    if options.ideal is False and options.ideal2 is False:
        ## Extract preamble, feed to Morelli & Mengali frequency offset estimator
        assert( block_header.mm_preamble_pos == 0 )
        morelli_foe = ofdm.mm_frequency_estimator( fft_length, 2, 1, config.fbmc )
        sampler_preamble = ofdm.vector_sampler( gr.sizeof_gr_complex * fft_length,
                                                1 )
        self.connect( ofdm_blocks, ( sampler_preamble, 0 ) )
        self.connect( frame_start, blocks.delay( gr.sizeof_char, 1 ), ( sampler_preamble, 1 ) )
        self.connect( sampler_preamble, morelli_foe )
        freq_offset = morelli_foe
        print "FRAME_LENGTH: ", frame_length
        #log_to_file( self, sampler_preamble, "data/sampler_preamble.compl" )
        #log_to_file( self, rx_input, "data/rx_input.compl" )
        #log_to_file( self, ofdm_blocks, "data/rx_input.compl" )

        
        #Extracting preamble for SNR estimation
        #fft_snr_est = fft_blocks.fft_vcc( fft_length, True, [], True )
        #self.connect( sampler_preamble, blocks.stream_to_vector(gr.sizeof_gr_complex*fft_length/2, 2),  fft_snr_est )
        
        
        ## Remove virtual subcarriers
        #if fft_length > data_subc:
          #subcarrier_mask_snr_est = ofdm.vector_mask( fft_length, virtual_subc/2,
                        #                       total_subc, [] )
          #self.connect( fft_snr_est, subcarrier_mask_snr_est )
          #fft_snr_est = subcarrier_mask_snr_est
          #log_to_file(self, ofdm_blocks, "data/vec_mask.compl")
           ## Least Squares estimator for channel transfer function (CTF)
        
        #self.connect( fft_snr_est, out_snr_pream ) # Connecting to output
        
        ## Adaptive LMS FIR filtering of frequency offset
        lms_fir = ofdm.lms_fir_ff( 20, 1e-3 ) # TODO: verify parameter choice
        self.connect( freq_offset, lms_fir )
        freq_offset = lms_fir
        
        self.connect(freq_offset, blocks.keep_one_in_n(gr.sizeof_float,20) ,out_disp_cfo)
    else:
        self.connect(blocks.vector_source_f ([1]) ,out_disp_cfo)

    
    #log_to_file(self, lms_fir, "data/lms_fir.float")
    
    if options.disable_freq_sync or options.ideal or options.ideal2:
      if options.ideal is False and options.ideal2 is False:  
          terminate_stream(self, freq_offset)
          freq_offset = blocks.vector_source_f([0.0],True)
      print "Disabled frequency synchronization stage"
    
    if options.ideal is False and options.ideal2 is False:
        ## Correct frequency shift, feed-forward structure
        frequency_shift = ofdm.frequency_shift_vcc( fft_length, -1.0/fft_length,
                                                    0)
        
        #freq_shift = blocks.multiply_cc()
        #norm_freq = -0.1 / config.fft_length
        #freq_off = self.freq_off_src = analog.sig_source_c(1.0, analog.GR_SIN_WAVE, norm_freq, 1.0, 0.0 )
        
        self.connect( ofdm_blocks, ( frequency_shift, 0 ) )
        self.connect( freq_offset, ( frequency_shift, 1 ) )
        self.connect( frame_start,blocks.delay( gr.sizeof_char, 0), ( frequency_shift, 2 ) )
        
        

        
        #self.connect(frequency_shift,s2help)
        #ofdm_blocks = s2help
        ofdm_blocks = frequency_shift
    #terminate_stream(self, frequency_shift)
    
    
    
    #inner_pb_filt = self._inner_pilot_block_filter = fbmc_inner_pilot_block_filter()
    #self.connect(ofdm_blocks,inner_pb_filt)
    #self.connect(frame_start,(inner_pb_filt,1))
    #self.connect((inner_pb_filt,1),blocks.null_sink(gr.sizeof_char))
    
    #ofdm_blocks = (inner_pb_filt,0)
    
    
    overlap_ser_to_par = ofdm.fbmc_overlapping_serial_to_parallel_cvc(fft_length)
    self.separate_vcvc = ofdm.fbmc_separate_vcvc(fft_length, 2)
    self.polyphase_network_vcvc_1 = ofdm.fbmc_polyphase_network_vcvc(fft_length, 4, 4*fft_length-1, True)
    self.polyphase_network_vcvc_2 = ofdm.fbmc_polyphase_network_vcvc(fft_length, 4, 4*fft_length-1, True)
    self.junction_vcvc = ofdm.fbmc_junction_vcvc(fft_length, 2)
    self.fft_fbmc = fft_blocks.fft_vcc(fft_length, True, [], True)
    
    print "config.training_data.fbmc_no_preambles: ", config.training_data.fbmc_no_preambles
    #center_preamble = [1, -1j, -1, 1j]
    
    #self.preamble = preamble = [0]*total_subc + center_preamble*((int)(total_subc/len(center_preamble)))+[0]*total_subc
    
    self.preamble = preamble = config.training_data.fbmc_pilotsym_fd_list
    #inv_preamble = 1. / numpy.array(self.preamble)
    #print "self.preamble: ", len(self.preamble
    #print "inv_preamble: ", list(inv_preamble)
    
    #print "self.preamble", self.preamble
    #print "self.preamble2", self.preamble2
    
    
    self.multiply_const= ofdm.multiply_const_vcc(([1.0/(math.sqrt(fft_length*0.6863))]*total_subc))    
    self.beta_multiplier_vcvc = ofdm.fbmc_beta_multiplier_vcvc(total_subc, 4, 4*fft_length-1, 0)
    #self.skiphead = blocks.skiphead(gr.sizeof_gr_complex*total_subc, 2*4-1-1)
    self.skiphead = blocks.skiphead(gr.sizeof_gr_complex*total_subc,2)
    self.skiphead_1 = blocks.skiphead(gr.sizeof_gr_complex*total_subc, 0)
    #self.remove_preamble_vcvc = ofdm.fbmc_remove_preamble_vcvc(total_subc, config.frame_data_part/2, config.training_data.fbmc_no_preambles*total_subc/2)
    #self.subchannel_processing_vcvc = ofdm.fbmc_subchannel_processing_vcvc(total_subc, config.frame_data_part, 1, 2, 1, 0)
    self.oqam_postprocessing_vcvc = ofdm.fbmc_oqam_postprocessing_vcvc(total_subc, 0, 0)
    
    #log_to_file( self, ofdm_blocks, "data/PRE_FBMC.compl" )
    #log_to_file( self, self.fft_fbmc, "data/FFT_FBMC.compl" )

    if options.ideal is False and options.ideal2 is False:
        self.subchannel_processing_vcvc = ofdm.fbmc_subchannel_processing_vcvc(total_subc, config.frame_data_part, 3, 2, 1, 0)
        help2 = blocks.keep_one_in_n(gr.sizeof_gr_complex*total_subc,frame_length)
        self.connect ((self.subchannel_processing_vcvc,1),help2)
        #log_to_file( self, self.subchannel_processing_vcvc, "data/fbmc_subc.compl" )

    
    #terminate_stream(self, help2)
    
    if options.ideal is False and options.ideal2 is False:
        self.connect(ofdm_blocks, blocks.vector_to_stream(gr.sizeof_gr_complex, fft_length),overlap_ser_to_par)
    else:
        self.connect(ofdm_blocks,overlap_ser_to_par)
        
    self.connect(overlap_ser_to_par, self.separate_vcvc)
    self.connect((self.separate_vcvc, 1), (self.polyphase_network_vcvc_2, 0))
    self.connect((self.separate_vcvc, 0), (self.polyphase_network_vcvc_1, 0))
    self.connect((self.polyphase_network_vcvc_1, 0), (self.junction_vcvc, 0))
    self.connect((self.polyphase_network_vcvc_2, 0), (self.junction_vcvc, 1))
    self.connect(self.junction_vcvc, self.fft_fbmc)
    
    ofdm_blocks = self.fft_fbmc
    print "config.dc_null: ", config.dc_null
    if fft_length > data_subc:
      subcarrier_mask_fbmc = ofdm.vector_mask_dc_null( fft_length, virtual_subc/2,
                                           total_subc, config.dc_null, [] )
      self.connect( ofdm_blocks, subcarrier_mask_fbmc )
      ofdm_blocks = subcarrier_mask_fbmc
      #log_to_file(self, ofdm_blocks, "data/vec_mask.compl")
       ## Least Squares estimator for channel transfer function (CTF)
      #log_to_file( self, subcarrier_mask, "data/OFDM_Blocks.compl" )
      
    
    self.connect(ofdm_blocks, self.beta_multiplier_vcvc)
    
    ofdm_blocks = self.beta_multiplier_vcvc
    #self.connect(ofdm_blocks,self.multiply_const)
    #self.connect(self.multiply_const, (self.skiphead, 0))
    
    self.connect(ofdm_blocks, (self.skiphead, 0))
    #log_to_file( self, self.skiphead, "data/fbmc_skiphead_4.compl" )
    
    
    #self.connect(ofdm_blocks, self.multiply_const)
    #self.connect(self.multiply_const, self.beta_multiplier_vcvc)
    #self.connect((self.beta_multiplier_vcvc, 0), (self.skiphead, 0))
    if options.ideal or options.ideal2:
        self.connect((self.skiphead, 0),(self.skiphead_1, 0))
    else:
        self.connect((self.skiphead, 0), (self.subchannel_processing_vcvc, 0))
        self.connect((self.subchannel_processing_vcvc, 0), (self.skiphead_1, 0))
        
    #log_to_file( self, self.skiphead, "data/fbmc_subc.compl" )    
    #self.connect((self.skiphead_1, 0),(self.remove_preamble_vcvc, 0))
    #self.connect((self.remove_preamble_vcvc, 0),  (self.oqam_postprocessing_vcvc, 0))
    
    #ofdm_blocks = self.oqam_postprocessing_vcvc
    #log_to_file( self, self.subchannel_processing_vcvc, "data/subc_0.compl" )
    #log_to_file( self, (self.subchannel_processing_vcvc,1), "data/subc_1.compl" )
    
    
    
    self.connect((self.skiphead_1, 0),(self.oqam_postprocessing_vcvc, 0))
    #self.connect((self.oqam_postprocessing_vcvc, 0), (self.remove_preamble_vcvc, 0) )
    
    ofdm_blocks = (self.oqam_postprocessing_vcvc, 0)#(self.remove_preamble_vcvc, 0)
    #log_to_file( self, (self.oqam_postprocessing_vcvc, 0), "data/fbmc_before_remove.compl" )
    
    #log_to_file( self, self.skiphead, "data/SKIP_HEAD_FBMC.compl" )
    #log_to_file( self, self.beta_multiplier_vcvc, "data/BETA_REC_FBMC.compl" )
    #log_to_file( self, self.oqam_postprocessing_vcvc, "data/REC_OUT_FBMC.compl" )
        
    

    
    
    
    
    
    """ DISABLED OFDM CHANNEL ESTIMATION PREMBLE -> CORRECT LATER to compare FBMC and OFDM channel estimation
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
    """
    if options.ideal is False and options.ideal2 is False:
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
        ctf_postprocess = ofdm.fbmc_postprocess_CTF_estimate( total_subc )
        
        self.connect( help2, ctf_postprocess )
        #estimated_SNR = ( ctf_postprocess, 0 )
        disp_CTF = ( ctf_postprocess, 0 )
        #self.connect(estimated_SNR,out_snr_pream)
        #log_to_file( self, estimated_SNR, "data/fbmc_SNR.float" )
        
        #Disable measured SNR output
        #terminate_stream(self, estimated_SNR)
        #self.connect(blocks.vector_source_f([10.0],True) ,out_snr_pream)
    
#     if options.disable_equalization or options.ideal:
#       terminate_stream(self, inv_estimated_CTF)
#       inv_estimated_CTF_vec = blocks.vector_source_c([1.0/fft_length*math.sqrt(total_subc)]*total_subc,True,total_subc)
#       inv_estimated_CTF_str = blocks.vector_to_stream(gr.sizeof_gr_complex, total_subc)
#       self.inv_estimated_CTF_mul = ofdm.multiply_const_ccf( 1.0/config.rms_amplitude )
#       #inv_estimated_CTF_mul.set_k(1.0/config.rms_amplitude)
#       inv_estimated_CTF = blocks.stream_to_vector(gr.sizeof_gr_complex, total_subc)
#       self.connect( inv_estimated_CTF_vec, inv_estimated_CTF_str, self.inv_estimated_CTF_mul, inv_estimated_CTF)
#       print "Disabled equalization stage"
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
    if options.ideal is False and options.ideal2 is False:
        self.connect( disp_CTF, out_disp_ctf )
    else:
        self.connect( blocks.vector_source_f([1.0]*total_subc),blocks.stream_to_vector(gr.sizeof_float,total_subc), out_disp_ctf )
    
    

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
