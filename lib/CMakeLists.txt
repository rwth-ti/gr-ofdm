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

add_library(gnuradio-ofdm SHARED 
    ofdm_cube_ff.cc 
    ofdm_power4_ff.cc 
    ofdm_new_ff.cc 
    ofdm_accumulator_cc.cc 
    ofdm_accumulator_ff.cc
    ofdm_autocorrelator.cc
    ofdm_autocorrelator_stage1.cc
    ofdm_autocorrelator_stage2.cc
    ofdm_ber_measurement.cc
    ofdm_bit_position_dependent_BER.cc
    ofdm_channel_equalizer.cc
    ofdm_channel_estimator_01.cc
    ofdm_channel_estimator_02.cc
    ofdm_coded_bpsk_soft_decoder.cc
    ofdm_compat_read_ber_from_imgxfer.cc
    ofdm_complex_to_arg.cc
    ofdm_imgtransfer_sink.cc
    ofdm_constellation_sample_filter.cc
#    ofdm_CTF_MSE_enhancer.cc
    ofdm_dominiks_sync_01.cc
    ofdm_dynamic_trigger_ib.cc
    ofdm_cyclic_prefixer.cc
    ofdm_extract_block_from_frame.cc
    #    ofdm_find_cir_shift.cc
    ofdm_frame_mux.cc
    ofdm_frequency_shift_vcc.cc
    ofdm_generic_mapper_bcv.cc
    ofdm_gate_ff.cc
    ofdm_generic_demapper_vcb.cc
    ofdm_get_zeros.cc
    ofdm_imgtransfer_src.cc
    ofdm_imgtransfer_testkanal.cc
    ofdm_interp_cir_set_noncir_to_zero.cc
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
    #ofdm_peak_detector_fb.cc
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
    #    ofdm_schmidl_tm_s1.cc
    #    ofdm_schmidl_tm_s2.cc
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
    ofdmi_mod.cc
    util_random.cc
    util_endian.cc
    util_bmp.cc
    util_ipc.cc
)
target_link_libraries(gnuradio-ofdm ${Boost_LIBRARIES} ${GRUEL_LIBRARIES} ${GNURADIO_CORE_LIBRARIES})
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

add_executable(qa_ofdm_cube_ff qa_ofdm_cube_ff.cc)
target_link_libraries(qa_ofdm_cube_ff gnuradio-ofdm ${Boost_LIBRARIES})
GR_ADD_TEST(qa_ofdm_cube_ff qa_ofdm_cube_ff)

add_executable(qa_ofdm_power4_ff qa_ofdm_power4_ff.cc)
target_link_libraries(qa_ofdm_power4_ff gnuradio-ofdm ${Boost_LIBRARIES})
GR_ADD_TEST(qa_ofdm_power4_ff qa_ofdm_power4_ff)

add_executable(qa_ofdm_new_ff qa_ofdm_new_ff.cc)
target_link_libraries(qa_ofdm_new_ff gnuradio-ofdm ${Boost_LIBRARIES})
GR_ADD_TEST(qa_ofdm_new_ff qa_ofdm_new_ff)

#add_executable(qa_ofdm_accumulator_cc qa_ofdm_accumulator_cc.cc)
#target_link_libraries(qa_ofdm_accumulator_cc gnuradio-ofdm ${Boost_LIBRARIES})
#GR_ADD_TEST(qa_ofdm_accumulator_cc qa_ofdm_accumulator_cc)
