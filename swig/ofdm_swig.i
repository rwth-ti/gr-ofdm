/* -*- c++ -*- */

#define OFDM_API

%include "gnuradio.i"			// the common stuff

//load generated python docstrings
%include "ofdm_swig_doc.i"

%{
#include "ofdm/accumulator_cc.h"
#include "ofdm/autocorrelator_stage1.h"
#include "ofdm/autocorrelator_stage2.h"
#include "ofdm/accumulator_ff.h"
#include "ofdm/autocorrelator0.h"
#include "ofdm/ber_measurement.h"
#include "ofdm/bernoulli_bit_src.h"
#include "ofdm/bit_position_dependent_ber.h"
#include "ofdm/ofdm_metric_type.h"
#include "ofdm/calc_metric.h"
#include "ofdm/channel_equalizer_mimo_2.h"
#include "ofdm/channel_equalizer_mimo_3.h"
#include "ofdm/channel_equalizer_mimo.h"
#include "ofdm/channel_equalizer.h"
#include "ofdm/channel_estimator_01.h"
#include "ofdm/channel_estimator_02.h"
#include "ofdm/coded_bpsk_soft_decoder.h"
//#include "ofdm/compat_read_ber_from_imgxfer.h"
//#include "ofdm/imgtransfer_sink.h"
#include "ofdm/imgtransfer_src.h"
#include "ofdm/imgtransfer_testkanal.h"
#include "ofdm/complex_to_arg.h"
#include "ofdm/complex_white_noise.h"
#include "ofdm/constellation_sample_filter.h"
#include "ofdm/CTF_MSE_enhancer.h"
#include "ofdm/cyclic_prefixer.h"
#include "ofdm/depuncture_bb.h"
#include "ofdm/depuncture_ff.h"
#include "ofdm/time_sync.h"
#include "ofdm/time_sync2.h"
#include "ofdm/dynamic_trigger_ib.h"
#include "ofdm/extract_block_from_frame.h"
#include "ofdm/find_cir_shift.h"
#include "ofdm/frame_mux.h"
#include "ofdm/frequency_shift_vcc.h"
#include "ofdm/gate_ff.h"
#include "ofdm/generic_mapper_bcv.h"
#include "ofdm/generic_demapper_vcb.h"
#include "ofdm/generic_mapper_mimo_bcv.h"
#include "ofdm/generic_softdemapper_vcf.h"
#include "ofdm/int_skip.h"
#include "ofdm/interp_cir_set_noncir_to_zero.h"
#include "ofdm/limit_vff.h"
#include "ofdm/lms_fir_ff.h"
#include "ofdm/lms_phase_tracking.h"
#include "ofdm/lms_phase_tracking_02.h"
#include "ofdm/lms_phase_tracking_03.h"
#include "ofdm/ls_estimator_straight_slope.h"
#include "ofdm/mean_squared_error.h"
#include "ofdm/mm_frequency_estimator.h"
#include "ofdm/moms_cc.h"
#include "ofdm/moms_ff.h"
#include "ofdm/multiply_frame_fc.h"
#include "ofdm/divide_frame_fc.h"
#include "ofdm/multiply_const_ccf.h"
#include "ofdm/multiply_const_ii.h"
#include "ofdm/multiply_const_vcc.h"
#include "ofdm/noise_nulling.h"
#include "ofdm/normalize_vcc.h"
#include "ofdm/peak_detector_02_fb.h"
#include "ofdm/peak_resync_bb.h"
#include "ofdm/pilot_subcarrier_inserter.h"
#include "ofdm/postprocess_CTF_estimate.h"
#include "ofdm/puncture_bb.h"
#include "ofdm/reassemble_ofdm_frame.h"
#include "ofdm/reference_data_source_ib.h"
#include "ofdm/reference_data_source_mimo_ib.h"
#include "ofdm/repetition_decoder_bs.h"
#include "ofdm/repetition_encoder_sb.h"
#include "ofdm/subc_snr_estimator.h"
#include "ofdm/scatterplot_sink.h"
#include "ofdm/schmidl_cfo_estimator.h"
#include "ofdm/schmidl_tm_rec_stage1.h"
#include "ofdm/schmidl_tm_rec_stage2.h"
#include "ofdm/sinr_estimator.h"
#include "ofdm/sinr_estimator_02.h"
#include "ofdm/sinr_interpolator.h"
#include "ofdm/skip.h"
#include "ofdm/snr_estimator.h"
#include "ofdm/sqrt_vff.h"
#include "ofdm/static_mux_c.h"
#include "ofdm/static_mux_v.h"
#include "ofdm/stc_decoder_rx0.h"
#include "ofdm/stc_decoder_rx1.h"
#include "ofdm/stc_encoder.h"
#include "ofdm/stream_controlled_mux_b.h"
#include "ofdm/stream_controlled_mux.h"
#include "ofdm/suppress_erasure_decision.h"
#include "ofdm/symbol_random_src.h"
#include "ofdm/throughput_measure.h"
#include "ofdm/trigger_surveillance.h"
#include "ofdm/vector_padding.h"
#include "ofdm/vector_mask.h"
#include "ofdm/vector_element.h"
#include "ofdm/vector_sampler.h"
#include "ofdm/vector_sum_vcc.h"
#include "ofdm/vector_sum_vff.h"
#include "ofdm/viterbi_combined_fb.h"
#include "ofdm/fsm.h"
//#include "ofdm/corba_assignment_src_sv.h"
//#include "ofdm/corba_bitcount_src_si.h"
//#include "ofdm/corba_bitmap_src.h"
//#include "ofdm/corba_id_filter.h"
//#include "ofdm/corba_id_src.h"
//#include "ofdm/corba_map_src_sv.h"
//#include "ofdm/corba_multiplex_src_ss.h"
//#include "ofdm/corba_power_allocator.h"
//#include "ofdm/corba_power_src_sv.h"
//#include "ofdm/corba_rxbaseband_sink.h"
//#include "ofdm/corba_rxinfo_sink_imgxfer.h"
//#include "ofdm/corba_rxinfo_sink.h"
#include "ofdm/itpp_tdl_channel.h"
#include "ofdm/encoder_bb.h"
#include "ofdm/reference_data_source_02_ib.h"
#include "ofdm/allocation_src.h"
#include "ofdm/allocation_buffer.h"
#include "ofdm/tx_mux_ctrl.h"
#include "ofdm/midamble_insert.h"
#include "ofdm/fbmc_oqam_preprocessing_vcvc.h"
#include "ofdm/fbmc_oqam_postprocessing_vcvc.h"
#include "ofdm/fbmc_beta_multiplier_vcvc.h"
#include "ofdm/fbmc_separate_vcvc.h"
#include "ofdm/fbmc_snr_estimator.h"
#include "ofdm/fbmc_polyphase_network_vcvc.h"
#include "ofdm/fbmc_postprocess_CTF_estimate.h"
#include "ofdm/fbmc_vector_copy_vcvc.h"
#include "ofdm/fbmc_junction_vcvc.h"
#include "ofdm/fbmc_subchannel_processing_vcvc.h"
#include "ofdm/fbmc_weighted_spreading_vcvc.h"
#include "ofdm/fbmc_weighted_despreading_vcvc.h"
#include "ofdm/fbmc_asymmetrical_vector_padding_vcvc.h"
#include "ofdm/fbmc_asymmetrical_vector_mask_vcvc.h"
#include "ofdm/scfdma_subcarrier_mapper_vcvc.h"
#include "ofdm/scfdma_subcarrier_demapper_vcvc.h"
#include "ofdm/add_vcc.h"
#include "ofdm/fbmc_subchannel_processing_mu_vcvc.h"
//#include "ofdm/corba_bitcount_src_02_si.h"
%}


%include "ofdm/accumulator_cc.h"
GR_SWIG_BLOCK_MAGIC2(ofdm, accumulator_cc);
%include "ofdm/autocorrelator_stage1.h"
GR_SWIG_BLOCK_MAGIC2(ofdm, autocorrelator_stage1);
%include "ofdm/autocorrelator_stage2.h"
GR_SWIG_BLOCK_MAGIC2(ofdm, autocorrelator_stage2);
%include "ofdm/accumulator_ff.h"
GR_SWIG_BLOCK_MAGIC2(ofdm, accumulator_ff);
%include "ofdm/autocorrelator0.h"
GR_SWIG_BLOCK_MAGIC2(ofdm, autocorrelator0);
%include "ofdm/ber_measurement.h"
GR_SWIG_BLOCK_MAGIC2(ofdm, ber_measurement);
%include "ofdm/bernoulli_bit_src.h"
GR_SWIG_BLOCK_MAGIC2(ofdm, bernoulli_bit_src);
%include "ofdm/bit_position_dependent_ber.h"
GR_SWIG_BLOCK_MAGIC2(ofdm, bit_position_dependent_ber);
%include "ofdm/calc_metric.h"
%include "ofdm/ofdm_metric_type.h"
%include "ofdm/channel_equalizer_mimo_2.h"
GR_SWIG_BLOCK_MAGIC2(ofdm, channel_equalizer_mimo_2);
%include "ofdm/channel_equalizer_mimo_3.h"
GR_SWIG_BLOCK_MAGIC2(ofdm, channel_equalizer_mimo_3);
%include "ofdm/channel_equalizer_mimo.h"
GR_SWIG_BLOCK_MAGIC2(ofdm, channel_equalizer_mimo);
%include "ofdm/channel_equalizer.h"
GR_SWIG_BLOCK_MAGIC2(ofdm, channel_equalizer);
%include "ofdm/channel_estimator_01.h"
GR_SWIG_BLOCK_MAGIC2(ofdm, channel_estimator_01);

%include "ofdm/channel_estimator_02.h"
GR_SWIG_BLOCK_MAGIC2(ofdm, channel_estimator_02);
%include "ofdm/coded_bpsk_soft_decoder.h"
GR_SWIG_BLOCK_MAGIC2(ofdm, coded_bpsk_soft_decoder);

//%include "ofdm/compat_read_ber_from_imgxfer.h"
//GR_SWIG_BLOCK_MAGIC2(ofdm, compat_read_ber_from_imgxfer);
//%include "ofdm/imgtransfer_sink.h"
//GR_SWIG_BLOCK_MAGIC2(ofdm, imgtransfer_sink);


%include "ofdm/imgtransfer_src.h"
GR_SWIG_BLOCK_MAGIC2(ofdm, imgtransfer_src);
%include "ofdm/imgtransfer_testkanal.h"
GR_SWIG_BLOCK_MAGIC2(ofdm, imgtransfer_testkanal);
%include "ofdm/complex_to_arg.h"
GR_SWIG_BLOCK_MAGIC2(ofdm, complex_to_arg);
%include "ofdm/complex_white_noise.h"
GR_SWIG_BLOCK_MAGIC2(ofdm, complex_white_noise);
%include "ofdm/constellation_sample_filter.h"
GR_SWIG_BLOCK_MAGIC2(ofdm, constellation_sample_filter);
%include "ofdm/CTF_MSE_enhancer.h"
GR_SWIG_BLOCK_MAGIC2(ofdm, CTF_MSE_enhancer);
%include "ofdm/cyclic_prefixer.h"
GR_SWIG_BLOCK_MAGIC2(ofdm, cyclic_prefixer);
%include "ofdm/depuncture_bb.h"
GR_SWIG_BLOCK_MAGIC2(ofdm, depuncture_bb);
%include "ofdm/depuncture_ff.h"
GR_SWIG_BLOCK_MAGIC2(ofdm, depuncture_ff);
%include "ofdm/time_sync.h"
GR_SWIG_BLOCK_MAGIC2(ofdm, time_sync);
%include "ofdm/time_sync2.h"
GR_SWIG_BLOCK_MAGIC2(ofdm, time_sync2);
%include "ofdm/dynamic_trigger_ib.h"
GR_SWIG_BLOCK_MAGIC2(ofdm, dynamic_trigger_ib);
%include "ofdm/extract_block_from_frame.h"
GR_SWIG_BLOCK_MAGIC2(ofdm, extract_block_from_frame);
%include "ofdm/find_cir_shift.h"
GR_SWIG_BLOCK_MAGIC2(ofdm, find_cir_shift);
%include "ofdm/frame_mux.h"
GR_SWIG_BLOCK_MAGIC2(ofdm, frame_mux);
%include "ofdm/frequency_shift_vcc.h"
GR_SWIG_BLOCK_MAGIC2(ofdm, frequency_shift_vcc);
%include "ofdm/gate_ff.h"
GR_SWIG_BLOCK_MAGIC2(ofdm, gate_ff);
%include "ofdm/generic_mapper_bcv.h"
GR_SWIG_BLOCK_MAGIC2(ofdm, generic_mapper_bcv);
%include "ofdm/generic_demapper_vcb.h"
GR_SWIG_BLOCK_MAGIC2(ofdm, generic_demapper_vcb);
%include "ofdm/generic_mapper_mimo_bcv.h"
GR_SWIG_BLOCK_MAGIC2(ofdm, generic_mapper_mimo_bcv);

%include "ofdm/generic_softdemapper_vcf.h"
GR_SWIG_BLOCK_MAGIC2(ofdm, generic_softdemapper_vcf);
%include "ofdm/int_skip.h"
GR_SWIG_BLOCK_MAGIC2(ofdm, int_skip);
%include "ofdm/interp_cir_set_noncir_to_zero.h"
GR_SWIG_BLOCK_MAGIC2(ofdm, interp_cir_set_noncir_to_zero);
%include "ofdm/limit_vff.h"
GR_SWIG_BLOCK_MAGIC2(ofdm, limit_vff);
%include "ofdm/lms_fir_ff.h"
GR_SWIG_BLOCK_MAGIC2(ofdm, lms_fir_ff);
%include "ofdm/lms_phase_tracking.h"
GR_SWIG_BLOCK_MAGIC2(ofdm, lms_phase_tracking);
%include "ofdm/lms_phase_tracking_02.h"
GR_SWIG_BLOCK_MAGIC2(ofdm, lms_phase_tracking_02);

%include "ofdm/lms_phase_tracking_03.h"
GR_SWIG_BLOCK_MAGIC2(ofdm, lms_phase_tracking_03);
%include "ofdm/ls_estimator_straight_slope.h"
GR_SWIG_BLOCK_MAGIC2(ofdm, ls_estimator_straight_slope);
%include "ofdm/mean_squared_error.h"
GR_SWIG_BLOCK_MAGIC2(ofdm, mean_squared_error);
%include "ofdm/mm_frequency_estimator.h"
GR_SWIG_BLOCK_MAGIC2(ofdm, mm_frequency_estimator);
%include "ofdm/moms_cc.h"
GR_SWIG_BLOCK_MAGIC2(ofdm, moms_cc);
%include "ofdm/moms_ff.h"
GR_SWIG_BLOCK_MAGIC2(ofdm, moms_ff);
%include "ofdm/multiply_frame_fc.h"
GR_SWIG_BLOCK_MAGIC2(ofdm, multiply_frame_fc);
%include "ofdm/divide_frame_fc.h"
GR_SWIG_BLOCK_MAGIC2(ofdm, divide_frame_fc);
%include "ofdm/multiply_const_ccf.h"
GR_SWIG_BLOCK_MAGIC2(ofdm, multiply_const_ccf);
%include "ofdm/multiply_const_ii.h"
GR_SWIG_BLOCK_MAGIC2(ofdm, multiply_const_ii);
%include "ofdm/multiply_const_vcc.h"
GR_SWIG_BLOCK_MAGIC2(ofdm, multiply_const_vcc);
%include "ofdm/noise_nulling.h"
GR_SWIG_BLOCK_MAGIC2(ofdm, noise_nulling);
%include "ofdm/normalize_vcc.h"
GR_SWIG_BLOCK_MAGIC2(ofdm, normalize_vcc);
%include "ofdm/peak_detector_02_fb.h"
GR_SWIG_BLOCK_MAGIC2(ofdm, peak_detector_02_fb);
%include "ofdm/peak_resync_bb.h"
GR_SWIG_BLOCK_MAGIC2(ofdm, peak_resync_bb);
%include "ofdm/pilot_subcarrier_inserter.h"
GR_SWIG_BLOCK_MAGIC2(ofdm, pilot_subcarrier_inserter);
%include "ofdm/postprocess_CTF_estimate.h"
GR_SWIG_BLOCK_MAGIC2(ofdm, postprocess_CTF_estimate);
%include "ofdm/puncture_bb.h"
GR_SWIG_BLOCK_MAGIC2(ofdm, puncture_bb);
%include "ofdm/reassemble_ofdm_frame.h"
GR_SWIG_BLOCK_MAGIC2(ofdm, reassemble_ofdm_frame);
%include "ofdm/reference_data_source_ib.h"
GR_SWIG_BLOCK_MAGIC2(ofdm, reference_data_source_ib);
%include "ofdm/reference_data_source_mimo_ib.h"
GR_SWIG_BLOCK_MAGIC2(ofdm, reference_data_source_mimo_ib);

%include "ofdm/repetition_decoder_bs.h"
GR_SWIG_BLOCK_MAGIC2(ofdm, repetition_decoder_bs);
%include "ofdm/repetition_encoder_sb.h"
GR_SWIG_BLOCK_MAGIC2(ofdm, repetition_encoder_sb);
%include "ofdm/subc_snr_estimator.h"
GR_SWIG_BLOCK_MAGIC2(ofdm, subc_snr_estimator);
%include "ofdm/scatterplot_sink.h"
GR_SWIG_BLOCK_MAGIC2(ofdm, scatterplot_sink);
%include "ofdm/schmidl_cfo_estimator.h"
GR_SWIG_BLOCK_MAGIC2(ofdm, schmidl_cfo_estimator);
%include "ofdm/schmidl_tm_rec_stage1.h"
GR_SWIG_BLOCK_MAGIC2(ofdm, schmidl_tm_rec_stage1);
%include "ofdm/schmidl_tm_rec_stage2.h"
GR_SWIG_BLOCK_MAGIC2(ofdm, schmidl_tm_rec_stage2);
%include "ofdm/sinr_estimator.h"
GR_SWIG_BLOCK_MAGIC2(ofdm, sinr_estimator);
%include "ofdm/sinr_estimator_02.h"
GR_SWIG_BLOCK_MAGIC2(ofdm, sinr_estimator_02);
%include "ofdm/sinr_interpolator.h"
GR_SWIG_BLOCK_MAGIC2(ofdm, sinr_interpolator);
%include "ofdm/skip.h"
GR_SWIG_BLOCK_MAGIC2(ofdm, skip);
%include "ofdm/snr_estimator.h"
GR_SWIG_BLOCK_MAGIC2(ofdm, snr_estimator);
%include "ofdm/sqrt_vff.h"
GR_SWIG_BLOCK_MAGIC2(ofdm, sqrt_vff);
%include "ofdm/static_mux_c.h"
GR_SWIG_BLOCK_MAGIC2(ofdm, static_mux_c);
%include "ofdm/static_mux_v.h"
GR_SWIG_BLOCK_MAGIC2(ofdm, static_mux_v);
%include "ofdm/stc_decoder_rx0.h"
GR_SWIG_BLOCK_MAGIC2(ofdm, stc_decoder_rx0);
%include "ofdm/stc_decoder_rx1.h"
GR_SWIG_BLOCK_MAGIC2(ofdm, stc_decoder_rx1);
%include "ofdm/stc_encoder.h"
GR_SWIG_BLOCK_MAGIC2(ofdm, stc_encoder);
%include "ofdm/stream_controlled_mux_b.h"
GR_SWIG_BLOCK_MAGIC2(ofdm, stream_controlled_mux_b);
%include "ofdm/stream_controlled_mux.h"
GR_SWIG_BLOCK_MAGIC2(ofdm, stream_controlled_mux);
%include "ofdm/suppress_erasure_decision.h"
GR_SWIG_BLOCK_MAGIC2(ofdm, suppress_erasure_decision);
%include "ofdm/symbol_random_src.h"
GR_SWIG_BLOCK_MAGIC2(ofdm, symbol_random_src);
%include "ofdm/throughput_measure.h"
GR_SWIG_BLOCK_MAGIC2(ofdm, throughput_measure);
%include "ofdm/trigger_surveillance.h"
GR_SWIG_BLOCK_MAGIC2(ofdm, trigger_surveillance);
%include "ofdm/vector_padding.h"
GR_SWIG_BLOCK_MAGIC2(ofdm, vector_padding);
%include "ofdm/vector_mask.h"
GR_SWIG_BLOCK_MAGIC2(ofdm, vector_mask);
%include "ofdm/vector_element.h"
GR_SWIG_BLOCK_MAGIC2(ofdm, vector_element);
%include "ofdm/vector_sampler.h"
GR_SWIG_BLOCK_MAGIC2(ofdm, vector_sampler);
%include "ofdm/vector_sum_vcc.h"
GR_SWIG_BLOCK_MAGIC2(ofdm, vector_sum_vcc);
%include "ofdm/vector_sum_vff.h"
GR_SWIG_BLOCK_MAGIC2(ofdm, vector_sum_vff);
%include "ofdm/viterbi_combined_fb.h"
GR_SWIG_BLOCK_MAGIC2(ofdm, viterbi_combined_fb);
//%include "ofdm/fsm.h"
//GR_SWIG_BLOCK_MAGIC2(ofdm, fsm);
//%include "ofdm/corba_assignment_src_sv.h"
//GR_SWIG_BLOCK_MAGIC2(ofdm, corba_assignment_src_sv);
//%include "ofdm/corba_bitcount_src_si.h"
//GR_SWIG_BLOCK_MAGIC2(ofdm, corba_bitcount_src_si);
//%include "ofdm/corba_bitmap_src.h"
//GR_SWIG_BLOCK_MAGIC2(ofdm, corba_bitmap_src);
//%include "ofdm/corba_id_filter.h"
//GR_SWIG_BLOCK_MAGIC2(ofdm, corba_id_filter);
//%include "ofdm/corba_id_src.h"
//GR_SWIG_BLOCK_MAGIC2(ofdm, corba_id_src);
//%include "ofdm/corba_map_src_sv.h"
//GR_SWIG_BLOCK_MAGIC2(ofdm, corba_map_src_sv);
//%include "ofdm/corba_multiplex_src_ss.h"
//GR_SWIG_BLOCK_MAGIC2(ofdm, corba_multiplex_src_ss);
//%include "ofdm/corba_power_allocator.h"
//GR_SWIG_BLOCK_MAGIC2(ofdm, corba_power_allocator);
//%include "ofdm/corba_power_src_sv.h"
//GR_SWIG_BLOCK_MAGIC2(ofdm, corba_power_src_sv);
//%include "ofdm/corba_rxbaseband_sink.h"
//GR_SWIG_BLOCK_MAGIC2(ofdm, corba_rxbaseband_sink);
//%include "ofdm/corba_rxinfo_sink_imgxfer.h"
//GR_SWIG_BLOCK_MAGIC2(ofdm, corba_rxinfo_sink_imgxfer);
//%include "ofdm/corba_rxinfo_sink.h"
//GR_SWIG_BLOCK_MAGIC2(ofdm, corba_rxinfo_sink);
%include "ofdm/itpp_tdl_channel.h"
GR_SWIG_BLOCK_MAGIC2(ofdm, itpp_tdl_channel);

class fsm {
private:
  int d_I;
  int d_S;
  int d_O;
  std::vector<int> d_NS;
  std::vector<int> d_OS;
  std::vector< std::vector<int> > d_PS;
  std::vector< std::vector<int> > d_PI;
  std::vector<int> d_TMi;
  std::vector<int> d_TMl;
  void generate_PS_PI ();
  void generate_TM ();
public:
  fsm();
  fsm(const fsm &FSM);
  fsm(int I, int S, int O, const std::vector<int> &NS, const std::vector<int> &OS);
  fsm(const char *name);
  fsm(int k, int n, const std::vector<int> &G);
  fsm(int mod_size, int ch_length);
  fsm(int P, int M, int L);
  fsm(const fsm &FSM1, const fsm &FSM2);
  fsm(const fsm &FSM, int n);
  int I () const { return d_I; }
  int S () const { return d_S; }
  int O () const { return d_O; }
  const std::vector<int> & NS () const { return d_NS; }
  const std::vector<int> & OS () const { return d_OS; }
  // disable these accessors until we find out how to swig them
  //const std::vector< std::vector<int> > & PS () const { return d_PS; }
  //const std::vector< std::vector<int> > & PI () const { return d_PI; }
  const std::vector<int> & TMi () const { return d_TMi; }
  const std::vector<int> & TMl () const { return d_TMl; }
  void fsm::write_trellis_svg(std::string filename ,int number_stages);
  void fsm::write_fsm_txt(std::string filename);
};
%include "ofdm/encoder_bb.h"
GR_SWIG_BLOCK_MAGIC2(ofdm, encoder_bb);
%include "ofdm/reference_data_source_02_ib.h"
GR_SWIG_BLOCK_MAGIC2(ofdm, reference_data_source_02_ib);
//%include "ofdm/corba_bitcount_src_02_si.h"
//GR_SWIG_BLOCK_MAGIC2(ofdm, corba_bitcount_src_02_si);
%include "ofdm/allocation_src.h"
GR_SWIG_BLOCK_MAGIC2(ofdm, allocation_src);
%include "ofdm/allocation_buffer.h"
GR_SWIG_BLOCK_MAGIC2(ofdm, allocation_buffer);
%include "ofdm/tx_mux_ctrl.h"
GR_SWIG_BLOCK_MAGIC2(ofdm, tx_mux_ctrl);
%include "ofdm/midamble_insert.h"
GR_SWIG_BLOCK_MAGIC2(ofdm, midamble_insert);
%include "ofdm/fbmc_oqam_preprocessing_vcvc.h"
GR_SWIG_BLOCK_MAGIC2(ofdm, fbmc_oqam_preprocessing_vcvc);
%include "ofdm/fbmc_oqam_postprocessing_vcvc.h"
GR_SWIG_BLOCK_MAGIC2(ofdm, fbmc_oqam_postprocessing_vcvc);
%include "ofdm/fbmc_beta_multiplier_vcvc.h"
GR_SWIG_BLOCK_MAGIC2(ofdm, fbmc_beta_multiplier_vcvc);
%include "ofdm/fbmc_separate_vcvc.h"
GR_SWIG_BLOCK_MAGIC2(ofdm, fbmc_separate_vcvc);
%include "ofdm/fbmc_polyphase_network_vcvc.h"
GR_SWIG_BLOCK_MAGIC2(ofdm, fbmc_polyphase_network_vcvc);
%include "ofdm/fbmc_postprocess_CTF_estimate.h"
GR_SWIG_BLOCK_MAGIC2(ofdm, fbmc_postprocess_CTF_estimate);
%include "ofdm/fbmc_vector_copy_vcvc.h"
GR_SWIG_BLOCK_MAGIC2(ofdm, fbmc_vector_copy_vcvc);
%include "ofdm/fbmc_junction_vcvc.h"
GR_SWIG_BLOCK_MAGIC2(ofdm, fbmc_junction_vcvc);
%include "ofdm/fbmc_subchannel_processing_vcvc.h"
GR_SWIG_BLOCK_MAGIC2(ofdm, fbmc_subchannel_processing_vcvc);
%include "ofdm/fbmc_weighted_spreading_vcvc.h"
GR_SWIG_BLOCK_MAGIC2(ofdm, fbmc_weighted_spreading_vcvc);
%include "ofdm/fbmc_weighted_despreading_vcvc.h"
GR_SWIG_BLOCK_MAGIC2(ofdm, fbmc_weighted_despreading_vcvc);
%include "ofdm/fbmc_snr_estimator.h"
GR_SWIG_BLOCK_MAGIC2(ofdm, fbmc_snr_estimator);
%include "ofdm/fbmc_asymmetrical_vector_padding_vcvc.h"
GR_SWIG_BLOCK_MAGIC2(ofdm, fbmc_asymmetrical_vector_padding_vcvc);
%include "ofdm/fbmc_asymmetrical_vector_mask_vcvc.h"
GR_SWIG_BLOCK_MAGIC2(ofdm, fbmc_asymmetrical_vector_mask_vcvc);
%include "ofdm/scfdma_subcarrier_mapper_vcvc.h"
GR_SWIG_BLOCK_MAGIC2(ofdm, scfdma_subcarrier_mapper_vcvc);
%include "ofdm/scfdma_subcarrier_demapper_vcvc.h"
GR_SWIG_BLOCK_MAGIC2(ofdm, scfdma_subcarrier_demapper_vcvc);
%include "ofdm/add_vcc.h"
GR_SWIG_BLOCK_MAGIC2(ofdm, add_vcc);
%include "ofdm/fbmc_subchannel_processing_mu_vcvc.h"
GR_SWIG_BLOCK_MAGIC2(ofdm, fbmc_subchannel_processing_mu_vcvc);

