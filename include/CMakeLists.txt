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
# Install public header files
########################################################################
install(FILES
    ofdm_api.h
    ofdm_cube_ff.h
    ofdm_power4_ff.h
    ofdm_new_ff.h
    ofdm_accumulator_cc.h
    ofdm_accumulator_ff.h
    ofdm_autocorrelator0.h
    ofdm_autocorrelator_stage1.h
    ofdm_autocorrelator_stage2.h
    ofdm_ber_measurement.h
    ofdm_bit_position_dependent_BER.h
    ofdm_channel_equalizer.h
    ofdm_channel_estimator_01.h
    ofdm_channel_estimator_02.h
    ofdm_coded_bpsk_soft_decoder.h
    ofdm_compat_read_ber_from_imgxfer.h
    ofdm_complex_to_arg.h
    ofdm_imgtransfer_sink.h
    ofdm_constellation_sample_filter.h
    ofdm_CTF_MSE_enhancer.h
    ofdm_dominiks_sync_01.h
    ofdm_dynamic_trigger_ib.h
    ofdm_cyclic_prefixer.h
    ofdm_extract_block_from_frame.h
    ofdm_find_cir_shift.h
    ofdm_frequency_shift_vcc.h
    ofdm_generic_mapper_bcv.h
    ofdm_gate_ff.h
    ofdm_frame_mux.h
    ofdmi_fast_math.h
    ofdmi_mod.h
    ofdm_generic_demapper_vcb.h
    ofdm_get_zeros.h
    ofdm_imgtransfer_src.h
    ofdm_imgtransfer_testkanal.h
    ofdm_interp_cir_set_noncir_to_zero.h
    ofdm_limit_vff.h
    ofdm_lms_fir_ff.h
    ofdm_lms_phase_tracking.h
    ofdm_LMS_phase_tracking2.h
    ofdm_LMS_phase_tracking3.h
    ofdmi_tictoc.hpp
    ofdm_LS_estimator_straight_slope.h
    ofdm_mean_squared_error.h
    ofdm_mm_frequency_estimator.h
    ofdm_moms_cc.h
    ofdm_moms_ff.h
    ofdm_multiply_const_vcc.h
    ofdm_multiply_const_ccf.h
    ofdm_noise_nulling.h
    ofdm_normalize_vcc.h
    ofdm_peak_detector2_fb.h
    ofdm_peak_resync_bb.h
    ofdm_pilot_subcarrier_inserter.h
    ofdm_postprocess_CTF_estimate.h
    ofdm_reassemble_ofdm_frame.h
    ofdm_reference_data_source_ib.h
    ofdm_repetition_decoder_bs.h
    ofdm_repetition_encoder_sb.h
    ofdm_scatterplot_sink.h
    ofdm_schmidl_cfo_estimator.h
    ofdm_schmidl_tm_rec_stage1.h
    ofdm_schmidl_tm_rec_stage2.h
    ofdm_sc_snr_estimator.h
    ofdm_sinr_estimator2.h
    ofdm_sinr_estimator.h
    ofdm_sinr_interpolator.h
    ofdm_skip.h
    ofdm_snr_estimator.h
    ofdm_static_mux_c.h
    ofdm_static_mux_v.h
    ofdm_sqrt_vff.h
    ofdm_stream_controlled_mux.h
    ofdm_stream_controlled_mux_b.h
    ofdm_suppress_erasure_decision.h
    ofdm_throughput_measure.h
    ofdm_trigger_surveillance.h
    ofdm_vector_element.h
    ofdm_vector_mask.h
    ofdm_vector_padding.h
    ofdm_vector_sampler.h
    ofdm_vector_sum_vcc.h
    ofdm_vector_sum_vff.h
    ofdm_bernoulli_bit_src.h
    ofdm_complex_white_noise.h
    ofdmi_shared_generator.h
    ofdm_symbol_random_src.h
    ofdm_itpp_tdl_channel.h
    util_random.h
    util_bmp.h
    util_endian.h
    util_ipc.h
    gr_block_fwd.h
    DESTINATION include/ofdm
)
