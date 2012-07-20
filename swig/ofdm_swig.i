/* -*- c++ -*- */

#define OFDM_API
#define __attribute__(x)

%include "gnuradio.i"			// the common stuff

//load generated python docstrings
%include "ofdm_swig_doc.i"

%{
#include "ofdm_api.h"
#include "ofdm_template_ff.h"
#include "ofdm_accumulator_cc.h"
#include "ofdm_accumulator_ff.h"
#include "ofdm_autocorrelator.h"
#include "ofdm_autocorrelator_stage1.h"
#include "ofdm_autocorrelator_stage2.h"
#include "ofdm_ber_measurement.h"
#include "ofdm_bit_position_dependent_BER.h"
#include "ofdm_channel_equalizer.h"
#include "ofdm_channel_estimator_01.h"
#include "ofdm_channel_estimator_02.h"
#include "ofdm_coded_bpsk_soft_decoder.h"
#include "ofdm_compat_read_ber_from_imgxfer.h"
#include "ofdm_complex_to_arg.h"
#include "ofdm_imgtransfer_sink.h"
#include "ofdm_constellation_sample_filter.h"
#include "ofdm_CTF_MSE_enhancer.h"
#include "ofdm_cyclic_prefixer.h"
#include "ofdm_dominiks_sync_01.h"
#include "ofdm_dynamic_trigger_ib.h"
#include "ofdm_extract_block_from_frame.h"
#include "ofdm_find_cir_shift.h"
#include "ofdm_frame_mux.h"
#include "ofdm_frequency_shift_vcc.h"
#include "ofdm_generic_mapper_bcv.h"
#include "ofdm_gate_ff.h"
#include "ofdm_get_zeros.h"
#include "ofdm_generic_demapper_vcb.h"
#include "ofdm_imgtransfer_src.h"
#include "ofdm_imgtransfer_testkanal.h"
#include "ofdm_interp_cir_set_noncir_to_zero.h"
#include "ofdm_limit_vff.h"
#include "ofdm_lms_fir_ff.h"
#include "ofdm_lms_phase_tracking.h"
#include "ofdm_LMS_phase_tracking2.h"
#include "ofdm_LMS_phase_tracking3.h"
#include "ofdm_LS_estimator_straight_slope.h"
#include "ofdm_mean_squared_error.h"
#include "ofdm_mm_frequency_estimator.h"
#include "ofdm_moms_cc.h"
#include "ofdm_moms_ff.h"
#include "ofdm_multiply_const_vcc.h"
#include "ofdm_multiply_const_ccf.h"
#include "ofdm_noise_nulling.h"
#include "ofdm_normalize_vcc.h"
#include "ofdm_peak_detector2_fb.h"
#include "ofdm_peak_resync_bb.h"
#include "ofdm_pilot_subcarrier_inserter.h"
#include "ofdm_postprocess_CTF_estimate.h"
#include "ofdm_reassemble_ofdm_frame.h"
#include "ofdm_reference_data_source_ib.h"
#include "ofdm_repetition_decoder_bs.h"
#include "ofdm_repetition_encoder_sb.h"
#include "ofdm_scatterplot_sink.h"
#include "ofdm_schmidl_cfo_estimator.h"
#include "ofdm_schmidl_tm_rec_stage1.h"
#include "ofdm_schmidl_tm_rec_stage2.h"
#include "ofdm_sc_snr_estimator.h"
#include "ofdm_sinr_estimator2.h"
#include "ofdm_sinr_estimator.h"
#include "ofdm_sinr_interpolator.h"
#include "ofdm_skip.h"
#include "ofdm_snr_estimator.h"
#include "ofdm_static_mux_v.h"
#include "ofdm_static_mux_c.h"
#include "ofdm_sqrt_vff.h"
#include "ofdm_stream_controlled_mux.h"
#include "ofdm_stream_controlled_mux_b.h"
#include "ofdm_suppress_erasure_decision.h"
#include "ofdm_throughput_measure.h"
#include "ofdm_trigger_surveillance.h"
#include "ofdm_vector_element.h"
#include "ofdm_vector_mask.h"
#include "ofdm_vector_padding.h"
#include "ofdm_vector_sampler.h"
#include "ofdm_vector_sum_vcc.h"
#include "ofdm_vector_sum_vff.h"
#include "ofdm_bernoulli_bit_src.h"
#include "ofdm_complex_white_noise.h"
#include "ofdm_symbol_random_src.h"
%}

GR_SWIG_BLOCK_MAGIC(ofdm,template_ff);
%include "ofdm_template_ff.h"

GR_SWIG_BLOCK_MAGIC(ofdm,accumulator_cc);
%include "ofdm_accumulator_cc.h"

GR_SWIG_BLOCK_MAGIC(ofdm,accumulator_ff);
%include "ofdm_accumulator_ff.h"

GR_SWIG_BLOCK_MAGIC(ofdm,autocorrelator);
#include "ofdm_autocorrelator.h"

GR_SWIG_BLOCK_MAGIC(ofdm,autocorrelator_stage1);
%include "ofdm_autocorrelator_stage1.h"

GR_SWIG_BLOCK_MAGIC(ofdm,autocorrelator_stage2);
%include "ofdm_autocorrelator_stage2.h"

GR_SWIG_BLOCK_MAGIC(ofdm,ber_measurement);
%include "ofdm_ber_measurement.h"

GR_SWIG_BLOCK_MAGIC(ofdm,bit_position_dependent_BER);
%include "ofdm_bit_position_dependent_BER.h"

GR_SWIG_BLOCK_MAGIC(ofdm,channel_equalizer);
%include "ofdm_channel_equalizer.h"

GR_SWIG_BLOCK_MAGIC(ofdm,channel_estimator_01);
%include "ofdm_channel_estimator_01.h"

GR_SWIG_BLOCK_MAGIC(ofdm,channel_estimator_02);
%include "ofdm_channel_estimator_02.h"

GR_SWIG_BLOCK_MAGIC(ofdm,coded_bpsk_soft_decoder);
%include "ofdm_coded_bpsk_soft_decoder.h"

GR_SWIG_BLOCK_MAGIC(ofdm,compat_read_ber_from_imgxfer);
%include "ofdm_compat_read_ber_from_imgxfer.h"

GR_SWIG_BLOCK_MAGIC(ofdm,complex_to_arg);
%include "ofdm_complex_to_arg.h"

GR_SWIG_BLOCK_MAGIC(ofdm,imgtransfer_sink);
%include "ofdm_imgtransfer_sink.h"

GR_SWIG_BLOCK_MAGIC(ofdm,constellation_sample_filter);
%include "ofdm_constellation_sample_filter.h"

GR_SWIG_BLOCK_MAGIC(ofdm,CTF_MSE_enhancer);
%include "ofdm_CTF_MSE_enhancer.h"

GR_SWIG_BLOCK_MAGIC(ofdm,cyclic_prefixer);
%include "ofdm_cyclic_prefixer.h"

GR_SWIG_BLOCK_MAGIC(ofdm,dominiks_sync_01);
%include "ofdm_dominiks_sync_01.h"

GR_SWIG_BLOCK_MAGIC(ofdm,dynamic_trigger_ib);
%include "ofdm_dynamic_trigger_ib.h"

GR_SWIG_BLOCK_MAGIC(ofdm,extract_block_from_frame);
%include "ofdm_extract_block_from_frame.h"

GR_SWIG_BLOCK_MAGIC(ofdm,find_cir_shift);
%include "ofdm_find_cir_shift.h"

GR_SWIG_BLOCK_MAGIC(ofdm,frame_mux);
%include "ofdm_frame_mux.h"

GR_SWIG_BLOCK_MAGIC(ofdm,frequency_shift_vcc);
%include "ofdm_frequency_shift_vcc.h"

GR_SWIG_BLOCK_MAGIC(ofdm,generic_mapper_bcv);
%include "ofdm_generic_mapper_bcv.h"

GR_SWIG_BLOCK_MAGIC(ofdm,gate_ff);
%include "ofdm_gate_ff.h"

GR_SWIG_BLOCK_MAGIC(ofdm,generic_demapper_vcb)
%include "ofdm_generic_demapper_vcb.h"

GR_SWIG_BLOCK_MAGIC(ofdm,get_zeros);
%include "ofdm_get_zeros.h"

GR_SWIG_BLOCK_MAGIC(ofdm,imgtransfer_src)
%include "ofdm_imgtransfer_src.h"

GR_SWIG_BLOCK_MAGIC(ofdm,imgtransfer_testkanal);
%include "ofdm_imgtransfer_testkanal.h"

GR_SWIG_BLOCK_MAGIC(ofdm,interp_cir_set_noncir_to_zero);
%include "ofdm_interp_cir_set_noncir_to_zero.h"

GR_SWIG_BLOCK_MAGIC(ofdm,limit_vff);
%include "ofdm_limit_vff.h"

GR_SWIG_BLOCK_MAGIC(ofdm,lms_fir_ff);
%include "ofdm_lms_fir_ff.h"

GR_SWIG_BLOCK_MAGIC(ofdm,lms_phase_tracking);
%include "ofdm_lms_phase_tracking.h"

GR_SWIG_BLOCK_MAGIC(ofdm,LMS_phase_tracking2);
%include "ofdm_LMS_phase_tracking2.h"

GR_SWIG_BLOCK_MAGIC(ofdm,LMS_phase_tracking3);
%include "ofdm_LMS_phase_tracking3.h"

GR_SWIG_BLOCK_MAGIC(ofdm,LS_estimator_straight_slope);
%include "ofdm_LS_estimator_straight_slope.h"

GR_SWIG_BLOCK_MAGIC(ofdm,mean_squared_error);
%include "ofdm_mean_squared_error.h"

GR_SWIG_BLOCK_MAGIC(ofdm,mm_frequency_estimator);
%include "ofdm_mm_frequency_estimator.h"

GR_SWIG_BLOCK_MAGIC(ofdm,moms_cc);
%include "ofdm_moms_cc.h"

GR_SWIG_BLOCK_MAGIC(ofdm,moms_ff);
%include "ofdm_moms_ff.h"

GR_SWIG_BLOCK_MAGIC(ofdm,multiply_const_vcc);
%include "ofdm_multiply_const_vcc.h"

GR_SWIG_BLOCK_MAGIC(ofdm,multiply_const_ccf);
%include "ofdm_multiply_const_ccf.h"

GR_SWIG_BLOCK_MAGIC(ofdm,noise_nulling);
%include "ofdm_noise_nulling.h"

GR_SWIG_BLOCK_MAGIC(ofdm,normalize_vcc);
%include "ofdm_normalize_vcc.h"

GR_SWIG_BLOCK_MAGIC(ofdm,peak_detector2_fb);
%include "ofdm_peak_detector2_fb.h"

GR_SWIG_BLOCK_MAGIC(ofdm,peak_resync_bb);
%include "ofdm_peak_resync_bb.h"

GR_SWIG_BLOCK_MAGIC(ofdm,pilot_subcarrier_inserter);
%include "ofdm_pilot_subcarrier_inserter.h"

GR_SWIG_BLOCK_MAGIC(ofdm,postprocess_CTF_estimate);
%include "ofdm_postprocess_CTF_estimate.h"

GR_SWIG_BLOCK_MAGIC(ofdm,reassemble_ofdm_frame);
%include "ofdm_reassemble_ofdm_frame.h"

GR_SWIG_BLOCK_MAGIC(ofdm,reference_data_source_ib);
%include "ofdm_reference_data_source_ib.h"

GR_SWIG_BLOCK_MAGIC(ofdm,repetition_decoder_bs);
%include "ofdm_repetition_decoder_bs.h"

GR_SWIG_BLOCK_MAGIC(ofdm,repetition_encoder_sb);
%include "ofdm_repetition_encoder_sb.h"

GR_SWIG_BLOCK_MAGIC(ofdm,scatterplot_sink);
%include "ofdm_scatterplot_sink.h"

GR_SWIG_BLOCK_MAGIC(ofdm,schmidl_cfo_estimator);
%include "ofdm_schmidl_cfo_estimator.h"

GR_SWIG_BLOCK_MAGIC(ofdm,schmidl_tm_rec_stage1);
%include "ofdm_schmidl_tm_rec_stage1.h"

GR_SWIG_BLOCK_MAGIC(ofdm,schmidl_tm_rec_stage2);
%include "ofdm_schmidl_tm_rec_stage2.h"

GR_SWIG_BLOCK_MAGIC(ofdm,sc_snr_estimator);
%include "ofdm_sc_snr_estimator.h"

GR_SWIG_BLOCK_MAGIC(ofdm,sinr_estimator2);
%include "ofdm_sinr_estimator2.h"

GR_SWIG_BLOCK_MAGIC(ofdm,sinr_estimator);
%include "ofdm_sinr_estimator.h"

GR_SWIG_BLOCK_MAGIC(ofdm,sinr_interpolator);
%include "ofdm_sinr_interpolator.h"

GR_SWIG_BLOCK_MAGIC(ofdm,skip);
%include "ofdm_skip.h"

GR_SWIG_BLOCK_MAGIC(ofdm,snr_estimator);
%include "ofdm_snr_estimator.h"

GR_SWIG_BLOCK_MAGIC(ofdm,static_mux_c);
%include "ofdm_static_mux_c.h"

GR_SWIG_BLOCK_MAGIC(ofdm,static_mux_v);
%include "ofdm_static_mux_v.h"

GR_SWIG_BLOCK_MAGIC(ofdm,sqrt_vff);
%include "ofdm_sqrt_vff.h"

GR_SWIG_BLOCK_MAGIC(ofdm,stream_controlled_mux);
%include "ofdm_stream_controlled_mux.h"

GR_SWIG_BLOCK_MAGIC(ofdm,stream_controlled_mux_b);
%include "ofdm_stream_controlled_mux_b.h"

GR_SWIG_BLOCK_MAGIC(ofdm,suppress_erasure_decision);
%include "ofdm_suppress_erasure_decision.h"

GR_SWIG_BLOCK_MAGIC(ofdm,throughput_measure);
%include "ofdm_throughput_measure.h"

GR_SWIG_BLOCK_MAGIC(ofdm,trigger_surveillance);
%include "ofdm_trigger_surveillance.h"

GR_SWIG_BLOCK_MAGIC(ofdm,vector_element);
%include "ofdm_vector_element.h"

GR_SWIG_BLOCK_MAGIC(ofdm,vector_mask);
%include "ofdm_vector_mask.h"

GR_SWIG_BLOCK_MAGIC(ofdm,vector_padding);
%include "ofdm_vector_padding.h"

GR_SWIG_BLOCK_MAGIC(ofdm,vector_sampler);
%include "ofdm_vector_sampler.h"

GR_SWIG_BLOCK_MAGIC(ofdm,vector_sum_vcc);
%include "ofdm_vector_sum_vcc.h"

GR_SWIG_BLOCK_MAGIC(ofdm,vector_sum_vff);
%include "ofdm_vector_sum_vff.h"

GR_SWIG_BLOCK_MAGIC(ofdm,bernoulli_bit_src);
%include "ofdm_bernoulli_bit_src.h"

GR_SWIG_BLOCK_MAGIC(ofdm,complex_white_noise);
%include "ofdm_complex_white_noise.h"

GR_SWIG_BLOCK_MAGIC(ofdm,symbol_random_src);
%include "ofdm_symbol_random_src.h"
