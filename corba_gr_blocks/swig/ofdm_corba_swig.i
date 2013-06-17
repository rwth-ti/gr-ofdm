/* -*- c++ -*- */

#define OFDM_API
#define __attribute__(x)

%include "gnuradio.i"			// the common stuff

//load generated python docstrings
%include "ofdm_swig_doc.i"

%{
#include "ofdm_api.h"
#include "ofdm_corba_assignment_src_sv.h"
#include "ofdm_corba_bitcount_src_si.h"
#include "ofdm_corba_bitmap_src.h"
#include "ofdm_corba_id_filter.h"
#include "ofdm_corba_id_src_s.h"
#include "ofdm_corba_map_src_sc.h"
#include "ofdm_corba_multiplex_src_ss.h"
#include "ofdm_corba_power_allocator.h"
#include "ofdm_corba_power_src.h"
#include "ofdm_corba_rx_baseband_sink.h"
#include "ofdm_corba_rxinfo_sink_imgxfer.h"
#include "ofdm_corba_rxinfo_sink.h"
%}

GR_SWIG_BLOCK_MAGIC(ofdm,corba_assignment_src_sv);
%include "ofdm_corba_assignment_src_sv.h"

GR_SWIG_BLOCK_MAGIC(ofdm,corba_bitcount_src_si);
%include "ofdm_corba_bitcount_src_si.h"

GR_SWIG_BLOCK_MAGIC(ofdm,corba_bitmap_src);
%include "ofdm_corba_bitmap_src.h"

GR_SWIG_BLOCK_MAGIC(ofdm,corba_id_filter);
#include "ofdm_corba_id_filter.h"

GR_SWIG_BLOCK_MAGIC(ofdm,corba_id_src_s);
%include "ofdm_corba_id_src_s.h"

GR_SWIG_BLOCK_MAGIC(ofdm,corba_map_src_sc);
%include "ofdm_corba_map_src_sc.h"

GR_SWIG_BLOCK_MAGIC(ofdm,corba_multiplex_src_ss);
%include "ofdm_corba_multiplex_src_ss.h"

GR_SWIG_BLOCK_MAGIC(ofdm,corba_power_allocator);
%include "ofdm_corba_power_allocator.h"

GR_SWIG_BLOCK_MAGIC(ofdm,corba_power_src);
%include "ofdm_corba_power_src.h"

GR_SWIG_BLOCK_MAGIC(ofdm,corba_rx_baseband_sink);
%include "ofdm_corba_rx_baseband_sink.h"

GR_SWIG_BLOCK_MAGIC(ofdm,corba_rxinfo_sink_imgxfer);
%include "ofdm_corba_rxinfo_sink_imgxfer.h"

GR_SWIG_BLOCK_MAGIC(ofdm,corba_rxinfo_sink);
%include "ofdm_corba_rxinfo_sink.h"
