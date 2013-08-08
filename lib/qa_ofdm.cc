/*
 * Copyright 2012 Free Software Foundation, Inc.
 *
 * This file is part of GNU Radio
 *
 * GNU Radio is free software; you can redistribute it and/or modify
 * it under the terms of the GNU General Public License as published by
 * the Free Software Foundation; either version 3, or (at your option)
 * any later version.
 *
 * GNU Radio is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 * GNU General Public License for more details.
 *
 * You should have received a copy of the GNU General Public License
 * along with GNU Radio; see the file COPYING.  If not, write to
 * the Free Software Foundation, Inc., 51 Franklin Street,
 * Boston, MA 02110-1301, USA.
 */

/*
 * This class gathers together all the test cases for the gr-filter
 * directory into a single test suite.  As you create new test cases,
 * add them here.
 */

#include "qa_ofdm.h"
#include "qa_accumulator_cc.h"
#include "qa_autocorrelator_stage1.h"
#include "qa_autocorrelator_stage2.h"
#include "qa_accumulator_ff.h"
#include "qa_autocorrelator0.h"
#include "qa_ber_measurement.h"
#include "qa_bernoulli_bit_src.h"
#include "qa_bit_position_dependent_ber.h"
#include "qa_channel_equalizer_mimo_2.h"
#include "qa_channel_equalizer_mimo_3.h"
#include "qa_channel_equalizer_mimo.h"
#include "qa_channel_equalizer.h"
#include "qa_channel_estimator_01.h"
#include "qa_channel_estimator_02.h"
#include "qa_coded_bpsk_soft_decoder.h"
//#include "qa_compat_read_ber_from_imgxfer.h"
//#include "qa_imgtransfer_sink.h"
#include "qa_imgtransfer_src.h"
#include "qa_complex_to_arg.h"
#include "qa_complex_white_noise.h"
#include "qa_constellation_sample_filter.h"
#include "qa_CTF_MSE_enhancer.h"
#include "qa_cyclic_prefixer.h"
#include "qa_depuncture_bb.h"
#include "qa_depuncture_ff.h"
#include "qa_dominiks_sync_01.h"
#include "qa_dynamic_trigger_ib.h"
#include "qa_extract_block_from_frame.h"
#include "qa_find_cir_shift.h"
#include "qa_frame_mux.h"
#include "qa_frequency_shift_vcc.h"
#include "qa_gate_ff.h"
#include "qa_generic_mapper_bcv.h"
#include "qa_generic_demapper_vcb.h"
#include "qa_generic_mapper_mimo_bcv.h"

#include "qa_generic_softdemapper_vcf.h"
#include "qa_int_skip.h"
#include "qa_interp_cir_set_noncir_to_zero.h"
#include "qa_limit_vff.h"
#include "qa_lms_fir_ff.h"
#include "qa_lms_phase_tracking.h"
#include "qa_lms_phase_tracking_02.h"
#include "qa_lms_phase_tracking_03.h"
#include "qa_ls_estimator_straight_slope.h"
#include "qa_mean_squared_error.h"
#include "qa_mm_frequency_estimator.h"
#include "qa_moms_cc.h"
#include "qa_moms_ff.h"
#include "qa_multiply_const_ccf.h"
#include "qa_multiply_const_ii.h"
#include "qa_multiply_const_vcc.h"
#include "qa_noise_nulling.h"
#include "qa_normalize_vcc.h"
#include "qa_peak_detector_02_fb.h"
#include "qa_peak_resync_bb.h"
#include "qa_pilot_subcarrier_inserter.h"
#include "qa_postprocess_CTF_estimate.h"
#include "qa_puncture_bb.h"
#include "qa_reassemble_ofdm_frame.h"
#include "qa_reference_data_source_ib.h"
#include "qa_reference_data_source_mimo_ib.h"
#include "qa_repetition_decoder_bs.h"
#include "qa_repetition_encoder_sb.h"
#include "qa_subc_snr_estimator.h"
#include "qa_scatterplot_sink.h"
#include "qa_schmidl_cfo_estimator.h"
#include "qa_schmidl_tm_rec_stage1.h"
#include "qa_schmidl_tm_rec_stage2.h"
#include "qa_sinr_estimator.h"
#include "qa_sinr_estimator_02.h"
#include "qa_sinr_interpolator.h"
#include "qa_skip.h"
#include "qa_snr_estimator.h"
#include "qa_sqrt_vff.h"
#include "qa_static_mux_c.h"
#include "qa_static_mux_v.h"
#include "qa_stc_decoder_rx0.h"
#include "qa_stc_decoder_rx1.h"
#include "qa_stc_encoder.h"
#include "qa_stream_controlled_mux_b.h"
#include "qa_stream_controlled_mux.h"
#include "qa_suppress_erasure_decision.h"
#include "qa_symbol_random_src.h"
#include "qa_trigger_surveillance.h"
#include "qa_vector_padding.h"
#include "qa_vector_mask.h"
#include "qa_vector_element.h"
#include "qa_vector_sampler.h"
#include "qa_vector_sum_vcc.h"
#include "qa_vector_sum_vff.h"
#include "qa_viterbi_combined_fb.h"

CppUnit::TestSuite *
qa_ofdm::suite()
{
  CppUnit::TestSuite *s = new CppUnit::TestSuite("ofdm");
  s->addTest(gr::ofdm::qa_accumulator_cc::suite());
  s->addTest(gr::ofdm::qa_autocorrelator_stage1::suite());
  s->addTest(gr::ofdm::qa_autocorrelator_stage2::suite());
  s->addTest(gr::ofdm::qa_accumulator_ff::suite());
  s->addTest(gr::ofdm::qa_autocorrelator0::suite());
  s->addTest(gr::ofdm::qa_ber_measurement::suite());
  s->addTest(gr::ofdm::qa_bernoulli_bit_src::suite());
  s->addTest(gr::ofdm::qa_bit_position_dependent_ber::suite());
  s->addTest(gr::ofdm::qa_channel_equalizer_mimo_2::suite());
  s->addTest(gr::ofdm::qa_channel_equalizer_mimo_3::suite());
  s->addTest(gr::ofdm::qa_channel_equalizer_mimo::suite());
  s->addTest(gr::ofdm::qa_channel_equalizer::suite());
  s->addTest(gr::ofdm::qa_channel_estimator_01::suite());
  s->addTest(gr::ofdm::qa_channel_estimator_02::suite());
  s->addTest(gr::ofdm::qa_coded_bpsk_soft_decoder::suite());
  //s->addTest(gr::ofdm::qa_compat_read_ber_from_imgxfer::suite());
 // s->addTest(gr::ofdm::qa_imgtransfer_sink::suite());
  s->addTest(gr::ofdm::qa_imgtransfer_src::suite());
  s->addTest(gr::ofdm::qa_complex_to_arg::suite());
  s->addTest(gr::ofdm::qa_complex_white_noise::suite());
  s->addTest(gr::ofdm::qa_constellation_sample_filter::suite());
  s->addTest(gr::ofdm::qa_CTF_MSE_enhancer::suite());
  s->addTest(gr::ofdm::qa_cyclic_prefixer::suite());
  s->addTest(gr::ofdm::qa_depuncture_bb::suite());
  s->addTest(gr::ofdm::qa_depuncture_ff::suite());
  s->addTest(gr::ofdm::qa_dominiks_sync_01::suite());
  s->addTest(gr::ofdm::qa_dynamic_trigger_ib::suite());
  s->addTest(gr::ofdm::qa_extract_block_from_frame::suite());
  s->addTest(gr::ofdm::qa_find_cir_shift::suite());
  s->addTest(gr::ofdm::qa_frame_mux::suite());
  s->addTest(gr::ofdm::qa_frequency_shift_vcc::suite());
  s->addTest(gr::ofdm::qa_gate_ff::suite());
  s->addTest(gr::ofdm::qa_generic_mapper_bcv::suite());
  s->addTest(gr::ofdm::qa_generic_demapper_vcb::suite());
  s->addTest(gr::ofdm::qa_generic_mapper_mimo_bcv::suite());

  s->addTest(gr::ofdm::qa_generic_softdemapper_vcf::suite());
  s->addTest(gr::ofdm::qa_int_skip::suite());
  s->addTest(gr::ofdm::qa_interp_cir_set_noncir_to_zero::suite());
  s->addTest(gr::ofdm::qa_limit_vff::suite());
  s->addTest(gr::ofdm::qa_lms_fir_ff::suite());
  s->addTest(gr::ofdm::qa_lms_phase_tracking::suite());
  s->addTest(gr::ofdm::qa_lms_phase_tracking_02::suite());
  s->addTest(gr::ofdm::qa_lms_phase_tracking_03::suite());
  s->addTest(gr::ofdm::qa_ls_estimator_straight_slope::suite());
  s->addTest(gr::ofdm::qa_mean_squared_error::suite());
  s->addTest(gr::ofdm::qa_mm_frequency_estimator::suite());
  s->addTest(gr::ofdm::qa_moms_cc::suite());
  s->addTest(gr::ofdm::qa_moms_ff::suite());
  s->addTest(gr::ofdm::qa_multiply_const_ccf::suite());
  s->addTest(gr::ofdm::qa_multiply_const_ii::suite());
  s->addTest(gr::ofdm::qa_multiply_const_vcc::suite());
  s->addTest(gr::ofdm::qa_noise_nulling::suite());
  s->addTest(gr::ofdm::qa_normalize_vcc::suite());
  s->addTest(gr::ofdm::qa_peak_detector_02_fb::suite());
  s->addTest(gr::ofdm::qa_peak_resync_bb::suite());
  s->addTest(gr::ofdm::qa_pilot_subcarrier_inserter::suite());
  s->addTest(gr::ofdm::qa_postprocess_CTF_estimate::suite());
  s->addTest(gr::ofdm::qa_puncture_bb::suite());
  s->addTest(gr::ofdm::qa_reassemble_ofdm_frame::suite());
  s->addTest(gr::ofdm::qa_reference_data_source_ib::suite());
  s->addTest(gr::ofdm::qa_reference_data_source_mimo_ib::suite());
  s->addTest(gr::ofdm::qa_repetition_decoder_bs::suite());
  s->addTest(gr::ofdm::qa_repetition_encoder_sb::suite());
  s->addTest(gr::ofdm::qa_subc_snr_estimator::suite());
  s->addTest(gr::ofdm::qa_scatterplot_sink::suite());
  s->addTest(gr::ofdm::qa_schmidl_cfo_estimator::suite());
  s->addTest(gr::ofdm::qa_schmidl_tm_rec_stage1::suite());
  s->addTest(gr::ofdm::qa_schmidl_tm_rec_stage2::suite());
  s->addTest(gr::ofdm::qa_sinr_estimator::suite());
  s->addTest(gr::ofdm::qa_sinr_estimator_02::suite());
  s->addTest(gr::ofdm::qa_sinr_interpolator::suite());
  s->addTest(gr::ofdm::qa_skip::suite());
  s->addTest(gr::ofdm::qa_snr_estimator::suite());
  s->addTest(gr::ofdm::qa_sqrt_vff::suite());
  s->addTest(gr::ofdm::qa_static_mux_c::suite());
  s->addTest(gr::ofdm::qa_static_mux_v::suite());
  s->addTest(gr::ofdm::qa_stc_decoder_rx0::suite());
  s->addTest(gr::ofdm::qa_stc_decoder_rx1::suite());
  s->addTest(gr::ofdm::qa_stc_encoder::suite());
  s->addTest(gr::ofdm::qa_stream_controlled_mux_b::suite());
  s->addTest(gr::ofdm::qa_stream_controlled_mux::suite());
  s->addTest(gr::ofdm::qa_suppress_erasure_decision::suite());
  s->addTest(gr::ofdm::qa_symbol_random_src::suite());
  s->addTest(gr::ofdm::qa_trigger_surveillance::suite());
  s->addTest(gr::ofdm::qa_vector_padding::suite());
  s->addTest(gr::ofdm::qa_vector_mask::suite());
  s->addTest(gr::ofdm::qa_vector_element::suite());
  s->addTest(gr::ofdm::qa_vector_sampler::suite());
  s->addTest(gr::ofdm::qa_vector_sum_vcc::suite());
  s->addTest(gr::ofdm::qa_vector_sum_vff::suite());
  s->addTest(gr::ofdm::qa_viterbi_combined_fb::suite());

  return s;
}
