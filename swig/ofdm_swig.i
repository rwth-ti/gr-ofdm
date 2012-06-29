/* -*- c++ -*- */

#define OFDM_API

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
