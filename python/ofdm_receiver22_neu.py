#!/usr/bin/env python

from gnuradio import gr
from gnuradio.eng_option import eng_option

from optparse import OptionParser
from gr_tools import log_to_file,terminate_stream

import ofdm as ofdm
import numpy
import math
from numpy import concatenate

from autocorrelator import autocorrelator
from station_configuration import station_configuration


class ofdm_inner_receiver( gr.hier_block2 ):
  def __init__( self, options, log = False ):
    
    ## Read configuration
    config = station_configuration()
    
    fft_length    = config.fft_length
    cp_length     = config.cp_length
    block_header  = config.training_data
    data_subc     = config.data_subcarriers
    virtual_subc  = config.virtual_subcarriers
    total_subc    = config.subcarriers
    block_length  = config.block_length
    frame_length  = config.frame_length
    
    L             = block_header.mm_periodic_parts
    
    frame_data_blocks    = options.data_blocks
    
    
    ## Set Input/Output signature
    gr.hier_block2.__init__( self, 
        "ofdm_inner_receiver",
        gr.io_signature(
            2, 2,
            gr.sizeof_gr_complex ),
        gr.io_signature5(
            5, 5,
            gr.sizeof_gr_complex * total_subc,    # OFDM blocks
            gr.sizeof_char,                       # Frame start
            gr.sizeof_float * total_subc,         # Normalized |CTF|^2
            gr.sizeof_char,                       # Frame start
            gr.sizeof_float * total_subc ) )      # Normalized |CTF|^2
    
    
    ## Input and output ports
    self.input  = rx_input = (self,0)
    self.input2 = rx2_input = (self,1)
    
    out_ofdm_blocks = ( self, 0 )
    out_frame_start = ( self, 1 )
    out_disp_ctf    = ( self, 2 )
    out_frame_start2 = ( self, 3 )
    out_disp_ctf2    = ( self, 4 )
    
    ## pre-FFT processing
    
    
    ## Compute autocorrelations for S&C preamble
    ## and cyclic prefix
    sc_metric = autocorrelator( fft_length/2, fft_length/2 )
    gi_metric = autocorrelator( fft_length, cp_length )
    
    self.connect( rx_input, sc_metric )
    self.connect( rx_input, gi_metric )
    
    sc_metric2 = autocorrelator( fft_length/2, fft_length/2 )
    gi_metric2 = autocorrelator( fft_length, cp_length )
    
    self.connect( rx2_input, sc_metric2 )
    self.connect( rx2_input, gi_metric2 )
    
    ## Sync. Output contains OFDM blocks
    sync = ofdm.dominiks_sync_01( fft_length, cp_length )
    self.connect( rx_input, ( sync, 0 ) )
    self.connect( sc_metric, ( sync, 1 ) )
    self.connect( gi_metric, ( sync, 2 ) )
    ofdm_blocks = ( sync, 0 )
    frame_start = ( sync, 1 )
    
    sync2 = ofdm.dominiks_sync_01( fft_length, cp_length )
    self.connect( rx2_input, ( sync2, 0 ) )
    self.connect( sc_metric2, ( sync2, 1 ) )
    self.connect( gi_metric2, ( sync2, 2 ) )
    ofdm_blocks2 = ( sync2, 0 )
    frame_start2 = ( sync2, 1 )

    
    if options.disable_time_sync or options.ideal:
      terminate_stream(self, ofdm_blocks)
      terminate_stream(self, ofdm_blocks2)
      terminate_stream(self, frame_start)
      terminate_stream(self, frame_start2)
      
      serial_to_parallel = gr.stream_to_vector(gr.sizeof_gr_complex,block_length)
      serial_to_parallel2 = gr.stream_to_vector(gr.sizeof_gr_complex,block_length)
      discard_cp = ofdm.vector_mask(block_length,cp_length,fft_length,[])
      discard_cp2 = ofdm.vector_mask(block_length,cp_length,fft_length,[])
      ofdm_blocks = discard_cp
      ofdm_blocks2 = discard_cp2
      self.connect( rx_input, serial_to_parallel, discard_cp )
      self.connect( rx2_input, serial_to_parallel2, discard_cp2 )
      
      frame_start = [0]*frame_length
      frame_start[0] = 1
      frame_start = gr.vector_source_b(frame_start,True)
      frame_start2 = [0]*frame_length
      frame_start2[0] = 1
      frame_start2 = gr.vector_source_b(frame_start2,True)
      
      print "Disabled time synchronization stage"
    
    
    
    ## Extract preamble, feed to Morelli & Mengali frequency offset estimator
    assert( block_header.mm_preamble_pos == 0 )
    morelli_foe = ofdm.mm_frequency_estimator( fft_length, L )
    sampler_preamble = ofdm.vector_sampler( gr.sizeof_gr_complex * fft_length,
                                            1 )
    self.connect( ofdm_blocks, ( sampler_preamble, 0 ) )
    self.connect( frame_start, ( sampler_preamble, 1 ) )
    self.connect( sampler_preamble, morelli_foe )
    freq_offset = morelli_foe
    
    morelli_foe2 = ofdm.mm_frequency_estimator( fft_length, L )
    sampler_preamble2 = ofdm.vector_sampler( gr.sizeof_gr_complex * fft_length,
                                            1 )
    self.connect( ofdm_blocks2, ( sampler_preamble2, 0 ) )
    self.connect( frame_start2, ( sampler_preamble2, 1 ) )
    self.connect( sampler_preamble2, morelli_foe2 )
    freq_offset2 = morelli_foe2
    
    ## Adaptive LMS FIR filtering of frequency offset
    lms_fir = ofdm.lms_fir_ff( 20, 1e-3 ) # TODO: verify parameter choice
    self.connect( freq_offset, lms_fir )
    freq_offset = lms_fir
    
    lms_fir2 = ofdm.lms_fir_ff( 20, 1e-3 ) # TODO: verify parameter choice
    self.connect( freq_offset2, lms_fir2 )
    freq_offset2 = lms_fir2
    
#    log_to_file(self, lms_fir, "data/lms_fir.float")
#    log_to_file(self, lms_fir2, "data/lms_fir2.float")
    
    if options.disable_freq_sync or options.ideal:
       terminate_stream(self, freq_offset)
       terminate_stream(self, freq_offset2)
       freq_offset = gr.vector_source_f([0.0],True)
       freq_offset2 = gr.vector_source_f([0.0],True)
       print "Disabled frequency synchronization stage"
    
    ## Correct frequency shift, feed-forward structure
    frequency_shift = ofdm.frequency_shift_vcc( fft_length, -1.0/fft_length,
                                                cp_length )
    self.connect( ofdm_blocks, ( frequency_shift, 0 ) )
    self.connect( freq_offset, ( frequency_shift, 1 ) )
    self.connect( frame_start, ( frequency_shift, 2 ) )
    ofdm_blocks = frequency_shift
    
    frequency_shift2 = ofdm.frequency_shift_vcc( fft_length, -1.0/fft_length,
                                                cp_length )
    self.connect( ofdm_blocks2, ( frequency_shift2, 0 ) )
    self.connect( freq_offset2, ( frequency_shift2, 1 ) )
    self.connect( frame_start2, ( frequency_shift2, 2 ) )
    ofdm_blocks2 = frequency_shift2
    
    
    ## FFT
    fft = gr.fft_vcc( fft_length, True, [], True )
    self.connect( ofdm_blocks, fft )
    ofdm_blocks = fft
    
    fft2 = gr.fft_vcc( fft_length, True, [], True )
    self.connect( ofdm_blocks2, fft2 )
    ofdm_blocks2 = fft2
    
    ## Remove virtual subcarriers
    if fft_length > data_subc:
      subcarrier_mask = ofdm.vector_mask( fft_length, virtual_subc/2,
                                           total_subc, [] )
      self.connect( ofdm_blocks, subcarrier_mask )
      ofdm_blocks = subcarrier_mask
      
      subcarrier_mask2 = ofdm.vector_mask( fft_length, virtual_subc/2,
                                           total_subc, [] )
      self.connect( ofdm_blocks2, subcarrier_mask2 )
      ofdm_blocks2 = subcarrier_mask2
      
       ## Least Squares estimator for channel transfer function (CTF)
    
    
      # if options.logcir:
          # log_to_file( self, ofdm_blocks, "data/OFDM_Blocks.compl" )
          
          # inv_preamble_fd = numpy.array( block_header.pilotsym_fd[ 
            # block_header.channel_estimation_pilot[0] ] )
          # print "Channel estimation pilot: ", inv_preamble_fd
          # inv_preamble_fd = 1. / inv_preamble_fd
          # LS_channel_estimator0 = ofdm.multiply_const_vcc( list( inv_preamble_fd ) )
          # self.connect( ofdm_blocks, LS_channel_estimator0, gr.null_sink(gr.sizeof_gr_complex*total_subc))
          # log_to_file( self, LS_channel_estimator0, "data/OFDM_Blocks_eq.compl" )
          
    ## post-FFT processing
      
    
    if options.est_preamble==1:
        ## extract channel estimation preamble from frame
        chest_pre_trigger = gr.delay( gr.sizeof_char, 
                                      1 )
        sampled_chest_preamble = \
          ofdm.vector_sampler( gr.sizeof_gr_complex * total_subc, 1 )
        self.connect( frame_start,       chest_pre_trigger )
        self.connect( chest_pre_trigger, ( sampled_chest_preamble, 1 ) )
        self.connect( ofdm_blocks,       ( sampled_chest_preamble, 0 ) )
        
        chest_pre_trigger2 = gr.delay( gr.sizeof_char, 
                                      1 )
        sampled_chest_preamble2 = \
          ofdm.vector_sampler( gr.sizeof_gr_complex * total_subc, 1 )
        self.connect( frame_start2,       chest_pre_trigger2 )
        self.connect( chest_pre_trigger2, ( sampled_chest_preamble2, 1 ) )
        self.connect( ofdm_blocks2,       ( sampled_chest_preamble2, 0 ) )
        
        
        ## Least Squares estimator for channel transfer function (CTF)
        
        # Taking inverse for estimating h11 (h12)
        inv_preamble_fd_1 = numpy.array( block_header.pilotsym_fd_1[ 
            block_header.channel_estimation_pilot[0] ] )
        inv_preamble_fd_1 = inv_preamble_fd_1[0::2]
        
        # Taking inverse for estimating h21 (h22)
        inv_preamble_fd_2 = numpy.array( block_header.pilotsym_fd_2[ 
            block_header.channel_estimation_pilot[0] ] )
        inv_preamble_fd_2 = inv_preamble_fd_2[1::2]
        
        inv_preamble_fd_1 = 1. / inv_preamble_fd_1
        inv_preamble_fd_2 = 1. / inv_preamble_fd_2
        
        
        ## Least Squares estimator for channel transfer function (CTF)
        
       
        
        dd = []
        for i in range (total_subc/2):
            dd.extend([i*2])
            
        skip_block_1 = ofdm.int_skip(total_subc,2,0)
        skip_block_2 = ofdm.int_skip(total_subc,2,1)
    #    inta_estim_1 = ofdm.interpolator(total_subc,2,dd)
    #    inta_estim_2 = ofdm.interpolator(total_subc,2,dd)
        
        LS_channel_estimator_1 = ofdm.multiply_const_vcc( list( inv_preamble_fd_1 ) )
        LS_channel_estimator_2 = ofdm.multiply_const_vcc( list( inv_preamble_fd_2 ) )
        self.connect( sampled_chest_preamble,skip_block_1, LS_channel_estimator_1)#,inta_estim_1 )
        self.connect( sampled_chest_preamble,skip_block_2, LS_channel_estimator_2)#,inta_estim_2 )
        
        estimated_CTF_1 = LS_channel_estimator_1                  # h0
        estimated_CTF_2 = LS_channel_estimator_2                  # h1
        
        skip_block_3 = ofdm.int_skip(total_subc,2,0)
        skip_block_4 = ofdm.int_skip(total_subc,2,1)
    #    inta_estim_3 = ofdm.interpolator(total_subc,2,dd)
    #    inta_estim_4 = ofdm.interpolator(total_subc,2,dd)
        
        LS_channel_estimator_3 = ofdm.multiply_const_vcc( list( inv_preamble_fd_1 ) )
        LS_channel_estimator_4 = ofdm.multiply_const_vcc( list( inv_preamble_fd_2 ) )
        
        self.connect( sampled_chest_preamble2,skip_block_3, LS_channel_estimator_3)#,inta_estim_3 )
        self.connect( sampled_chest_preamble2,skip_block_4, LS_channel_estimator_4)#,inta_estim_4 )
        
        estimated_CTF_3 = LS_channel_estimator_3                  # h2
        estimated_CTF_4 = LS_channel_estimator_4                  # h3
            
        
        if not options.disable_ctf_enhancer:
          
          # if options.logcir:
            # ifft1 = gr.fft_vcc(total_subc,False,[],True)
            # self.connect( estimated_CTF, ifft1,gr.null_sink(gr.sizeof_gr_complex*total_subc))
            # summ1 = ofdm.vector_sum_vcc(total_subc)
            # c2m =gr.complex_to_mag(total_subc)
            # self.connect( estimated_CTF,summ1 ,gr.null_sink(gr.sizeof_gr_complex))
            # self.connect( estimated_CTF, c2m,gr.null_sink(gr.sizeof_float*total_subc))
            # log_to_file( self, ifft1, "data/CIR1.compl" )
            # log_to_file( self, summ1, "data/CTFsumm1.compl" )
            # log_to_file( self, estimated_CTF, "data/CTF1.compl" )
            # log_to_file( self, c2m, "data/CTFmag1.float" )
            
          ## MSE enhancer
          ctf_mse_enhancer_1 = ofdm.CTF_MSE_enhancer( total_subc, cp_length + cp_length)
          ctf_mse_enhancer_2 = ofdm.CTF_MSE_enhancer( total_subc, cp_length + cp_length)
          self.connect( estimated_CTF_1, ctf_mse_enhancer_1 )
          self.connect( estimated_CTF_2, ctf_mse_enhancer_2 )
          
          ctf_mse_enhancer_3 = ofdm.CTF_MSE_enhancer( total_subc, cp_length + cp_length)
          ctf_mse_enhancer_4 = ofdm.CTF_MSE_enhancer( total_subc, cp_length + cp_length)
          self.connect( estimated_CTF_3, ctf_mse_enhancer_3 )
          self.connect( estimated_CTF_4, ctf_mse_enhancer_4 )
          
            
          estimated_CTF_1 = ctf_mse_enhancer_1
          estimated_CTF_2 = ctf_mse_enhancer_2
          
          estimated_CTF_3 = ctf_mse_enhancer_3
          estimated_CTF_4 = ctf_mse_enhancer_4
          print "Disabled CTF MSE enhancer"
        
        ctf_postprocess_1 = ofdm.postprocess_CTF_estimate( total_subc/2 )
        self.connect( estimated_CTF_1, ( ctf_postprocess_1, 0 ) )
        ctf_postprocess_2 = ofdm.postprocess_CTF_estimate( total_subc/2 )
        self.connect( estimated_CTF_2, ( ctf_postprocess_2, 0 ) )
        ctf_postprocess_3 = ofdm.postprocess_CTF_estimate( total_subc/2 )
        self.connect( estimated_CTF_3, ( ctf_postprocess_3, 0 ) )
        ctf_postprocess_4 = ofdm.postprocess_CTF_estimate( total_subc/2 )
        self.connect( estimated_CTF_4, ( ctf_postprocess_4, 0 ) )
               
        inv_CTF_1 = ( ctf_postprocess_1, 0 )
        disp_CTF_1 = ( ctf_postprocess_1, 1 )
        inv_CTF_2 = ( ctf_postprocess_2, 0 )
        disp_CTF_2 = ( ctf_postprocess_2, 1 )  
        inv_CTF_3 = ( ctf_postprocess_3, 0 )
        disp_CTF_3 = ( ctf_postprocess_3, 1 )
        inv_CTF_4 = ( ctf_postprocess_4, 0 )
        disp_CTF_4 = ( ctf_postprocess_4, 1 )     
        
        disp_CTF_RX0 = gr.add_ff(total_subc/2)
        disp_CTF_RX1 = gr.add_ff(total_subc/2)
        
        self.connect ( disp_CTF_1, (disp_CTF_RX0, 0) )
        self.connect ( disp_CTF_2, (disp_CTF_RX0, 1) )
        self.connect ( disp_CTF_3, (disp_CTF_RX1, 0) )
        self.connect ( disp_CTF_4, (disp_CTF_RX1, 1) ) 
    
        terminate_stream(self,disp_CTF_RX0)
        terminate_stream(self,disp_CTF_RX1)
        
        disp_CTF_RX0 = gr.null_source(gr.sizeof_float*total_subc)
        disp_CTF_RX1 = gr.null_source(gr.sizeof_float*total_subc)
        ## Channel Equalizer
        
        #log_to_file(self, ofdm_blocks, "data/vec_mask.compl")
        #log_to_file(self, ofdm_blocks2, "data/vec_mask2.compl")
        
        nondata_blocks = []
        for i in range(config.frame_length):
          if i in config.training_data.pilotsym_pos:
            nondata_blocks.append(i)
            
        pilot_subc = block_header.pilot_tones
        pilot_subcarriers = block_header.pilot_subc_sym
        print "PILOT SUBCARRIERS: ", pilot_subcarriers
        
        phase_tracking = ofdm.LMS_phase_tracking3( total_subc, pilot_subc,
                                                   nondata_blocks,pilot_subcarriers,0 )
        phase_tracking2 = ofdm.LMS_phase_tracking3( total_subc, pilot_subc,
                                                    nondata_blocks,pilot_subcarriers,0 )
        
        ##phase_tracking = ofdm.LMS_phase_tracking2( total_subc, pilot_subc,
         ##                                          nondata_blocks )
        ##phase_tracking2 = ofdm.LMS_phase_tracking2( total_subc, pilot_subc,
         ##                                           nondata_blocks )
        
    #    self.connect( ofdm_blocks,          ( phase_tracking, 0 ) )
    #    self.connect( ofdm_blocks2,          ( phase_tracking, 1 ))
    #    self.connect( inv_CTF_1,            ( phase_tracking, 2 ) )
    #    self.connect( inv_CTF_3,            ( phase_tracking, 3 ) )
    #    self.connect( frame_start,            ( phase_tracking, 4 ) )
    #    self.connect( frame_start2,            ( phase_tracking, 5) )
    #    
    #    self.connect( ofdm_blocks2,          ( phase_tracking2, 0 ) )
    #    self.connect( ofdm_blocks,          ( phase_tracking2, 1 ))
    #    self.connect( inv_CTF_3,            ( phase_tracking2, 2 ) )
    #    self.connect( inv_CTF_1,            ( phase_tracking2, 3 ) )
    #    self.connect( frame_start2,            ( phase_tracking2, 4 ) )
    #    self.connect( frame_start,            ( phase_tracking2, 5 ) )
        
        self.connect( ofdm_blocks,          ( phase_tracking, 0 ) )
        self.connect( inv_CTF_1,            ( phase_tracking, 1 ) )
        self.connect( frame_start,            ( phase_tracking, 2 ) )
        
        self.connect( ofdm_blocks2,          ( phase_tracking2, 0 ) )
        self.connect( inv_CTF_3,            ( phase_tracking2, 1 ) )
        self.connect( frame_start2,            ( phase_tracking2, 2 ) )
        
        #ofdm_blocks = phase_tracking
        #ofdm_blocks2 = phase_tracking2
        self.connect(phase_tracking,gr.null_sink(gr.sizeof_gr_complex*total_subc))
        self.connect(phase_tracking2,gr.null_sink(gr.sizeof_gr_complex*total_subc))
        
        terminate_stream(self, inv_CTF_2)
        terminate_stream(self, inv_CTF_4)
        #terminate_stream(self, inv_CTF_1)
        #terminate_stream(self, inv_CTF_3)
        terminate_stream(self, estimated_CTF_3)
        terminate_stream(self, estimated_CTF_4)
            ##terminate_stream(self, (phase_tracking,1))
            ##terminate_stream(self, (phase_tracking2,1))
          
        '''equalizer = ofdm.channel_equalizer_mimo_2( total_subc )
        self.connect(  ofdm_blocks,         ( equalizer, 0 ) )
        self.connect(  ofdm_blocks2,        ( equalizer, 1 ) )
        self.connect( inv_CTF_1,            ( equalizer, 2 ) )
        self.connect( inv_CTF_2,            ( equalizer, 3 ) )
        self.connect( inv_CTF_3,            ( equalizer, 4 ) )
        self.connect( inv_CTF_4,            ( equalizer, 5 ) )
        self.connect( frame_start,          ( equalizer, 6 ) )
        self.connect( frame_start2,         ( equalizer, 7 ) )
        ofdm_blocks = equalizer'''
          
        terminate_stream(self, inv_CTF_1)
        terminate_stream(self, inv_CTF_3)
    
        equalizer = ofdm.channel_equalizer_mimo_2( total_subc )    
        self.connect(  ofdm_blocks,          ( equalizer, 0 ) )
        self.connect( estimated_CTF_1,            ( equalizer, 1 ) )
        self.connect( estimated_CTF_2,            ( equalizer, 2 ) )
        self.connect( frame_start,          ( equalizer, 3 ) )
        ofdm_blocks = equalizer
        
        equalizer2 = ofdm.channel_equalizer_mimo_2( total_subc )    
        self.connect( ofdm_blocks2,         ( equalizer2, 0 ) )
        self.connect( estimated_CTF_3,            ( equalizer2, 1 ) )
        self.connect( estimated_CTF_4,            ( equalizer2, 2 ) )
        self.connect( frame_start2,         ( equalizer2, 3 ) )
        ofdm_blocks2 = equalizer2
        
        #ofdm_blocks = equalizer
        #ofdm_blocks2 = equalizer2
        
        #log_to_file(self, equalizer,"data/equalizer.compl")
        #log_to_file(self, ofdm_blocks2,"data/equalizer.compl")
        #log_to_file(self, ofdm_blocks,"data/equalizer2.compl")
        
        
        
        
        
        
        ## LMS Phase tracking
        ## Track residual frequency offset and sampling clock frequency offset
        '''
        nondata_blocks = []
        for i in range(config.frame_length):
          if i in config.training_data.pilotsym_pos:
            nondata_blocks.append(i)
            
        pilot_subc = block_header.pilot_tones
            
        phase_tracking = ofdm.LMS_phase_tracking2( total_subc, pilot_subc,
                                                   nondata_blocks )
        self.connect( equalizer, ( phase_tracking, 0 ) )
        self.connect( frame_start, ( phase_tracking, 1 ) )
        
        phase_tracking2 = ofdm.LMS_phase_tracking2( total_subc, pilot_subc,
                                                    nondata_blocks )
        self.connect( equalizer2, ( phase_tracking2, 0 ) )
        self.connect( frame_start2, ( phase_tracking2, 1 ) )
        
        # if options.scatter_plot_before_phase_tracking:
          # self.before_phase_tracking = equalizer
          
        
        if options.disable_phase_tracking or options.ideal:
          terminate_stream(self, phase_tracking)
          terminate_stream(self, phase_tracking2)
          print "Disabled phase tracking stage"
        else:
          ofdm_blocks = phase_tracking
          ofdm_blocks2 = phase_tracking2
          
        log_to_file(self,phase_tracking, "data/phase_tracking.compl")
        '''
          
        combine = gr.add_cc(config.subcarriers)
        self.connect(ofdm_blocks, (combine,0))
        self.connect(ofdm_blocks2, (combine,1))
        
        norm_val = [0.5]*208
        norm = ofdm.multiply_const_vcc( norm_val)
        self.connect(combine,norm)
        
        ofdm_blocks = norm
    ##    div = gr.multiply_cc(config.subcarriers)
    ##    const = gr.vector_source_c([[0.5+0]*config.subcarriers],True)
    ##    self.connect(ofdm_blocks,div)
    ##    self.connect(const,(div,1))
    ##    ofdm_blocks=div
    #    log_to_file(self,combine,"data/combine.compl")
        ## Output connections
        
        self.connect( ofdm_blocks, out_ofdm_blocks )
        self.connect( frame_start, out_frame_start )
        self.connect( disp_CTF_RX0, out_disp_ctf )
        self.connect( frame_start2, out_frame_start2 )
        self.connect( disp_CTF_RX1, out_disp_ctf2 )
 
    else:
        ## extract channel estimation preamble from frame
        
        chest_pre_trigger_11 = gr.delay( gr.sizeof_char, 
                                      1 )
        chest_pre_trigger_12 = gr.delay( gr.sizeof_char, 
                                      2 )
        sampled_chest_preamble_11 = \
          ofdm.vector_sampler( gr.sizeof_gr_complex * total_subc, 1 )
        sampled_chest_preamble_12 = \
          ofdm.vector_sampler( gr.sizeof_gr_complex * total_subc, 1 )
          
        self.connect( frame_start,       chest_pre_trigger_11 )
        self.connect( chest_pre_trigger_11, ( sampled_chest_preamble_11, 1 ) )
        self.connect( ofdm_blocks,       ( sampled_chest_preamble_11, 0 ) )
        
        self.connect( frame_start,       chest_pre_trigger_12 )
        self.connect( chest_pre_trigger_12, ( sampled_chest_preamble_12, 1 ) )
        self.connect( ofdm_blocks,       ( sampled_chest_preamble_12, 0 ) )
        
        chest_pre_trigger_21 = gr.delay( gr.sizeof_char, 
                                      1 )
        chest_pre_trigger_22 = gr.delay( gr.sizeof_char, 
                                      2 )
        sampled_chest_preamble_21 = \
          ofdm.vector_sampler( gr.sizeof_gr_complex * total_subc, 1 )
        sampled_chest_preamble_22 = \
          ofdm.vector_sampler( gr.sizeof_gr_complex * total_subc, 1 )
          
        self.connect( frame_start2,       chest_pre_trigger_21 )
        self.connect( chest_pre_trigger_21, ( sampled_chest_preamble_21, 1 ) )
        self.connect( ofdm_blocks2,       ( sampled_chest_preamble_21, 0 ) )
        
        self.connect( frame_start2,       chest_pre_trigger_22 )
        self.connect( chest_pre_trigger_22, ( sampled_chest_preamble_22, 1 ) )
        self.connect( ofdm_blocks2,       ( sampled_chest_preamble_22, 0 ) )
        
        
         # Taking inverse for estimating h11 (h12)
        inv_preamble_fd_1 = numpy.array( block_header.pilotsym_fd_1[ 
            block_header.channel_estimation_pilot[0] ] )
        #inv_preamble_fd_1 = inv_preamble_fd_1[0::2]
        
        # Taking inverse for estimating h21 (h22)
        inv_preamble_fd_2 = numpy.array( block_header.pilotsym_fd_2[ 
            block_header.channel_estimation_pilot[0]+1 ] )
        #inv_preamble_fd_2 = inv_preamble_fd_2[1::2]
        
        inv_preamble_fd_1 = 1. / inv_preamble_fd_1
        inv_preamble_fd_2 = 1. / inv_preamble_fd_2
        
       # dd = []
        #for i in range (total_subc/2):
           # dd.extend([i*2])
            
        skip_block_11 = ofdm.int_skip(total_subc,2,0)
        skip_block_111 = ofdm.int_skip(total_subc,2,0)
        skip_block_12 = ofdm.int_skip(total_subc,2,1)
    #    inta_estim_1 = ofdm.interpolator(total_subc,2,dd)
    #    inta_estim_2 = ofdm.interpolator(total_subc,2,dd)
        
        LS_channel_estimator_11 = ofdm.multiply_const_vcc( list( inv_preamble_fd_1 ) )
        LS_channel_estimator_12 = ofdm.multiply_const_vcc( list( inv_preamble_fd_2 ) )
        self.connect( sampled_chest_preamble_11, LS_channel_estimator_11)#,inta_estim_1 )
        self.connect( sampled_chest_preamble_12, LS_channel_estimator_12)#,inta_estim_2 )
        
        estimated_CTF_11 = LS_channel_estimator_11                  # h0
        estimated_CTF_12 = LS_channel_estimator_12                  # h1
        
        skip_block_21 = ofdm.int_skip(total_subc,2,0)
        skip_block_211 = ofdm.int_skip(total_subc,2,0)
        skip_block_22 = ofdm.int_skip(total_subc,2,1)
    #    inta_estim_3 = ofdm.interpolator(total_subc,2,dd)
    #    inta_estim_4 = ofdm.interpolator(total_subc,2,dd)
        
        LS_channel_estimator_21 = ofdm.multiply_const_vcc( list( inv_preamble_fd_1 ) )
        LS_channel_estimator_22 = ofdm.multiply_const_vcc( list( inv_preamble_fd_2 ) )
        
        self.connect( sampled_chest_preamble_21, LS_channel_estimator_21)#,inta_estim_3 )
        self.connect( sampled_chest_preamble_22, LS_channel_estimator_22)#,inta_estim_4 )
        
        estimated_CTF_21 = LS_channel_estimator_21                  # h2
        estimated_CTF_22 = LS_channel_estimator_22                  # h3
            
        
        if not options.disable_ctf_enhancer:
          
          # if options.logcir:
            # ifft1 = gr.fft_vcc(total_subc,False,[],True)
            # self.connect( estimated_CTF, ifft1,gr.null_sink(gr.sizeof_gr_complex*total_subc))
            # summ1 = ofdm.vector_sum_vcc(total_subc)
            # c2m =gr.complex_to_mag(total_subc)
            # self.connect( estimated_CTF,summ1 ,gr.null_sink(gr.sizeof_gr_complex))
            # self.connect( estimated_CTF, c2m,gr.null_sink(gr.sizeof_float*total_subc))
            # log_to_file( self, ifft1, "data/CIR1.compl" )
            # log_to_file( self, summ1, "data/CTFsumm1.compl" )
            # log_to_file( self, estimated_CTF, "data/CTF1.compl" )
            # log_to_file( self, c2m, "data/CTFmag1.float" )
            
          ## MSE enhancer
          ctf_mse_enhancer_11 = ofdm.CTF_MSE_enhancer( total_subc, cp_length + cp_length)
          ctf_mse_enhancer_12 = ofdm.CTF_MSE_enhancer( total_subc, cp_length + cp_length)
          self.connect( estimated_CTF_11, ctf_mse_enhancer_11 )
          self.connect( estimated_CTF_12, ctf_mse_enhancer_12 )
          
          ctf_mse_enhancer_21 = ofdm.CTF_MSE_enhancer( total_subc, cp_length + cp_length)
          ctf_mse_enhancer_22 = ofdm.CTF_MSE_enhancer( total_subc, cp_length + cp_length)
          self.connect( estimated_CTF_21, ctf_mse_enhancer_21 )
          self.connect( estimated_CTF_22, ctf_mse_enhancer_22 )
          
            
          estimated_CTF_11 = ctf_mse_enhancer_11
          estimated_CTF_12 = ctf_mse_enhancer_12
          
          estimated_CTF_21 = ctf_mse_enhancer_21
          estimated_CTF_22 = ctf_mse_enhancer_22
          print "Disabled CTF MSE enhancer"
        
        ctf_postprocess_11 = ofdm.postprocess_CTF_estimate( total_subc )
        self.connect( estimated_CTF_11, ( ctf_postprocess_11, 0 ) )
        ctf_postprocess_12 = ofdm.postprocess_CTF_estimate( total_subc )
        self.connect( estimated_CTF_12, ( ctf_postprocess_12, 0 ) )
        
        ctf_postprocess_21 = ofdm.postprocess_CTF_estimate( total_subc )
        self.connect( estimated_CTF_21, ( ctf_postprocess_21, 0 ) )
        ctf_postprocess_22 = ofdm.postprocess_CTF_estimate( total_subc )
        self.connect( estimated_CTF_22, ( ctf_postprocess_22, 0 ) )
               
        inv_CTF_11 = ( ctf_postprocess_11, 0 )
        disp_CTF_11 = ( ctf_postprocess_11, 1 )
        inv_CTF_12 = ( ctf_postprocess_12, 0 )
        disp_CTF_12 = ( ctf_postprocess_12, 1 )  
        inv_CTF_21 = ( ctf_postprocess_21, 0 )
        disp_CTF_21 = ( ctf_postprocess_21, 1 )
        inv_CTF_22 = ( ctf_postprocess_22, 0 )
        disp_CTF_22 = ( ctf_postprocess_22, 1 )     
        
        #disp_CTF_RX0 = gr.add_ff(total_subc)
        #disp_CTF_RX1 = gr.add_ff(total_subc)
        
        #self.connect ( disp_CTF_11, (disp_CTF_RX0, 0) )
        #self.connect ( disp_CTF_12, (disp_CTF_RX0, 1) )
        #self.connect ( disp_CTF_21, (disp_CTF_RX1, 0) )
        #self.connect ( disp_CTF_22, (disp_CTF_RX1, 1) ) 
    
        terminate_stream(self,disp_CTF_21)
        terminate_stream(self,disp_CTF_22)
        
        disp_CTF_RX0 = disp_CTF_11
        disp_CTF_RX1 = disp_CTF_12
        ## Channel Equalizer
        
        #log_to_file(self, ofdm_blocks, "data/vec_mask.compl")
        #log_to_file(self, ofdm_blocks2, "data/vec_mask2.compl")
        
        nondata_blocks = []
        for i in range(config.frame_length):
          if i in config.training_data.pilotsym_pos:
            nondata_blocks.append(i)
            
        pilot_subc = block_header.pilot_tones
        pilot_subcarriers = block_header.pilot_subc_sym
        print "PILOT SUBCARRIERS: ", pilot_subcarriers
        
        phase_tracking = ofdm.LMS_phase_tracking3( total_subc, pilot_subc,
                                                   nondata_blocks,pilot_subcarriers,0 )
        phase_tracking2 = ofdm.LMS_phase_tracking3( total_subc, pilot_subc,
                                                    nondata_blocks,pilot_subcarriers,0 )
        
        ##phase_tracking = ofdm.LMS_phase_tracking2( total_subc, pilot_subc,
         ##                                          nondata_blocks )
        ##phase_tracking2 = ofdm.LMS_phase_tracking2( total_subc, pilot_subc,
         ##                                           nondata_blocks )
        
    #    self.connect( ofdm_blocks,          ( phase_tracking, 0 ) )
    #    self.connect( ofdm_blocks2,          ( phase_tracking, 1 ))
    #    self.connect( inv_CTF_1,            ( phase_tracking, 2 ) )
    #    self.connect( inv_CTF_3,            ( phase_tracking, 3 ) )
    #    self.connect( frame_start,            ( phase_tracking, 4 ) )
    #    self.connect( frame_start2,            ( phase_tracking, 5) )
    #    
    #    self.connect( ofdm_blocks2,          ( phase_tracking2, 0 ) )
    #    self.connect( ofdm_blocks,          ( phase_tracking2, 1 ))
    #    self.connect( inv_CTF_3,            ( phase_tracking2, 2 ) )
    #    self.connect( inv_CTF_1,            ( phase_tracking2, 3 ) )
    #    self.connect( frame_start2,            ( phase_tracking2, 4 ) )
    #    self.connect( frame_start,            ( phase_tracking2, 5 ) )
        
        self.connect( ofdm_blocks,          ( phase_tracking, 0 ) )
        self.connect( inv_CTF_11,    skip_block_111,        ( phase_tracking, 1 ) )
        self.connect( frame_start,            ( phase_tracking, 2 ) )
        
        self.connect( ofdm_blocks2,          ( phase_tracking2, 0 ) )
        self.connect( inv_CTF_21, skip_block_211,   ( phase_tracking2, 1 ) )
        self.connect( frame_start2,            ( phase_tracking2, 2 ) )
        
        if options.disable_phase_tracking or options.ideal:
          terminate_stream(self, phase_tracking)
          terminate_stream(self, phase_tracking2)
          print "Disabled phase tracking stage"
        else:
          ofdm_blocks = phase_tracking
          ofdm_blocks2 = phase_tracking2
          
        self.connect(phase_tracking,gr.null_sink(gr.sizeof_gr_complex*total_subc))
        self.connect(phase_tracking2,gr.null_sink(gr.sizeof_gr_complex*total_subc))
        
        terminate_stream(self, inv_CTF_12)
        terminate_stream(self, inv_CTF_22)
        #terminate_stream(self, inv_CTF_1)
        #terminate_stream(self, inv_CTF_3)
        #terminate_stream(self, estimated_CTF_21)
        #terminate_stream(self, estimated_CTF_22)
            ##terminate_stream(self, (phase_tracking,1))
            ##terminate_stream(self, (phase_tracking2,1))
            
       
          
        equalizer = ofdm.channel_equalizer_mimo_3( total_subc )
        self.connect(  ofdm_blocks,         ( equalizer, 0 ) )
        self.connect(  ofdm_blocks2,        ( equalizer, 1 ) )
        self.connect( estimated_CTF_11,    skip_block_11,         ( equalizer, 2 ) )
        self.connect( estimated_CTF_12,   skip_block_12,          ( equalizer, 3 ) )
        self.connect( estimated_CTF_21,   skip_block_21,          ( equalizer, 4 ) )
        self.connect( estimated_CTF_22,    skip_block_22,         ( equalizer, 5 ) )
        self.connect( frame_start,          ( equalizer, 6 ) )
        self.connect( frame_start,         ( equalizer, 7 ) )
        ofdm_blocks = equalizer
          
        #terminate_stream(self, inv_CTF_11)
        #terminate_stream(self, inv_CTF_21)
    
        '''equalizer = ofdm.channel_equalizer_mimo_2( total_subc )    
        self.connect(  ofdm_blocks,          ( equalizer, 0 ) )
        self.connect( estimated_CTF_11,    skip_block_11,        ( equalizer, 1 ) )
        self.connect( estimated_CTF_12,   skip_block_12,         ( equalizer, 2 ) )
        self.connect( frame_start,          ( equalizer, 3 ) )
        ofdm_blocks = equalizer
        
        equalizer2 = ofdm.channel_equalizer_mimo_2( total_subc )    
        self.connect( ofdm_blocks2,         ( equalizer2, 0 ) )
        self.connect( estimated_CTF_21,  skip_block_21,            ( equalizer2, 1 ) )
        self.connect( estimated_CTF_22,    skip_block_22,        ( equalizer2, 2 ) )
        self.connect( frame_start2,         ( equalizer2, 3 ) )
        ofdm_blocks2 = equalizer2'''
        
        #ofdm_blocks = equalizer
        #ofdm_blocks2 = equalizer2
        
        #log_to_file(self, equalizer,"data/equalizer.compl")
        #log_to_file(self, ofdm_blocks2,"data/equalizer.compl")
        #log_to_file(self, ofdm_blocks,"data/equalizer2.compl")
        
        
        
        
        
        
        ## LMS Phase tracking
        ## Track residual frequency offset and sampling clock frequency offset
        '''
        nondata_blocks = []
        for i in range(config.frame_length):
          if i in config.training_data.pilotsym_pos:
            nondata_blocks.append(i)
            
        pilot_subc = block_header.pilot_tones
            
        phase_tracking = ofdm.LMS_phase_tracking2( total_subc, pilot_subc,
                                                   nondata_blocks )
        self.connect( equalizer, ( phase_tracking, 0 ) )
        self.connect( frame_start, ( phase_tracking, 1 ) )
        
        phase_tracking2 = ofdm.LMS_phase_tracking2( total_subc, pilot_subc,
                                                    nondata_blocks )
        self.connect( equalizer2, ( phase_tracking2, 0 ) )
        self.connect( frame_start2, ( phase_tracking2, 1 ) )
        
        # if options.scatter_plot_before_phase_tracking:
          # self.before_phase_tracking = equalizer
          
        
        if options.disable_phase_tracking or options.ideal:
          terminate_stream(self, phase_tracking)
          terminate_stream(self, phase_tracking2)
          print "Disabled phase tracking stage"
        else:
          ofdm_blocks = phase_tracking
          ofdm_blocks2 = phase_tracking2
          
        log_to_file(self,phase_tracking, "data/phase_tracking.compl")
        '''
          
        '''combine = gr.add_cc(config.subcarriers)
        self.connect(ofdm_blocks, (combine,0))
        self.connect(ofdm_blocks2, (combine,1))
        
        norm_val = [0.5]*config.subcarriers
        norm = ofdm.multiply_const_vcc( norm_val)
        self.connect(combine,norm)
        
        ofdm_blocks = norm'''
    ##    div = gr.multiply_cc(config.subcarriers)
    ##    const = gr.vector_source_c([[0.5+0]*config.subcarriers],True)
    ##    self.connect(ofdm_blocks,div)
    ##    self.connect(const,(div,1))
    ##    ofdm_blocks=div
    #    log_to_file(self,combine,"data/combine.compl")
        ## Output connections
        
        self.connect( ofdm_blocks, out_ofdm_blocks )
        self.connect( frame_start, out_frame_start )
        self.connect( disp_CTF_RX0, out_disp_ctf )
        self.connect( frame_start2, out_frame_start2 )
        self.connect( disp_CTF_RX1, out_disp_ctf2 )
        
    
    
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
