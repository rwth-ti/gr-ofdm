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
# Install public header files
########################################################################
install(FILES
    api.h
    accumulator_cc.h
    autocorrelator_stage1.h
    autocorrelator_stage2.h
    accumulator_ff.h
    autocorrelator0.h
    base.h
    ber_measurement.h
    bernoulli_bit_src.h
    ofdmi_shared_generator.h
    ofdmi_fast_math.h
    ofdmi_mod.h
    bit_position_dependent_ber.h
    calc_metric.h
    channel_equalizer_mimo_2.h
    channel_equalizer_mimo_3.h
    channel_equalizer_mimo.h
    channel_equalizer.h
    channel_estimator_01.h
    channel_estimator_02.h
    coded_bpsk_soft_decoder.h
    compat_read_ber_from_imgxfer.h
    imgtransfer_sink.h
    util_random.h
    util_endian.h
    util_bmp.h
    util_ipc.h
    imgtransfer_src.h
    imgtransfer_testkanal.h
    complex_to_arg.h
    complex_white_noise.h
    constellation_sample_filter.h
    CTF_MSE_enhancer.h
    cyclic_prefixer.h
    depuncture_bb.h
    depuncture_ff.h
    time_sync.h
    dynamic_trigger_ib.h
    extract_block_from_frame.h
    find_cir_shift.h
    frame_mux.h
    frequency_shift_vcc.h
    gate_ff.h
    generic_mapper_bcv.h
    generic_demapper_vcb.h
    generic_mapper_mimo_bcv.h
    generic_softdemapper_vcf.h
    int_skip.h
    interp_cir_set_noncir_to_zero.h
    limit_vff.h
    lms_fir_ff.h
    lms_phase_tracking.h
    lms_phase_tracking_02.h
    lms_phase_tracking_03.h
    ls_estimator_straight_slope.h
    mean_squared_error.h
    mm_frequency_estimator.h
    moms_cc.h
    moms_ff.h
    multiply_frame_fc.h
    divide_frame_fc.h
    multiply_const_ccf.h
    multiply_const_ii.h
    multiply_const_vcc.h
    noise_nulling.h
    normalize_vcc.h
    peak_detector_02_fb.h
    peak_resync_bb.h
    pilot_subcarrier_inserter.h
    postprocess_CTF_estimate.h
    puncture_bb.h
    reassemble_ofdm_frame.h
    reference_data_source_ib.h
    reference_data_source_mimo_ib.h
    repetition_decoder_bs.h
    repetition_encoder_sb.h
    subc_snr_estimator.h
    scatterplot_sink.h
    schmidl_cfo_estimator.h
    schmidl_tm_rec_stage1.h
    schmidl_tm_rec_stage2.h
    sinr_estimator.h
    sinr_estimator_02.h
    sinr_interpolator.h
    skip.h
    snr_estimator.h
    sqrt_vff.h
    static_mux_c.h
    static_mux_v.h
    stc_decoder_rx0.h
    stc_decoder_rx1.h
    stc_encoder.h
    stream_controlled_mux_b.h
    stream_controlled_mux.h
    suppress_erasure_decision.h
    symbol_random_src.h
    throughput_measure.h
    trigger_surveillance.h
    vector_padding.h
    vector_mask.h
    vector_element.h
    vector_sampler.h
    vector_sum_vcc.h
    vector_sum_vff.h
    viterbi_combined_fb.h
    fsm.h
    itpp_tdl_channel.h
    encoder_bb.h
    reference_data_source_02_ib.h
    allocation_src.h
    allocation_buffer.h
    tx_mux_ctrl.h
    midamble_insert.h 
    fbmc_oqam_preprocessing_vcvc.h
    fbmc_oqam_postprocessing_vcvc.h
    fbmc_beta_multiplier_vcvc.h
    fbmc_separate_vcvc.h
    fbmc_polyphase_network_vcvc.h
    fbmc_vector_copy_vcvc.h
    fbmc_junction_vcvc.h
    fbmc_subchannel_processing_vcvc.h
    fbmc_weighted_spreading_vcvc.h
    fbmc_weighted_despreading_vcvc.h 
    DESTINATION include/ofdm
)
