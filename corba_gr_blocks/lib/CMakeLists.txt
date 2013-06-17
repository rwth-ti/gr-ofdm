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
# Setup library
########################################################################
include(GrPlatform) #define LIB_SUFFIX

add_library(gnuradio-ofdm SHARED 
    corba_push_consumer.cc
    corba_push_supplier.cc
    corba_push_supplier_wrapper.cc
    ofdm_corba_assignment_src_sv.cc
    ofdm_corba_bitcount_src_si.cc
    ofdm_corba_bitmap_src.cc
    ofdm_corba_id_filter.cc
    ofdm_corba_id_src_s.cc
    ofdm_corba_map_src_sv.cc
    ofdm_corba_multiplex_src_ss.cc
    ofdm_corba_power_allocator.cc
    ofdm_corba_power_src_sv.cc
    ofdm_corba_rxinfo_sink.cc
    ofdm_corba_rxinfo_sink_imgxfer.cc
    ofdm_corba_rxbaseband_sink.cc
    orb.cc
)
target_link_libraries(gnuradio-ofdm 
    ${Boost_LIBRARIES}
    ${GRUEL_LIBRARIES}
    ${GNURADIO_CORE_LIBRARIES}
    ${ITPP_LIBRARIES}
    ${TAO_UTILS_LIBS}
    ${TAO_COSEVENT_SKEL_LIBS}
    ${TAO_COSNAMING_LIBS})
set_target_properties(gnuradio-ofdm PROPERTIES DEFINE_SYMBOL "gnuradio_ofdm_EXPORTS")

########################################################################
# Install built library files
########################################################################
install(TARGETS gnuradio-ofdm
    LIBRARY DESTINATION lib${LIB_SUFFIX} # .so/.dylib file
    ARCHIVE DESTINATION lib${LIB_SUFFIX} # .lib file
    RUNTIME DESTINATION bin              # .dll file
)

