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
    ofdm_autocorrelator.h
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
    util_random.h
    util_bmp.h
    util_endian.h
    util_ipc.h
    gr_block_fwd.h
    DESTINATION include/ofdm
)
