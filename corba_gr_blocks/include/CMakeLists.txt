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
    ofdm_corba_assignment_src_sv.h
    ofdm_corba_bitcount_src_si.h
    ofdm_corba_bitmap_src.h
    ofdm_corba_id_filter.h
    ofdm_corba_id_src_s.h
    ofdm_corba_map_src_sv.h
    ofdm_corba_multiplex_src_ss.h
    ofdm_corba_power_allocator.h
    ofdm_corba_power_src_sv.h
    ofdm_corba_rxinfo_sink.h
    ofdm_corba_rxinfo_sink_imgxfer.h
    ofdm_corba_rxbaseband_sink.h
    corba_push_consumer.h 
    corba_push_supplier.h 
    corba_push_supplier_wrapper.h
    DESTINATION corba_gr_blocks/include/ofdm
)
