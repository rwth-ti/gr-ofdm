#!/usr/bin/env python

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