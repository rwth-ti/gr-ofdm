# Copyright 2011,2012 Free Software Foundation, Inc.
#
# This file is part of GNU Radio
#
# GNU Radio is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 3, or (at your option)
# any later version.
#
# GNU Radio is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with GNU Radio; see the file COPYING.  If not, write to
# the Free Software Foundation, Inc., 51 Franklin Street,
# Boston, MA 02110-1301, USA.

########################################################################
# Setup library
########################################################################
include(GrPlatform) #define LIB_SUFFIX


include_directories(${Boost_INCLUDE_DIR}
					${CMAKE_CURRENT_BINARY_DIR}
    				${CMAKE_CURRENT_BINARY_DIR}/../include
    				${VOLK_INCLUDE_DIRS})
link_directories(${Boost_LIBRARY_DIRS})
list(APPEND ofdm_sources
    accumulator_cc_impl.cc
    autocorrelator_stage1_impl.cc
    autocorrelator_stage2_impl.cc
    accumulator_ff_impl.cc
    autocorrelator0_impl.cc
    ber_measurement_impl.cc
    bernoulli_bit_src_impl.cc
    base.cc
    ofdmi_shared_generator.cc
    ofdmi_mod.cc
    bit_position_dependent_ber_impl.cc
    calc_metric.cc
    channel_equalizer_mimo_2_impl.cc
    channel_equalizer_mimo_3_impl.cc
    channel_equalizer_mimo_impl.cc
    channel_equalizer_impl.cc
    channel_estimator_01_impl.cc
    channel_estimator_02_impl.cc
    coded_bpsk_soft_decoder_impl.cc
    #compat_read_ber_from_imgxfer_impl.cc
    #imgtransfer_sink_impl.cc
    util_random.cc
    util_endian.cc
    util_bmp.cc
    util_ipc.cc
    imgtransfer_src_impl.cc
    imgtransfer_testkanal_impl.cc
    complex_to_arg_impl.cc
    complex_white_noise_impl.cc
    constellation_sample_filter_impl.cc
    CTF_MSE_enhancer_impl.cc
    cyclic_prefixer_impl.cc
    depuncture_bb_impl.cc
    depuncture_ff_impl.cc
    dominiks_sync_01_impl.cc
    dynamic_trigger_ib_impl.cc
    extract_block_from_frame_impl.cc
    find_cir_shift_impl.cc
    frame_mux_impl.cc
    frequency_shift_vcc_impl.cc
    gate_ff_impl.cc
    generic_mapper_bcv_impl.cc
    generic_demapper_vcb_impl.cc
    generic_mapper_mimo_bcv_impl.cc
    generic_softdemapper_vcf_impl.cc
    int_skip_impl.cc
    interp_cir_set_noncir_to_zero_impl.cc
    limit_vff_impl.cc
    lms_fir_ff_impl.cc
    lms_phase_tracking_impl.cc
    lms_phase_tracking_02_impl.cc
    lms_phase_tracking_03_impl.cc
    ls_estimator_straight_slope_impl.cc
    mean_squared_error_impl.cc
    mm_frequency_estimator_impl.cc
    moms_cc_impl.cc
    moms_ff_impl.cc
    multiply_const_ccf_impl.cc
    multiply_const_ii_impl.cc
    multiply_const_vcc_impl.cc
    noise_nulling_impl.cc
    normalize_vcc_impl.cc
    peak_detector_02_fb_impl.cc
    peak_resync_bb_impl.cc
    pilot_subcarrier_inserter_impl.cc
    postprocess_CTF_estimate_impl.cc
    puncture_bb_impl.cc
    reassemble_ofdm_frame_impl.cc
    reference_data_source_ib_impl.cc
    reference_data_source_mimo_ib_impl.cc
    repetition_decoder_bs_impl.cc
    repetition_encoder_sb_impl.cc
    subc_snr_estimator_impl.cc
    scatterplot_sink_impl.cc
    schmidl_cfo_estimator_impl.cc
    schmidl_tm_rec_stage1_impl.cc
    schmidl_tm_rec_stage2_impl.cc
    sinr_estimator_impl.cc
    sinr_estimator_02_impl.cc
    sinr_interpolator_impl.cc
    skip_impl.cc
    snr_estimator_impl.cc
    sqrt_vff_impl.cc
    static_mux_c_impl.cc
    static_mux_v_impl.cc
    stc_decoder_rx0_impl.cc
    stc_decoder_rx1_impl.cc
    stc_encoder_impl.cc
    stream_controlled_mux_b_impl.cc
    stream_controlled_mux_impl.cc
    suppress_erasure_decision_impl.cc
    symbol_random_src_impl.cc
    throughput_measure_impl.cc
    trigger_surveillance_impl.cc
    vector_padding_impl.cc
    vector_mask_impl.cc
    vector_element_impl.cc
    vector_sampler_impl.cc
    vector_sum_vcc_impl.cc
    vector_sum_vff_impl.cc
    viterbi_combined_fb_impl.cc
    fsm.cc
    #corba_push_consumer.cc
    #corba_push_supplier.cc
    #corba_push_supplier_wrapper.cc
    #orb.cc 
    #corba_assignment_src_sv_impl.cc
    #corba_bitcount_src_si_impl.cc
    #corba_bitmap_src_impl.cc
    #corba_id_filter_impl.cc
    #corba_id_src_impl.cc
    #corba_map_src_sv_impl.cc
    #corba_multiplex_src_ss_impl.cc
    #corba_power_allocator_impl.cc
    #corba_power_src_sv_impl.cc
    #corba_rxbaseband_sink_impl.cc
    #corba_rxinfo_sink_imgxfer_impl.cc
    #corba_rxinfo_sink_impl.cc
    itpp_tdl_channel_impl.cc
    encoder_bb_impl.cc
    reference_data_source_02_ib_impl.cc
    #corba_bitcount_src_02_si_impl.cc 
    )
SET ( CMAKE_CXX_FLAGS "-O3 -march=core2 -mfpmath=sse" )
add_library(gnuradio-ofdm SHARED ${ofdm_sources})
target_link_libraries(gnuradio-ofdm 
		${Boost_LIBRARIES} 
		${GNURADIO_RUNTIME_LIBRARIES}
		${GNURADIO_FFT_LIBRARIES}
		${GNURADIO_BLOCKS_LIBRARIES}
        ${GNURADIO_FILTER_LIBRARIES}
        ${GNURADIO_FEC_LIBRARIES}
        ${GNURADIO_TRELLIS_LIBRARIES}
		${ITPP_LIBRARIES}
    	#${TAO_LIBRARIES}
    	# "-Wl,--whole-archive"
     	#${CMAKE_BINARY_DIR}/tao_skeleton/libtao_ofdmti.a
    	#"-Wl,--no-whole-archive"
		)
		
add_dependencies(gnuradio-ofdm gnuradio-runtime gnuradio-fft gnuradio-blocks gnuradio-filter gnuradio-fec gnuradio -trellis)
# tao_ofdmti)
    message(STATUS "gnuradio-fft: ${gnuradio-fft}")
    message(STATUS "Boost_LIBRARIES at: ${Boost_LIBRARIES}")
    message(STATUS "GNURADIO_RUNTIME_LIBRARIES at: ${GNURADIO_RUNTIME_LIBRARIES}")
    message(STATUS "TAO_LIBRARIES at: ${CMAKE_BINARY_DIR}/tao_skeleton/libtao_ofdmti.a")
    		
set_target_properties(gnuradio-ofdm PROPERTIES DEFINE_SYMBOL "gnuradio_ofdm_EXPORTS")

########################################################################
# Install built library files
########################################################################
install(TARGETS gnuradio-ofdm
    LIBRARY DESTINATION lib${LIB_SUFFIX} # .so/.dylib file
    ARCHIVE DESTINATION lib${LIB_SUFFIX} # .lib file
    RUNTIME DESTINATION bin              # .dll file
)


