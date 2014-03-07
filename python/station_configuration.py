#!/usr/bin/env python
# 
# Copyright 2014 Institute for Theoretical Information Technology,
#                RWTH Aachen University
#                www.ti.rwth-aachen.de
# 
# This is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 3, or (at your option)
# any later version.
# 
# This software is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
# 
# You should have received a copy of the GNU General Public License
# along with this software; see the file COPYING.  If not, write to
# the Free Software Foundation, Inc., 51 Franklin Street,
# Boston, MA 02110-1301, USA.
#

# frame_length
# frame_data_blocks
# frame_id_blocks
# frame_data_part
# training_data
# data_subcarriers
# subcarriers
# fft_length
# cp_length
# _verbose
# block_length
# virtual_subcarriers
# frame_id_blocks
# ber_window
# rx_station_id
# tx_station_id
# used_id_bits
# enc_id_bits
# rms_amplitude

class station_configuration:
  __shared_state = {}
  def __init__(self):
    pass

  def __getattr__(self, item):
    try:
        return self.__shared_state.__getitem__(item)
    except KeyError:
        raise AttributeError(item)

  def __setattr__(self, item, value):
    """Maps attributes to values.
    Only if we are initialised
    """
    self.__shared_state.__setitem__(item, value)
