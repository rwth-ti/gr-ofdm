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

from numpy import concatenate
import numpy

from resource_manager_base import resource_manager_base,start_resource_manager

class resource_manager (resource_manager_base):
  def __init__(self,orb):
    resource_manager_base.__init__(self,orb)

    # set initial parameters
    self.required_ber = 1e-4
    self.constraint = 4000.0   # rate or power, RMS!
    self.setup_time = 3*1000   # ms
    self.data_rate= 365079     # implicitly exposed to GUI
    self.tx_amplitude = 5000   # RMS!

    # self.subcarriers

  def work(self):
    self.query_sounder()
    self.get_ber()

    snr_vec = self.get_snr()
    snr_mean = 10**(snr_vec[len(snr_vec)-1]/10)

    ctf = self.get_ctf()

    cur_tx_power = self.tx_amplitude**2     # average power
    cur_tx_constraint = self.constraint**2  # dito

    # Input:
    #  self.required_ber
    #  self.constraint
    #  self.current_ber
    #  self.ac_vector (if sounder connected)

    if self.is_reset_mode():
      pass
    elif self.is_margin_adaptive_policy():
      pass
    elif self.is_rate_adaptive_policy():
      pass

    # Modify:
    #  self.pa_vector:      power allocation, sqrt(vec) is gain
    #  self.ac_vector:      artificial channel, channel impulse response (complex)
    #  self.mod_map:        bit loading/modulation scheme
    #  self.assignment_map: subcarrier to user assignment
    #  self.tx_amplitude:   RMS level of sent signal

################################################################################

def main():
  start_resource_manager(resource_manager, "PA")

if __name__ == '__main__':
  try:
    main()
  except KeyboardInterrupt:
    pass
