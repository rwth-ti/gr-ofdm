/* -*- c++ -*- */

#define OFDM_API
#define __attribute__(x)

%include "gnuradio.i"			// the common stuff

//load generated python docstrings
%include "ofdm_swig_doc.i"


%{
#include "ofdm_cube_ff.h"
#include "ofdm_power4_ff.h"
#include "ofdm_new_ff.h"
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
//#include "ofdm_CTF_MSE_enhancer.h"
#include "ofdm_cyclic_prefixer.h"
#include "ofdm_dominiks_sync_01.h"
#include "ofdm_dynamic_trigger_ib.h"
#include "ofdm_extract_block_from_frame.h"
//#include "ofdm_find_cir_shift.h"
#include "ofdm_frame_mux.h"
#include "ofdm_frequency_shift_vcc.h"
#include "ofdm_generic_mapper_bcv.h"
#include "ofdm_gate_ff.h"
#include "ofdm_get_zeros.h"
#include "ofdm_generic_demapper_vcb.h"
#include "ofdm_imgtransfer_src.h"
#include "ofdm_imgtransfer_testkanal.h"
%}

GR_SWIG_BLOCK_MAGIC(ofdm,cube_ff);
%include "ofdm_cube_ff.h"

GR_SWIG_BLOCK_MAGIC(ofdm,power4_ff);
%include "ofdm_power4_ff.h"

GR_SWIG_BLOCK_MAGIC(ofdm,new_ff);
%include "ofdm_new_ff.h"

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

//GR_SWIG_BLOCK_MAGIC(ofdm,CTF_MSE_enhancer);
//%include "ofdm_CTF_MSE_enhancer.h"

GR_SWIG_BLOCK_MAGIC(ofdm,cyclic_prefixer);
%include "ofdm_cyclic_prefixer.h"

GR_SWIG_BLOCK_MAGIC(ofdm,dominiks_sync_01);
%include "ofdm_dominiks_sync_01.h"

GR_SWIG_BLOCK_MAGIC(ofdm,dynamic_trigger_ib);
%include "ofdm_dynamic_trigger_ib.h"

GR_SWIG_BLOCK_MAGIC(ofdm,extract_block_from_frame);
%include "ofdm_extract_block_from_frame.h"

//GR_SWIG_BLOCK_MAGIC(ofdm,find_cir_shift);
//%include "ofdm_find_cir_shift.h"

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
