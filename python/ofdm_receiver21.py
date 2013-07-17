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
            1, 1,
            gr.sizeof_gr_complex ),
        gr.io_signature4(
            4, 4,
            gr.sizeof_gr_complex * total_subc,    # OFDM blocks
            gr.sizeof_char,                       # Frame start
            gr.sizeof_float * total_subc,         # Normalized |CTF|^2
            gr.sizeof_float * total_subc ) )      # Normalized |CTF|^2
    
    
    ## Input and output ports
    self.input  = rx_input = (self,0)

    
    out_ofdm_blocks = ( self, 0 )
    out_frame_start = ( self, 1 )
    out_disp_ctf    = ( self, 2 )
    out_disp_ctf2    = ( self, 3 )
    
    ## pre-FFT processing
    
    
    ## Compute autocorrelations for S&C preamble
    ## and cyclic prefix
    sc_metric = autocorrelator( fft_length/2, fft_length/2 )
    gi_metric = autocorrelator( fft_length, cp_length )
    
    self.connect( rx_input, sc_metric )
    self.connect( rx_input, gi_metric )
    
    ## Sync. Output contains OFDM blocks
    sync = ofdm.dominiks_sync_01( fft_length, cp_length )
    self.connect( rx_input, ( sync, 0 ) )
    self.connect( sc_metric, ( sync, 1 ) )
    self.connect( gi_metric, ( sync, 2 ) )
    ofdm_blocks = ( sync, 0 )
    frame_start = ( sync, 1 )
    
    if options.disable_time_sync or options.ideal:
      terminate_stream(self, ofdm_blocks)
      terminate_stream(self, frame_start)
      
      serial_to_parallel = gr.stream_to_vector(gr.sizeof_gr_complex,block_length)
      discard_cp = ofdm.vector_mask(block_length,cp_length,fft_length,[])
      ofdm_blocks = discard_cp
      self.connect( rx_input, serial_to_parallel, discard_cp )
      
      frame_start = [0]*frame_length
      frame_start[0] = 1
      frame_start = gr.vector_source_b(frame_start,True)
      
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
    
    
    
    ## Adaptive LMS FIR filtering of frequency offset
    lms_fir = ofdm.lms_fir_ff( 20, 1e-3 ) # TODO: verify parameter choice
    self.connect( freq_offset, lms_fir )
    freq_offset = lms_fir
    log_to_file(self, lms_fir, "data/foe_21.float")
    
#    log_to_file(self, lms_fir, "data/lms_fir.float")
#    log_to_file(self, lms_fir2, "data/lms_fir2.float")
    
    if options.disable_freq_sync or options.ideal:
       terminate_stream(self, freq_offset)
       freq_offset = gr.vector_source_f([0.0],True)
       print "Disabled frequency synchronization stage"
    
    ## Correct frequency shift, feed-forward structure
    frequency_shift = ofdm.frequency_shift_vcc( fft_length, -1.0/fft_length,
                                                cp_length )
    self.connect( ofdm_blocks, ( frequency_shift, 0 ) )
    self.connect( freq_offset, ( frequency_shift, 1 ) )
    self.connect( frame_start, ( frequency_shift, 2 ) )
    ofdm_blocks = frequency_shift
    
    
    ## FFT
    fft = gr.fft_vcc( fft_length, True, [], True )
    self.connect( ofdm_blocks, fft )
    ofdm_blocks = fft
    
    ## Remove virtual subcarriers
    if fft_length > data_subc:
      subcarrier_mask = ofdm.vector_mask( fft_length, virtual_subc/2,
                                           total_subc, [] )
      self.connect( ofdm_blocks, subcarrier_mask )
      ofdm_blocks = subcarrier_mask
      
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
      
    
    
    ## extract channel estimation preamble from frame
    
    if options.est_preamble==1:
        chest_pre_trigger = gr.delay( gr.sizeof_char, 
                                      1 )
        sampled_chest_preamble = \
          ofdm.vector_sampler( gr.sizeof_gr_complex * total_subc, 1 )
        self.connect( frame_start,       chest_pre_trigger )
        self.connect( chest_pre_trigger, ( sampled_chest_preamble, 1 ) )
        self.connect( ofdm_blocks,       ( sampled_chest_preamble, 0 ) )
        
        
        ## Least Squares estimator for channel transfer function (CTF)
        
        # Taking inverse for estimating h11 (h12)
        inv_preamble_fd_1 = numpy.array( block_header.pilotsym_fd_1[ 
            block_header.channel_estimation_pilot[0] ] )
        print "inv_preamble_fd_1: ",inv_preamble_fd_1
        inv_preamble_fd_1 = inv_preamble_fd_1[0::2]
        #print "inv_preamble_fd_1 ", inv_preamble_fd_1
        
        # Taking inverse for estimating h21 (h22)
        inv_preamble_fd_2 = numpy.array( block_header.pilotsym_fd_2[ 
            block_header.channel_estimation_pilot[0] ] )
        print "inv_preamble_fd_2: ",inv_preamble_fd_2
        inv_preamble_fd_2 = inv_preamble_fd_2[1::2]
        #print "inv_preamble_fd_2 ", inv_preamble_fd_2
        
        print "inv_preamble_fd_1: ",inv_preamble_fd_1
        print "inv_preamble_fd_2: ",inv_preamble_fd_2
        
        
        inv_preamble_fd_1 = 1. / inv_preamble_fd_1
        inv_preamble_fd_2 = 1. / inv_preamble_fd_2
        
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
        estimated_CTF_2 = LS_channel_estimator_2                  # h1              # h3
            
        
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
          
            
          estimated_CTF_1 = ctf_mse_enhancer_1
          estimated_CTF_2 = ctf_mse_enhancer_2
          
          print "Disabled CTF MSE enhancer"
        
        ctf_postprocess_1 = ofdm.postprocess_CTF_estimate( total_subc/2 )
        self.connect( estimated_CTF_1, ( ctf_postprocess_1, 0 ) )
        ctf_postprocess_2 = ofdm.postprocess_CTF_estimate( total_subc/2 )
        self.connect( estimated_CTF_2, ( ctf_postprocess_2, 0 ) )
               
        inv_CTF_1 = ( ctf_postprocess_1, 0 )
        disp_CTF_1 = ( ctf_postprocess_1, 1 )
        inv_CTF_2 = ( ctf_postprocess_2, 0 )
        disp_CTF_2 = ( ctf_postprocess_2, 1 )  
    
        disp_CTF_RX0 = gr.add_ff(total_subc/2)
        
        self.connect ( disp_CTF_1, (disp_CTF_RX0, 0) )
        self.connect ( disp_CTF_2, (disp_CTF_RX0, 1) )
    
    
        terminate_stream(self,disp_CTF_RX0)
        terminate_stream(self,inv_CTF_2)
        
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
        
        #self.connect(phase_tracking,gr.null_sink(gr.sizeof_gr_complex*total_subc))
        
        ofdm_blocks = phase_tracking
       
          
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
          
    
        equalizer = ofdm.channel_equalizer_mimo_2( total_subc )    
        self.connect(  ofdm_blocks,          ( equalizer, 0 ) )
        self.connect( estimated_CTF_1,            ( equalizer, 1 ) )
        self.connect( estimated_CTF_2,            ( equalizer, 2 ) )
        self.connect( frame_start,          ( equalizer, 3 ) )
        #ofdm_blocks = equalizer
    
        #ofdm_blocks2 = equalizer2
        
    
        ofdm_blocks = equalizer
        
        #log_to_file(self, equalizer,"data/equalizer.compl")
        log_to_file(self, ofdm_blocks,"data/equalizer.compl")
        log_to_file(self, estimated_CTF_1,"data/estimated_CTF_1.compl")
        log_to_file(self, estimated_CTF_2,"data/estimated_CTF_2.compl")
        
        
        
        
        
        
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
        ofdm_blocks = combine'''
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
        self.connect( disp_CTF_RX1, out_disp_ctf2 )
        
    else: # (2 preambles for channel estimation)
        chest_pre_trigger_1 = gr.delay( gr.sizeof_char, 
                                      1 )
        
        chest_pre_trigger_2 = gr.delay( gr.sizeof_char, 
                                      2 )
        sampled_chest_preamble_1 = \
          ofdm.vector_sampler( gr.sizeof_gr_complex * total_subc, 1 )
          
        sampled_chest_preamble_2 = \
          ofdm.vector_sampler( gr.sizeof_gr_complex * total_subc, 1 ) 
           
        self.connect( frame_start,       chest_pre_trigger_1 )
        self.connect( chest_pre_trigger_1, ( sampled_chest_preamble_1, 1 ) )
        self.connect( ofdm_blocks,       ( sampled_chest_preamble_1, 0 ) )
        
        self.connect( frame_start,       chest_pre_trigger_2 )
        self.connect( chest_pre_trigger_2, ( sampled_chest_preamble_2, 1 ) )
        self.connect( ofdm_blocks,       ( sampled_chest_preamble_2, 0 ) )
        
        
        ## Least Squares estimator for channel transfer function (CTF)
        
        # Taking inverse for estimating h11 (h12)
        inv_preamble_fd_1 = numpy.array( block_header.pilotsym_fd_1[ 
            block_header.channel_estimation_pilot[0] ] )
        print "inv_preamble_fd_1: ",inv_preamble_fd_1
        #inv_preamble_fd_1 = inv_preamble_fd_1[0::2]
        #print "inv_preamble_fd_1 ", inv_preamble_fd_1
        
        # Taking inverse for estimating h21 (h22)
        inv_preamble_fd_2 = numpy.array( block_header.pilotsym_fd_2[ 
            block_header.channel_estimation_pilot[0]+1 ] )
        print "inv_preamble_fd_2: ",inv_preamble_fd_2
        #inv_preamble_fd_2 = inv_preamble_fd_2[1::2]
        #print "inv_preamble_fd_2 ", inv_preamble_fd_2
        
        print "inv_preamble_fd_1: ",inv_preamble_fd_1
        print "inv_preamble_fd_2: ",inv_preamble_fd_2
        
        
        inv_preamble_fd_1 = 1. / inv_preamble_fd_1
        inv_preamble_fd_2 = 1. / inv_preamble_fd_2
        
        #dd = []
        #for i in range (total_subc/2):
          #  dd.extend([i*2])
            
        skip_block_1 = ofdm.int_skip(total_subc,2,0)
        skip_block_11 = ofdm.int_skip(total_subc,2,0)
        skip_block_2 = ofdm.int_skip(total_subc,2,1)
    #    inta_estim_1 = ofdm.interpolator(total_subc,2,dd)
    #    inta_estim_2 = ofdm.interpolator(total_subc,2,dd)
        
        LS_channel_estimator_1 = ofdm.multiply_const_vcc( list( inv_preamble_fd_1 ) )
        LS_channel_estimator_2 = ofdm.multiply_const_vcc( list( inv_preamble_fd_2 ) )
        self.connect( sampled_chest_preamble_1, LS_channel_estimator_1)#,inta_estim_1 )
        self.connect( sampled_chest_preamble_2, LS_channel_estimator_2)#,inta_estim_2 )
        
        estimated_CTF_1 = LS_channel_estimator_1                  # h0
        estimated_CTF_2 = LS_channel_estimator_2                  # h1              # h3
            
        
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
          
            
          estimated_CTF_1 = ctf_mse_enhancer_1
          estimated_CTF_2 = ctf_mse_enhancer_2
          
          print "Disabled CTF MSE enhancer"
        
        ctf_postprocess_1 = ofdm.postprocess_CTF_estimate( total_subc )
        self.connect( estimated_CTF_1, ( ctf_postprocess_1, 0 ) )
        ctf_postprocess_2 = ofdm.postprocess_CTF_estimate( total_subc )
        self.connect( estimated_CTF_2, ( ctf_postprocess_2, 0 ) )
               
        inv_CTF_1 = ( ctf_postprocess_1, 0 )
        disp_CTF_1 = ( ctf_postprocess_1, 1 )
        inv_CTF_2 = ( ctf_postprocess_2, 0 )
        disp_CTF_2 = ( ctf_postprocess_2, 1 )  
    
        #disp_CTF_RX0 = gr.add_ff(total_subc)
        
        #self.connect ( disp_CTF_1, (disp_CTF_RX0, 0) )
        #self.connect ( disp_CTF_2, (disp_CTF_RX0, 1) )
    
    
        #terminate_stream(self,disp_CTF_RX0)
        terminate_stream(self,inv_CTF_2)
        
        disp_CTF_RX0 = disp_CTF_1
        disp_CTF_RX1 = disp_CTF_2
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
        self.connect( inv_CTF_1,    skip_block_11,   ( phase_tracking, 1 ) )
        self.connect( frame_start,            ( phase_tracking, 2 ) )
        
        #self.connect(phase_tracking,gr.null_sink(gr.sizeof_gr_complex*total_subc))
        
        if options.disable_phase_tracking or options.ideal:
          terminate_stream(self, phase_tracking)
          print "Disabled phase tracking stage"
        else:
          ofdm_blocks = phase_tracking
          
       
          
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
          
    
        equalizer = ofdm.channel_equalizer_mimo_2( total_subc )    
        self.connect(  ofdm_blocks,          ( equalizer, 0 ) )
        self.connect( estimated_CTF_1,     skip_block_1,       ( equalizer, 1 ) )
        self.connect( estimated_CTF_2,    skip_block_2,        ( equalizer, 2 ) )
        self.connect( frame_start,          ( equalizer, 3 ) )
        #ofdm_blocks = equalizer
    
        #ofdm_blocks2 = equalizer2
        
    
        ofdm_blocks = equalizer
        
        #log_to_file(self, equalizer,"data/equalizer.compl")
        log_to_file(self, ofdm_blocks,"data/equalizer.compl")
        log_to_file(self, estimated_CTF_1,"data/estimated_CTF_1.compl")
        log_to_file(self, estimated_CTF_2,"data/estimated_CTF_2.compl")
        
        
        
        
        
        
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
        ofdm_blocks = combine'''
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
