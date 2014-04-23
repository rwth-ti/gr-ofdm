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
from numpy import numarray,mean,var,std,sqrt,logspace
import time

import array

from resource_manager_base import resource_manager_base,start_resource_manager

class resource_manager (resource_manager_base):
  def __init__(self,orb):
    resource_manager_base.__init__(self,orb)

    # set initial parameters
    self.required_ber = 1e-4
    self.constraint = 4000.0   # rate or power, RMS!
    self.setup_time = 6*1000   # ms
    self.data_rate= 365079     # implicitly exposed to GUI
    self.tx_amplitude = 5000   # RMS!

    # self.subcarriers

    self.state = 0
    self.txpow_range = logspace(6, 8, 20, True, 10)# range(1000**2,3000**2,1000**2)
    self.cur_txpow_ind = 0

    self.mod_range = range(1,9)
    self.cur_mod_ind = 0

    self.ber_vec = []
    self.snr_vec = []

    self.results = []

  def work(self):
    if self.state == 0:
      # setup measurement
      self.state = 1

      txpow = self.txpow_range[self.cur_txpow_ind]
      self.tx_amplitude = sqrt(txpow)
      self.cur_txpow_ind += 1

      m = self.mod_range[self.cur_mod_ind]
      self.mod_map = [m] * self.subcarriers

      if len(self.results) > 0:
        f = open("data/snrgap_results.tmp", "a")
        f.write(time.asctime())
        f.write("\n")
        f.write(str(self.results[len(self.results)-1]))
        f.write("\n")
        f.close()

      if self.cur_txpow_ind == len(self.txpow_range):
        self.cur_mod_ind += 1
        self.cur_txpow_ind = 0

        if self.cur_mod_ind == len(self.mod_range):
          f = open("data/snrgap_results.txt", "a")
          f.write("-----------------------------------------------------------\n")
          f.write(time.asctime())
          f.write("\n")
          f.write(str(self.results))
          f.write("\n")
          f.close()

          self.cur_mod_ind = 0
          self.results = []

      print "Current bit loading per subchannel: %d" % (m)
      print "Current transmit amplitude %d and power %d" % (self.tx_amplitude,txpow)
    elif self.state == 1:
      self.rx_snr.flush()
      self.rx_ber.flush()
      self.snr_vec = numarray.array([],typecode=numarray.Float)
      self.ber_vec = numarray.array([],typecode=numarray.Float)

      snr_vec_max = 1e4
      ber_vec_max = 1e4

      while 1:
        snr_vec = numarray.array(self.get_snr(),typecode=numarray.Float)
        current_ber = numarray.array(self.rx_ber.get_data(),typecode=numarray.Float)

        snr_vec = 10**(snr_vec/10)

        self.ber_vec = concatenate([self.ber_vec,current_ber])
        self.snr_vec = concatenate([self.snr_vec,snr_vec])

        mean_ber = mean(self.ber_vec)
        std_ber = std(self.ber_vec)
        mean_snr = mean(self.snr_vec)
        std_snr = std(self.snr_vec)

        dev1 = std_snr/mean_snr
        dev2 = std_ber/mean_ber

        print "SNR: mean %.2f, std %.2f, dev %.2f   BER: mean %.5f, std %.5f, dev %.2f  State %3d %3d" \
          % (mean_snr,std_snr,dev1,mean_ber,std_ber,dev2,len(self.snr_vec)/snr_vec_max*100,len(self.ber_vec)/ber_vec_max*100)

        try:
          time.sleep(1.0)
        except KeyboardInterrupt:
           break

        cond1 = len(self.ber_vec) > 1000 and len(self.ber_vec) > 1000/mean_ber
        cond2 = (abs(dev1) < 0.05 or len(self.snr_vec) > snr_vec_max) and len(self.snr_vec) > 1000
        cond3 = (mean_ber < 1e-7 or dev2 < 0.05 or len(self.ber_vec) > 1000/mean_ber) or len(self.ber_vec) > ber_vec_max

        if len(self.snr_vec) > snr_vec_max and len(self.ber_vec) > ber_vec_max: #cond1 and cond2 and cond3:
          tmpfile = "snr.dat"
          fileobj = open(tmpfile, mode='ab')
          outvalues = array.array('f')
          self.snr_vec = concatenate([[len(self.snr_vec),self.tx_amplitude,self.mod_map[0]],self.snr_vec])
          outvalues.fromlist( self.snr_vec.astype(float).tolist() )#
          outvalues.tofile(fileobj)
          fileobj.close()

          tmpfile = "ber.dat"
          fileobj = open(tmpfile, mode='ab')
          outvalues = array.array('f')
          self.ber_vec = concatenate([[len(self.ber_vec),self.tx_amplitude,self.mod_map[0]],self.ber_vec])
          outvalues.fromlist(self.ber_vec.astype(float).tolist() )
          outvalues.tofile(fileobj)
          fileobj.close()

          self.results.append([self.tx_amplitude,self.mod_map[0],mean_snr,std_snr,mean_ber,std_ber])
          self.state = 0
          break



    # Input:
    #  self.required_ber
    #  self.constraint
    #  self.current_ber
    #  self.ac_vector (if sounder connected)



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
