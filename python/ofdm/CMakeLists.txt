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
# Include python install macros
########################################################################
include(GrPython)
if(NOT PYTHONINTERP_FOUND)
    return()
endif()

########################################################################
# Install python sources
########################################################################
GR_PYTHON_INSTALL(
    PROGRAMS
    benchmark_ofdm.py
    ofdm_rms_amplifier_grc.py
    fbmc_rms_amplifier_grc.py
    tx_rpc_manager_grc.py
    rx_rpc_manager_grc.py
    fbmc_rms_amplifier_grc.py
    ber_reference_source_grc.py
    fbmc_frame_sampler_grc.py
    ofdm_frame_sampler_grc.py
    preambles_grc.py
    autocorrelator.py
    schmidl.py
    rx.py
    tx.py
    fbmc_insert_preamble_vcvc.py
    fbmc_overlapping_parallel_to_serial_vcc.py
    fbmc_overlapping_serial_to_parallel_cvc.py
    preambles.py
    fbmc_vector_reshape_vcvc.py
    fbmc_remove_preamble_vcvc.py
    fbmc_channel_hier_cc.py
    fbmc_receiver_hier_cb.py
    fbmc_transmitter_hier_bc.py
    fbmc_symbol_estimation_vcb.py
    fbmc_symbol_creation_bvc.py
    fbmc_transmitter_demo.py
    fbmc_receiver_demo.py
    fbmc_transmitter_multiuser_bc.py
    fbmc_receiver_multiuser_cb.py
    scfdma_transmitter_bc.py
    transmit_path.py
    fbmc_transmit_path.py
    scfdma_receiver_cb.py
    fbmc_insert_preamble_mu_vcvc.py DESTINATION bin
)

GR_PYTHON_INSTALL(
    FILES
    configparse.py
    DESTINATION ${GR_PYTHON_DIR}
)

GR_PYTHON_INSTALL(
    FILES
    __init__.py
    autocorrelator.py
    channel.py
    common_options.py
    delaylines.py
    file_psd.py
    fusb_options.py
    gr_tools.py
    moms_general.py
    moms.py
    morelli.py
    ofdm_receiver2.py
    ofdm_receiver.py
    preambles.py
    receive_path.py
    receive_path12.py
    receive_path21.py
    receive_path22_neu.py
    schmidl.py
    snr_estimator.py
    station_configuration.py
    transmit_path2.py
    transmit_path.py
    fbmc_transmit_path.py
    fbmc_receive_path.py
    fbmc_receiver.py
    uhd_interface.py
    vector_equalizer.py
    DESTINATION ${GR_PYTHON_DIR}/ofdm
)


########################################################################
# Handle the unit tests
########################################################################
include(GrTest)

set(GR_TEST_TARGET_DEPS gnuradio-test1)
set(GR_TEST_PYTHON_DIRS ${CMAKE_BINARY_DIR}/swig)
GR_ADD_TEST(qa_multiply_frame_fc ${PYTHON_EXECUTABLE} ${CMAKE_CURRENT_SOURCE_DIR}/qa_multiply_frame_fc.py)
GR_ADD_TEST(qa_vector_padding_dc_null ${PYTHON_EXECUTABLE} ${CMAKE_CURRENT_SOURCE_DIR}/qa_vector_padding_dc_null.py)
GR_ADD_TEST(qa_snr_estimator_dc_null ${PYTHON_EXECUTABLE} ${CMAKE_CURRENT_SOURCE_DIR}/qa_snr_estimator_dc_null.py)
GR_ADD_TEST(qa_vector_mask_dc_null ${PYTHON_EXECUTABLE} ${CMAKE_CURRENT_SOURCE_DIR}/qa_vector_mask_dc_null.py)
GR_ADD_TEST(qa_lms_phase_tracking_dc_null ${PYTHON_EXECUTABLE} ${CMAKE_CURRENT_SOURCE_DIR}/qa_lms_phase_tracking_dc_null.py)
GR_ADD_TEST(qa_midamble_insert ${PYTHON_EXECUTABLE} ${CMAKE_CURRENT_SOURCE_DIR}/qa_midamble_insert.py)
GR_ADD_TEST(qa_fbmc_oqam_preprocessing_vcvc ${PYTHON_EXECUTABLE} ${CMAKE_CURRENT_SOURCE_DIR}/qa_fbmc_oqam_preprocessing_vcvc.py)
GR_ADD_TEST(qa_oqam_preprocessing_vcvc ${PYTHON_EXECUTABLE} ${CMAKE_CURRENT_SOURCE_DIR}/qa_oqam_preprocessing_vcvc.py)
GR_ADD_TEST(qa_fbmc_oqam_preprocessing_vcvc ${PYTHON_EXECUTABLE} ${CMAKE_CURRENT_SOURCE_DIR}/qa_fbmc_oqam_preprocessing_vcvc.py)
GR_ADD_TEST(qa_fbmc_oqam_postprocessing_vcvc ${PYTHON_EXECUTABLE} ${CMAKE_CURRENT_SOURCE_DIR}/qa_fbmc_oqam_postprocessing_vcvc.py)
GR_ADD_TEST(qa_fbmc_insert_preamble_vcvc ${PYTHON_EXECUTABLE} ${CMAKE_CURRENT_SOURCE_DIR}/qa_fbmc_insert_preamble_vcvc.py)
GR_ADD_TEST(qa_fbmc_beta_multiplier_vcvc ${PYTHON_EXECUTABLE} ${CMAKE_CURRENT_SOURCE_DIR}/qa_fbmc_beta_multiplier_vcvc.py)
GR_ADD_TEST(qa_fbmc_separate_vcvc ${PYTHON_EXECUTABLE} ${CMAKE_CURRENT_SOURCE_DIR}/qa_fbmc_separate_vcvc.py)
GR_ADD_TEST(qa_fbmc_polyphase_network_vcvc ${PYTHON_EXECUTABLE} ${CMAKE_CURRENT_SOURCE_DIR}/qa_fbmc_polyphase_network_vcvc.py)
GR_ADD_TEST(qa_fbmc_overlapping_parallel_to_serial_vcc ${PYTHON_EXECUTABLE} ${CMAKE_CURRENT_SOURCE_DIR}/qa_fbmc_overlapping_parallel_to_serial_vcc.py)
GR_ADD_TEST(qa_fbmc_overlapping_serial_to_parallel_cvc ${PYTHON_EXECUTABLE} ${CMAKE_CURRENT_SOURCE_DIR}/qa_fbmc_overlapping_serial_to_parallel_cvc.py)
GR_ADD_TEST(qa_fbmc_vector_reshape_vcvc ${PYTHON_EXECUTABLE} ${CMAKE_CURRENT_SOURCE_DIR}/qa_fbmc_vector_reshape_vcvc.py)
GR_ADD_TEST(qa_fbmc_vector_copy_vcvc ${PYTHON_EXECUTABLE} ${CMAKE_CURRENT_SOURCE_DIR}/qa_fbmc_vector_copy_vcvc.py)
GR_ADD_TEST(qa_fbmc_junction_vcvc ${PYTHON_EXECUTABLE} ${CMAKE_CURRENT_SOURCE_DIR}/qa_fbmc_junction_vcvc.py)
GR_ADD_TEST(qa_fbmc_remove_preamble_vcvc ${PYTHON_EXECUTABLE} ${CMAKE_CURRENT_SOURCE_DIR}/qa_fbmc_remove_preamble_vcvc.py)
GR_ADD_TEST(qa_fbmc_subchannel_processing_vcvc ${PYTHON_EXECUTABLE} ${CMAKE_CURRENT_SOURCE_DIR}/qa_fbmc_subchannel_processing_vcvc.py)
GR_ADD_TEST(qa_fbmc_weighted_spreading_vcvc ${PYTHON_EXECUTABLE} ${CMAKE_CURRENT_SOURCE_DIR}/qa_fbmc_weighted_spreading_vcvc.py)
GR_ADD_TEST(qa_fbmc_weighted_despreading_vcvc ${PYTHON_EXECUTABLE} ${CMAKE_CURRENT_SOURCE_DIR}/qa_fbmc_weighted_despreading_vcvc.py)
GR_ADD_TEST(qa_fbmc_channel_hier_cc ${PYTHON_EXECUTABLE} ${CMAKE_CURRENT_SOURCE_DIR}/qa_fbmc_channel_hier_cc.py)
GR_ADD_TEST(qa_fbmc_receiver_hier_cb ${PYTHON_EXECUTABLE} ${CMAKE_CURRENT_SOURCE_DIR}/qa_fbmc_receiver_hier_cb.py)
GR_ADD_TEST(qa_fbmc_transmitter_hier_bc ${PYTHON_EXECUTABLE} ${CMAKE_CURRENT_SOURCE_DIR}/qa_fbmc_transmitter_hier_bc.py)
GR_ADD_TEST(qa_fbmc_symbol_estimation_vcb ${PYTHON_EXECUTABLE} ${CMAKE_CURRENT_SOURCE_DIR}/qa_fbmc_symbol_estimation_vcb.py)
GR_ADD_TEST(qa_fbmc_symbol_creation_bvc ${PYTHON_EXECUTABLE} ${CMAKE_CURRENT_SOURCE_DIR}/qa_fbmc_symbol_creation_bvc.py)
GR_ADD_TEST(qa_fbmc_transmitter_demo ${PYTHON_EXECUTABLE} ${CMAKE_CURRENT_SOURCE_DIR}/qa_fbmc_transmitter_demo.py)
GR_ADD_TEST(qa_fbmc_receiver_demo ${PYTHON_EXECUTABLE} ${CMAKE_CURRENT_SOURCE_DIR}/qa_fbmc_receiver_demo.py)
GR_ADD_TEST(qa_asymmetrical_vector_padding_cc ${PYTHON_EXECUTABLE} ${CMAKE_CURRENT_SOURCE_DIR}/qa_asymmetrical_vector_padding_cc.py)
GR_ADD_TEST(qa_fbmc_asymmetrical_vector_padding_vcvc ${PYTHON_EXECUTABLE} ${CMAKE_CURRENT_SOURCE_DIR}/qa_fbmc_asymmetrical_vector_padding_vcvc.py)
GR_ADD_TEST(qa_fbmc_transmitter_multiuser_bc ${PYTHON_EXECUTABLE} ${CMAKE_CURRENT_SOURCE_DIR}/qa_fbmc_transmitter_multiuser_bc.py)
GR_ADD_TEST(qa_fbmc_asymmetrical_vector_mask_vcvc ${PYTHON_EXECUTABLE} ${CMAKE_CURRENT_SOURCE_DIR}/qa_fbmc_asymmetrical_vector_mask_vcvc.py)
GR_ADD_TEST(qa_fbmc_receiver_multiuser_cb ${PYTHON_EXECUTABLE} ${CMAKE_CURRENT_SOURCE_DIR}/qa_fbmc_receiver_multiuser_cb.py)
GR_ADD_TEST(qa_scfdma_subcarrier_mapper_vcvc ${PYTHON_EXECUTABLE} ${CMAKE_CURRENT_SOURCE_DIR}/qa_scfdma_subcarrier_mapper_vcvc.py)
GR_ADD_TEST(qa_scfdma_subcarrier_mapper_vcvc ${PYTHON_EXECUTABLE} ${CMAKE_CURRENT_SOURCE_DIR}/qa_scfdma_subcarrier_mapper_vcvc.py)
GR_ADD_TEST(qa_scfdma_transmitter_bc ${PYTHON_EXECUTABLE} ${CMAKE_CURRENT_SOURCE_DIR}/qa_scfdma_transmitter_bc.py)
GR_ADD_TEST(qa_scfdma_subcarrier_demapper_vcvc ${PYTHON_EXECUTABLE} ${CMAKE_CURRENT_SOURCE_DIR}/qa_scfdma_subcarrier_demapper_vcvc.py)
GR_ADD_TEST(qa_scfdma_receiver_cb ${PYTHON_EXECUTABLE} ${CMAKE_CURRENT_SOURCE_DIR}/qa_scfdma_receiver_cb.py)
GR_ADD_TEST(qa_add_vcc ${PYTHON_EXECUTABLE} ${CMAKE_CURRENT_SOURCE_DIR}/qa_add_vcc.py)
GR_ADD_TEST(qa_fbmc_insert_preamble_mu_vcvc ${PYTHON_EXECUTABLE} ${CMAKE_CURRENT_SOURCE_DIR}/qa_fbmc_insert_preamble_mu_vcvc.py)
GR_ADD_TEST(qa_fbmc_subchannel_processing_mu_vcvc ${PYTHON_EXECUTABLE} ${CMAKE_CURRENT_SOURCE_DIR}/qa_fbmc_subchannel_processing_mu_vcvc.py)
