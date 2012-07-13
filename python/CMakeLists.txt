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
    FILES
    __init__.py
    channel.py
    common_options.py
    configparse.py
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
    schmidl.py
    snr_estimator.py
    station_configuration.py
    vector_equalizer.py
    DESTINATION ${GR_PYTHON_DIR}/ofdm
)

########################################################################
# Handle the unit tests
########################################################################
include(GrTest)

set(GR_TEST_TARGET_DEPS gnuradio-ofdm)
set(GR_TEST_PYTHON_DIRS ${CMAKE_BINARY_DIR}/swig)
GR_ADD_TEST(qa_ofdm ${PYTHON_EXECUTABLE} ${CMAKE_CURRENT_SOURCE_DIR}/qa_ofdm.py)
GR_ADD_TEST(qa_ber_measurement ${PYTHON_EXECUTABLE} ${CMAKE_CURRENT_SOURCE_DIR}/qa_ber_measurement.py)
GR_ADD_TEST(qa_bernoulli_bit_src ${PYTHON_EXECUTABLE} ${CMAKE_CURRENT_SOURCE_DIR}/qa_bernoulli_bit_src.py)
GR_ADD_TEST(qa_cfo_estimator ${PYTHON_EXECUTABLE} ${CMAKE_CURRENT_SOURCE_DIR}/qa_cfo_estimator.py)
GR_ADD_TEST(qa_channel_model ${PYTHON_EXECUTABLE} ${CMAKE_CURRENT_SOURCE_DIR}/qa_channel_model.py)
GR_ADD_TEST(qa_bit_position_dependent_BER ${PYTHON_EXECUTABLE} ${CMAKE_CURRENT_SOURCE_DIR}/qa_bit_position_dependent_BER.py)
GR_ADD_TEST(qa_channel_equalizer ${PYTHON_EXECUTABLE} ${CMAKE_CURRENT_SOURCE_DIR}/qa_channel_equalizer.py)
GR_ADD_TEST(qa_complex_white_noise ${PYTHON_EXECUTABLE} ${CMAKE_CURRENT_SOURCE_DIR}/qa_complex_white_noise.py)
GR_ADD_TEST(qa_demapper ${PYTHON_EXECUTABLE} ${CMAKE_CURRENT_SOURCE_DIR}/qa_demapper.py)
GR_ADD_TEST(qa_dynamic_trigger ${PYTHON_EXECUTABLE} ${CMAKE_CURRENT_SOURCE_DIR}/qa_dynamic_trigger.py)
GR_ADD_TEST(qa_frame_mux ${PYTHON_EXECUTABLE} ${CMAKE_CURRENT_SOURCE_DIR}/qa_frame_mux.py)
GR_ADD_TEST(qa_freqshift ${PYTHON_EXECUTABLE} ${CMAKE_CURRENT_SOURCE_DIR}/qa_freqshift.py)
GR_ADD_TEST(qa_LMS_phase_tracking2 ${PYTHON_EXECUTABLE} ${CMAKE_CURRENT_SOURCE_DIR}/qa_LMS_phase_tracking2.py)
GR_ADD_TEST(qa_mean_squared_error ${PYTHON_EXECUTABLE} ${CMAKE_CURRENT_SOURCE_DIR}/qa_mean_squared_error.py)
GR_ADD_TEST(qa_modulation ${PYTHON_EXECUTABLE} ${CMAKE_CURRENT_SOURCE_DIR}/qa_modulation.py)
GR_ADD_TEST(qa_multiply_const_ccf ${PYTHON_EXECUTABLE} ${CMAKE_CURRENT_SOURCE_DIR}/qa_multiply_const_ccf.py)
GR_ADD_TEST(qa_multiply_const_vcc ${PYTHON_EXECUTABLE} ${CMAKE_CURRENT_SOURCE_DIR}/qa_multiply_const_vcc.py)
GR_ADD_TEST(qa_peakdetector ${PYTHON_EXECUTABLE} ${CMAKE_CURRENT_SOURCE_DIR}/qa_peakdetector.py)
GR_ADD_TEST(qa_pilot_subcarrier_filter ${PYTHON_EXECUTABLE} ${CMAKE_CURRENT_SOURCE_DIR}/qa_pilot_subcarrier_filter.py)
GR_ADD_TEST(qa_postprocess_CTF_estimate ${PYTHON_EXECUTABLE} ${CMAKE_CURRENT_SOURCE_DIR}/qa_postprocess_CTF_estimate.py)
GR_ADD_TEST(qa_reassemble_ofdm_frame ${PYTHON_EXECUTABLE} ${CMAKE_CURRENT_SOURCE_DIR}/qa_reassemble_ofdm_frame.py)
GR_ADD_TEST(qa_repetition_encoder_decoder ${PYTHON_EXECUTABLE} ${CMAKE_CURRENT_SOURCE_DIR}/qa_repetition_encoder_decoder.py)
GR_ADD_TEST(qa_sampler ${PYTHON_EXECUTABLE} ${CMAKE_CURRENT_SOURCE_DIR}/qa_sampler.py)
GR_ADD_TEST(qa_sinr_estimator ${PYTHON_EXECUTABLE} ${CMAKE_CURRENT_SOURCE_DIR}/qa_sinr_estimator.py)
GR_ADD_TEST(qa_skip ${PYTHON_EXECUTABLE} ${CMAKE_CURRENT_SOURCE_DIR}/qa_skip.py)
GR_ADD_TEST(qa_snr_estimator ${PYTHON_EXECUTABLE} ${CMAKE_CURRENT_SOURCE_DIR}/qa_snr_estimator.py)
GR_ADD_TEST(qa_static_mux ${PYTHON_EXECUTABLE} ${CMAKE_CURRENT_SOURCE_DIR}/qa_static_mux.py)
GR_ADD_TEST(qa_stream_controlled_mux ${PYTHON_EXECUTABLE} ${CMAKE_CURRENT_SOURCE_DIR}/qa_stream_controlled_mux.py)
GR_ADD_TEST(qa_vector_element ${PYTHON_EXECUTABLE} ${CMAKE_CURRENT_SOURCE_DIR}/qa_vector_element.py)
GR_ADD_TEST(qa_vector_sum ${PYTHON_EXECUTABLE} ${CMAKE_CURRENT_SOURCE_DIR}/qa_vector_sum.py)
