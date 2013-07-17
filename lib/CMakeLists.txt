# Copyright 2011 Free Software Foundation, Inc.
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

SET ( CMAKE_CXX_FLAGS "-O3 -march=core2 -mfpmath=sse" )
add_library(gnuradio-ofdm SHARED 
    ofdm_template_ff.cc 
    ofdm_accumulator_cc.cc 
    ofdm_accumulator_ff.cc
    ofdm_autocorrelator0.cc
    ofdm_autocorrelator_stage1.cc
    ofdm_autocorrelator_stage2.cc
    ofdm_ber_measurement.cc
    ofdm_bit_position_dependent_BER.cc
    ofdm_channel_equalizer_mimo.cc
    ofdm_channel_equalizer_mimo_2.cc
    ofdm_channel_equalizer_mimo_3.cc
    fsm.cc
    base.cc
    ofdm_stc_encoder.cc
    ofdm_stc_decoder_rx1.cc
    ofdm_stc_decoder_rx0.cc
    ofdm_puncture_bb.cc
    ofdm_reference_data_source_mimo_ib.cc
    ofdm_viterbi_combined_fb.cc
    ofdm_depuncture_bb.cc
    ofdm_depuncture_ff.cc
    ofdm_calc_metric.cc
    ofdm_channel_equalizer.cc
    ofdm_channel_estimator_01.cc
    ofdm_channel_estimator_02.cc
    ofdm_coded_bpsk_soft_decoder.cc
    ofdm_compat_read_ber_from_imgxfer.cc
    ofdm_complex_to_arg.cc
    ofdm_imgtransfer_sink.cc
    ofdm_int_skip.cc
    ofdm_multiply_const_ii.cc
    ofdm_constellation_sample_filter.cc
    ofdm_CTF_MSE_enhancer.cc
    ofdm_dominiks_sync_01.cc
    ofdm_dynamic_trigger_ib.cc
    ofdm_cyclic_prefixer.cc
    ofdm_extract_block_from_frame.cc
    ofdm_find_cir_shift.cc
    ofdm_frame_mux.cc
    ofdm_frequency_shift_vcc.cc
    ofdm_generic_mapper_bcv.cc
    ofdm_gate_ff.cc
    ofdm_generic_demapper_vcb.cc
    ofdm_generic_mapper_mimo_bcv.cc
    ofdm_generic_softdemapper_vcf.cc
    ofdm_get_zeros.cc
    ofdm_imgtransfer_src.cc
    ofdm_imgtransfer_testkanal.cc
    ofdm_interp_cir_set_noncir_to_zero.cc
    ofdm_itpp_tdl_channel.cc
    ofdm_limit_vff.cc
    ofdm_lms_fir_ff.cc
    ofdm_lms_phase_tracking.cc
    ofdm_LMS_phase_tracking2.cc
    ofdm_LMS_phase_tracking3.cc
    ofdm_LS_estimator_straight_slope.cc
    ofdm_mean_squared_error.cc
    ofdm_mm_frequency_estimator.cc
    ofdm_moms_cc.cc
    ofdm_moms_ff.cc
    ofdm_multiply_const_vcc.cc
    ofdm_multiply_const_ccf.cc
    ofdm_normalize_vcc.cc
    ofdm_noise_nulling.cc
    ofdm_peak_detector2_fb.cc
    ofdm_peak_resync_bb.cc
    ofdm_pilot_subcarrier_inserter.cc
    ofdm_postprocess_CTF_estimate.cc
    ofdm_reassemble_ofdm_frame.cc
    ofdm_reference_data_source_ib.cc
    ofdm_repetition_encoder_sb.cc
    ofdm_repetition_decoder_bs.cc
    ofdm_scatterplot_sink.cc
    ofdm_schmidl_cfo_estimator.cc
    ofdm_schmidl_tm_rec_stage1.cc
    ofdm_schmidl_tm_rec_stage2.cc
    ofdm_sc_snr_estimator.cc
    ofdm_sinr_estimator2.cc
    ofdm_sinr_estimator.cc
    ofdm_sinr_interpolator.cc
    ofdm_skip.cc
    ofdm_snr_estimator.cc
    ofdm_static_mux_v.cc
    ofdm_static_mux_c.cc
    ofdm_sqrt_vff.cc
    ofdm_stream_controlled_mux.cc
    ofdm_stream_controlled_mux_b.cc
    ofdm_suppress_erasure_decision.cc
    ofdm_throughput_measure.cc
    ofdm_trigger_surveillance.cc
    ofdm_vector_element.cc
    ofdm_vector_mask.cc
    ofdm_vector_padding.cc
    ofdm_vector_sampler.cc
    ofdm_vector_sum_vcc.cc
    ofdm_vector_sum_vff.cc
    ofdm_bernoulli_bit_src.cc
    ofdm_complex_white_noise.cc
    ofdmi_shared_generator.cc
    ofdm_symbol_random_src.cc
    ofdmi_mod.cc
    util_random.cc
    util_endian.cc
    util_bmp.cc
    util_ipc.cc
    corba_push_consumer.cc
    corba_push_supplier.cc
    corba_push_supplier_wrapper.cc
    ofdm_corba_assignment_src_sv.cc
    ofdm_corba_bitcount_src_si.cc
    ofdm_corba_bitmap_src.cc
    ofdm_corba_id_filter.cc
    ofdm_corba_id_src_s.cc
    ofdm_corba_map_src_sv.cc
    ofdm_corba_multiplex_src_ss.cc
    ofdm_corba_power_allocator.cc
    ofdm_corba_power_src_sv.cc
    ofdm_corba_rxinfo_sink.cc
    ofdm_corba_rxinfo_sink_imgxfer.cc
    ofdm_corba_rxbaseband_sink.cc
    orb.cc
    #${CMAKE_BINARY_DIR}/tao_skeleton/libtao_ofdmti.a
)
target_link_libraries(gnuradio-ofdm 
    ${Boost_LIBRARIES}
    ${GRUEL_LIBRARIES}
    ${GNURADIO_CORE_LIBRARIES}
    ${ITPP_LIBRARIES}
    ${TAO_LIBRARIES}
    # "-Wl,--whole-archive"
     ${CMAKE_BINARY_DIR}/tao_skeleton/libtao_ofdmti.a
    #"-Wl,--no-whole-archive"
    )
    
  add_dependencies(gnuradio-ofdm tao_ofdmti)
    message(STATUS "Boost_LIBRARIES at: ${Boost_LIBRARIES}")
    #message(STATUS "GNURADIO_CORE_LIBRARIES at: ${GNURADIO_CORE_LIBRARIES}")
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

########################################################################
# Build and register unit test
########################################################################
find_package(Boost COMPONENTS unit_test_framework)

include(GrTest)
set(GR_TEST_TARGET_DEPS gnuradio-ofdm)
#turn each test cpp file into an executable with an int main() function
add_definitions(-DBOOST_TEST_DYN_LINK -DBOOST_TEST_MAIN)

add_executable(qa_ofdm_template_ff qa_ofdm_template_ff.cc)
target_link_libraries(qa_ofdm_template_ff gnuradio-ofdm ${Boost_LIBRARIES})
GR_ADD_TEST(qa_ofdm_template_ff qa_ofdm_template_ff)
