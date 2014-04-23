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

from numpy import concatenate,abs,numarray,argmin,argmax,zeros,inf,sqrt,log10, ceil
from scipy.special import erfcinv
import numpy
import random
import time, array

from gnuradio import eng_notation
from configparse import OptionParser

from time import strftime, gmtime

import logging

from resource_manager_base import resource_manager_base,start_resource_manager

from corba_stubs import ofdm_ti

class resource_manager (resource_manager_base):
  def __init__(self,orb,options):
    resource_manager_base.__init__(self,orb,options=options,loggerbase="suw.")

    self.logger = logging.getLogger("suw.rm")
    self.logger.setLevel(logging.DEBUG)
    # set initial parameters
    self.required_ber = 1e-3
    self.constraint = 8000.0   # rate or power, RMS!
    self.setup_time = 10000   # ms
    self.data_rate= 365079     # implicitly exposed to GUI

    #self.data_rate= self.subcarriers*4*9/12/(self.fft_length+self.cp_length)/self.bandwidth
    if self.options.usrp2:
        self.tx_amplitude = 0.8   # RMS!
        self.scale = 1/32768.  #Still experimental
    else:
        self.tx_amplitude = 8000
    
    #!!! dummy setup of parameters using options -> improve !!!
    self.bandwidth = options.bandwidth
    if options.dyn_freq:
        self.freq = options.freq    
        self.tx_freq = options.freq
        self.rx_freq = options.freq

    # self.subcarriers
    self.store_ctrl_events = False

    self.auto_state = 0
    self.state1_cntr = 0

    self.options = options

  def work(self):
    self.query_sounder()
    print self.ac_vector
    self.ac_vector = [0.0+0.0j]*self.ac_vlen
    if self.ac_vlen >= 8:
      self.ac_vector[0] = (2*10**(-0.452))
      self.ac_vector[3] = (10**(-0.651))
      self.ac_vector[7] = (10**(-1.151))
      print self.ac_vector

    rxperf = self.get_rx_perf_meas()
    if len(rxperf) == 0:
      # TODO: recover if necessary
      return

    if self.store_ctrl_events:
      self.process_received_events(rxperf)

    if self.options.automode:
#      self.logger.warning("Automatic Measurement mode activated")

      self.logger.debug("Auto state is %d"%(self.auto_state))
      if self.auto_state == 0:

        self.state1_cntr = 0
        self.strategy_mode = ofdm_ti.PA_Ctrl.reset
        self.constraint = 2000
        self.required_ber = 1e-3
        self.auto_state = 1
      elif self.auto_state == 1:
        self.state1_cntr += 1
        if self.state1_cntr > 10:
          self.strategy_mode = ofdm_ti.PA_Ctrl.rate_adaptive
          self.constraint = 4000
          self.auto_state = 2
          self.store_ctrl_events = True
          self.start_measurement()
      elif self.auto_state == 2:
        if len(self.bervec) > 20000:
          self.end_measurement()
          self.store_ctrl_events = False
          self.auto_state = 0


    rxperf = rxperf[len(rxperf)-1]
    current_ber = rxperf.ber
    snr_mean = rxperf.snr
    ctf = rxperf.ctf

#    print "Received performance measure estimate:"
#    print repr(rxperf)
#    print "======================================"
    if self.options.usrp2:
        cur_tx_power = (self.tx_amplitude/self.scale)**2
    else:
        cur_tx_power = self.tx_amplitude**2     # average power
    #cur_tx_constraint = self.constraint**2  # dito

    # Input:
    #  self.required_ber
    #  self.constraint
    #  self.current_ber
    #  self.ac_vector (if sounder connected)
    

    if self.is_reset_mode():
      print "Current mode is reset mode"
      self.pa_vector = [1]*self.subcarriers
      self.mod_map = [2]*self.subcarriers
      self.assignment_map = [1] * self.subcarriers
      
     #for ii in range (self.subcarriers/4):
     ##     self.pa_vector[ii]=4.0
      #    self.mod_map[ii] = [2]
      #    self.assignment_map[ii] = [1]
          
      #self.pa_vector = concatenate([[float(2.0)]*(self.subcarriers/2), [float(0.0)]*(self.subcarriers -self.subcarriers/2)])
      #self.mod_map = concatenate([[2]*(self.subcarriers/2),[0]*(self.subcarriers-self.subcarriers/2)])
        #self.mod_map = [2]*self.subcarriers
      #self.assignment_map = concatenate([[1]*(self.subcarriers/2), [0]*(self.subcarriers -self.subcarriers/2)])    
    
      #self.tx_freq = self.freq# - self.bandwidth/2 +   random.randint(100000,1400000)
      if self.options.dyn_freq:
          print "Start frequency:", self.freq
          self.tx_freq = newtx = self.freq -self.bandwidth*2 + random.randint(100000,1400000)
          self.rx_freq = self.tx_freq
          print "New tx frequency:", newtx

      if self.options.usrp2:
        self.tx_amplitude = self.scale*self.constraint
      else:
        self.tx_amplitude = self.constraint

      frame_length_samples = 12*self.block_length # FIXME constant
      bits_per_frame = 2*self.subcarriers*9       # FIXME constant
      frame_duration = frame_length_samples/self.bandwidth
      self.data_rate = bits_per_frame/frame_duration

      ###################################
      c_ber = max(current_ber, 1e-7)

      snr_mean_lin = 10**(snr_mean/10.0)
      print "Current SNR:", snr_mean
      print "Current BER:", c_ber
      snr_func_lin = 2.0*(erfcinv(c_ber)**2.0)
      snr_func = 10*log10(snr_func_lin)
      print "Func. SNR:", snr_func
      delta = self._delta = snr_mean_lin/snr_func_lin
      print "Current delta", delta
      self._agg_rate = 2


      #################################

      pass
    elif self.is_margin_adaptive_policy():
      print "Current mode is margin adaptive mode"
      cur_bit_constraint = ceil(self.constraint*self.block_length/self.bandwidth*12/9)
      self.margin_adaptive_policy(ctf, cur_tx_power, cur_bit_constraint, snr_mean)
      #pass
    elif self.is_rate_adaptive_policy():
      print "Current mode is rate adaptive mode"
      cur_tx_constraint = self.constraint**2
      self.rate_adaptive_policy(ctf, cur_tx_power, cur_tx_constraint, snr_mean)


    if self.auto_state == 2 and self.options.automode:
      self.logger.debug("####################### Already collected %d ################################"%(len(self.bervec)))
    # Modify:
    #  self.pa_vector:      power allocation, (vec) is gain
    #  self.mod_map:        bit loading/modulation scheme
    #  self.assignment_map: subcarrier to user assignment
    #  self.tx_amplitude:   RMS level of sent sigself.subcarriers
    #  self.ac_vector:      artificial channel, channel impulse response (complex)
    #                       if sounder not connected

  def rate_adaptive_policy(self,ctf,cur_tx_power,cur_tx_constraint,snr_db):
    ber = max(self.required_ber,1e-7)

    snrf = (2)*(erfcinv(ber)**2.0)   #*3.2
    snr_corr = snrf*self._delta

    #gamma = (2.0/3.0)*(erfcinv(ber)**2.0)   #*3.2

    gamma = snr_corr/(2**(self._agg_rate)-1)    #*3.2


    print "required ber",ber
    print "snr gap (dB) for req. ber",10*log10(gamma)

    N = self.subcarriers

    

    (b,e) = levin_campello(self.mod_map, N, cur_tx_constraint,
                           snr_db, ctf, gamma, cur_tx_power)

    b = numarray.array(b)
    e = numarray.array(e)
    a = numarray.array(zeros(len(self.assignment_map)))

    if sum(b < 0) > 0:
      print "WARNING: bit loading < 0"
      b[b < 0] = 0

    a[b > 0] = 1
    

        
    

        

    txpow = sum(e)
    e = e / txpow * N

    print "txpow", txpow
    print "tx amplitude",sqrt(txpow)
    print numarray.array(map(lambda x: "%.2f" % (x), e))
    print numarray.array(map(lambda x: "%d" % (x),b))

    #return

    if self.options.usrp2:
        self.tx_amplitude = sqrt(txpow)*self.scale
    else:
        self.tx_amplitude = sqrt(txpow)
    self.mod_map = list(b)
    self.pa_vector = list(e)
    self.assignment_map = list(a)

    frame_length_samples = 12*self.block_length # FIXME constant
    bits_per_frame = sum(b)*9                   # FIXME constant
    frame_duration = frame_length_samples/self.bandwidth
    self.data_rate = bits_per_frame/frame_duration
    print "Datarate",self.data_rate
    print "TX amplitude",self.tx_amplitude
    #print "TX amplitude",self.tx_amplitude/self.scale

    ####New adaptation -> Experimental ########################
    # Calculating the aggregate rate per used subcarrier
    agg_rate =self._agg_rate = sum(b)/sum(a)
    print "Aggregate rate:", agg_rate

    rxperf = self.get_rx_perf_meas()
    if len(rxperf) == 0:
      return

    rxperf = rxperf[len(rxperf)-1]
    current_ber = rxperf.ber
    snr_mean = rxperf.snr
    ctf = rxperf.ctf

    #Taking care of only used subcarriers
    str_corr = sum(ctf*a)/sum(a) #Improve lin <-> square
    print"STR CORR:", str_corr

    ##
    c_ber = max(current_ber, 1e-7)
    snr_mean_lin = 10**(snr_mean/10.0)
    print "Current SNR:", snr_mean
    print "Current BER:", c_ber
    snr_func_lin = 2.0*(erfcinv(c_ber)**2.0)
    snr_func = 10*log10(snr_func_lin)
    print "Func. SNR:", snr_func
    delta = self._delta = snr_mean_lin/snr_func_lin*(str_corr**2)
    print "Current delta", delta


    ###########################################################

################################################################################

  def margin_adaptive_policy(self,ctf,cur_tx_power,cur_bit_constraint,snr_db):
    ber = max(self.required_ber,1e-7)

    snrf = (2)*(erfcinv(ber)**2.0)   #*3.2
    snr_corr = snrf*self._delta

    #gamma = (2.0/3.0)*(erfcinv(ber)**2.0)   #*3.2

    #gamma = snr_corr/3.0    #*3.2
    gamma = snr_corr/(2**(self._agg_rate)-1)

    print "required ber",ber
    print "snr gap (dB) for req. ber",10*log10(gamma)

    N = self.subcarriers

    (b,e) = levin_campello_margin(self.mod_map, N, cur_bit_constraint,
                           snr_db, ctf, gamma, cur_tx_power)

    b = numarray.array(b)
    e = numarray.array(e)
    a = numarray.array(zeros(len(self.assignment_map)))

    if sum(b < 0) > 0:
      print "WARNING: bit loading < 0"
      b[b < 0] = 0

    a[b > 0] = 1

    txpow = sum(e)
    e = e / txpow * N

    print "txpow", txpow
    print "tx amplitude",sqrt(txpow)
    print numarray.array(map(lambda x: "%.2f" % (x), e))
    print numarray.array(map(lambda x: "%d" % (x),b))

    #return

    if self.options.usrp2:
        self.tx_amplitude = sqrt(txpow)*self.scale
    else:
        self.tx_amplitude = sqrt(txpow)

    self.mod_map = list(b)
    self.pa_vector = list(e)
    self.assignment_map = list(a)

    frame_length_samples = 12*self.block_length # FIXME constant
    bits_per_frame = sum(b)*9                   # FIXME constant
    frame_duration = frame_length_samples/self.bandwidth
    self.data_rate = bits_per_frame/frame_duration
    print "Datarate",self.data_rate

        ####New adaptation -> Experimental ########################
    # Calculating the aggregate rate per used subcarrier
    agg_rate =self._agg_rate = sum(b)/sum(a)
    print "Aggregate rate:", agg_rate

    rxperf = self.get_rx_perf_meas()
    if len(rxperf) == 0:
      return

    rxperf = rxperf[len(rxperf)-1]
    current_ber = rxperf.ber
    snr_mean = rxperf.snr
    ctf = rxperf.ctf

    #Taking care of only used subcarriers
    str_corr = sum(ctf*a)/sum(a) #Improve lin <-> square
    print"STR CORR:", str_corr

    ##
    c_ber = max(current_ber, 1e-7)
    snr_mean_lin = 10**(snr_mean/10.0)
    print "Current SNR:", snr_mean
    print "Current BER:", c_ber
    snr_func_lin = 2.0*(erfcinv(c_ber)**2.0)
    snr_func = 10*log10(snr_func_lin)
    print "Func. SNR:", snr_func
    delta = self._delta = snr_mean_lin/snr_func_lin*(str_corr**2)
    print "Current delta", delta


    ###########################################################

  def start_measurement(self):
    self.bervec = list()
    self.snrvec = list()
    self.datarate_vec = list()
    self.txamp_vec = list()
    self.start_time = strftime("%a, %d %b %Y %H:%M:%S +0000", gmtime())

    self.filename_prefix = strftime("%Y%m%d%H%M%S",gmtime())

  def end_measurement(self):
    bervec = numpy.array(self.bervec)
    snrvec = numpy.array(self.snrvec)
    datarate_vec = numpy.array(self.datarate_vec)
    txamp_vec = numpy.array(self.txamp_vec)
    berout = array.array('f')
    snrout = array.array('f')
    datarate_out = array.array('f')
    txamp_out  = array.array('f')
    berout.fromlist(bervec.astype(float).tolist())
    snrout.fromlist(snrvec.astype(float).tolist())
    datarate_out.fromlist(datarate_vec.astype(float).tolist())
    txamp_out.fromlist(txamp_vec.astype(float).tolist())

    filename_prefix=self.filename_prefix
    f_ber = open( filename_prefix+"_ber.float", "wb" )
    f_snr = open( filename_prefix+"_snr.float", "wb" )
    f_datarate = open( filename_prefix+"_datarate.float", "wb" )
    f_txamp = open( filename_prefix+"_txamp.float", "wb" )
    f_nfo = open( filename_prefix+"_nfo.txt", "w" )


    berout.tofile(f_ber)
    snrout.tofile(f_snr)
    datarate_out.tofile(f_datarate)
    txamp_out.tofile(f_txamp)

    f_nfo.write("Start time: %s\n"%(self.start_time))
    f_nfo.write( "End time: %s\n" %(strftime("%a, %d %b %Y %H:%M:%S +0000", gmtime())))
    if self.is_margin_adaptive_policy():
      f_nfo.write("Margin adaptive\n")
    elif self.is_rate_adaptive_policy():
      f_nfo.write("rate adaptive\n")
    else:
      f_nfo.write("error\n")
    f_nfo.write("Required BER: %.8g\n"%(self.required_ber))

    f_ber.close()
    f_snr.close()
    f_datarate.close()
    f_txamp.close()




  def process_received_events(self,rxperf):
    assert(len(rxperf)>0)


    for x in rxperf:

      if x.rx_id in self.ctrl_events.keys():

        previd = x.rx_id - 1
        if previd < 0:
          previd += self.max_tx_id

        if previd in self.ctrl_events.keys():
          del self.ctrl_events[previd]

#        self.logger.debug("Found corresponding RX Id in control event buffer")

        ev = self.ctrl_events[x.rx_id]
        self.bervec.append(x.ber)
        self.snrvec.append(x.snr)
        self.datarate_vec.append(ev.datarate)
        self.txamp_vec.append(ev.tx_amplitude)


      else:
        pass
#        self.logger.warning("RX ID %d was not found in ctrl event buffer" %(x.rx_id))




  def add_options(normal, expert):
    """
    Adds receiver-specific options to the Options Parser
    """
    resource_manager_base.add_options(normal,expert)
    normal.add_option("", "--automode",
                      action="store_true",
                      default=False,
                      help="Activate automatic measurement mode")
    expert.add_option("", "--usrp2",
                      action="store_true",
                      default=False,
                      help="USRP2")
    expert.add_option("-f", "--freq", type="eng_float", default=None,
                      help="set transmit frequency to FREQ [default=%default]", metavar="FREQ")
    expert.add_option("", "--bandwidth", type="eng_float", default='500k',
                      help="set total bandwidth. [default=%default]")
  add_options = staticmethod(add_options)

################################################################################

#def levin_campello(b,N,constraint,snr_db,ctf,gamma,txpow):
#  ctf = numarray.array(ctf)
#
#  # channel to noise ratio
#  snr = 10**(snr_db/10)
#  avtxpow = txpow/N
#  norm_ctf_sqrd = abs(ctf)**2 / (sum(abs(ctf)**2)/N)
#  g = snr/avtxpow * norm_ctf_sqrd
#
#  beta = 1    # smallest bit increment
#  inc_energy = lambda b,n: inc_energy_base(b,n,g,gamma,beta)
#  energy = lambda b,n: gamma/g[n]*(2**b[n]-1)
#
#  # prepare
#  ie1 = map(lambda x: inc_energy(b+beta,x), range(N))
#  ie2 = map(lambda x: inc_energy(b     ,x), range(N))
#
#  # energy efficiency
#  (ie1,ie2,b) = EF(inc_energy,b,beta,ie1,ie2)
#
#  # e-tightness
#  S = sum(map(lambda x: energy(b,x),range(N)))
#  (ie1,b) = ET(b,beta,constraint,S,inc_energy,ie1)
#
#  # compute energy distribution
#  e = map(lambda x: energy(b,x),range(N))
#
#  return (b,e)

def levin_campello(b,N,constraint,snr_db,ctf,gamma,txpow):
  ctf = numarray.array(ctf)
  b = numarray.array(b)

  # gain to noise ratio
  snr = 10**(snr_db/10)
  avtxpow = txpow/N # average tx power
  norm_ctf_sqrd = abs(ctf)**2 / (sum(abs(ctf)**2)/N)
  g = snr/avtxpow * norm_ctf_sqrd

  # prepare
  beta = 1
  gn = prepare_table(g,gamma,beta)
  min_ie = lambda b : min_c(gn,b/beta)
  max_ie = lambda b : max_c(gn,b/beta)
  energy = lambda b,n : gamma/g[n]*(2.0**b[n]-1)

  # energy efficiency
  b = EF(b,beta,min_ie,max_ie)

  # e-tightness
  S = sum(map(lambda x : energy(b,x),range(N)))
  b = ET(b,beta,constraint,S,min_ie,max_ie)

  # set changes
  e = map(lambda x :energy(b,x),range(N))
  print "sum(e)",sum(e)

  b = list(b)
  return (b,e)

def levin_campello_margin(b,N,constraint,snr_db,ctf,gamma,txpow):
  ctf = numarray.array(ctf)
  b = numarray.array(b)

  # gain to noise ratio
  snr = 10**(snr_db/10)
  avtxpow = txpow/N # average tx power
  norm_ctf_sqrd = abs(ctf)**2 / (sum(abs(ctf)**2)/N)
  g = snr/avtxpow * norm_ctf_sqrd

  # prepare
  beta = 1
  gn = prepare_table(g,gamma,beta)
  min_ie = lambda b : min_c(gn,b/beta)
  max_ie = lambda b : max_c(gn,b/beta)
  energy = lambda b,n : gamma/g[n]*(2.0**b[n]-1)

  # energy efficiency
  b = EF(b,beta,min_ie,max_ie)

  # e-tightness
  #S = sum(map(lambda x : energy(b,x),range(N)))
#  print "sum_b", sum(b)
  #b_sum=sum(map(lambda x : b(x),range(N)))
  b_sum=sum(b)
  b = BT(b,beta,constraint,b_sum,min_ie,max_ie)

  # set changes
  e = map(lambda x :energy(b,x),range(N))
  print "sum(e)",sum(e)

  b = list(b)
  return (b,e)
#########################################################################################
def prepare_table(g,gamma,beta):
  max_nbits = 8
  nsubc = len(g)

  gn = zeros((max_nbits/beta+1,nsubc))

  for b in range(beta,max_nbits+beta,beta):
    for n in range(nsubc):
        gn[b/beta][n] = gamma/g[n]*(2.0**b)*(1.0-2.0**(-beta))

  return gn

def min_c(gn,ind):
    # constrained minimum search over incremental energies
    # for each index in ind(:), find minimum gn(index) if index within bounds

    max_ind = len(gn)
    nsubc = len(gn[0])

    ie = inf
    c = 0
    for n in range(nsubc):
        i = ind[n]
        if i >= max_ind:
            continue
        if ie > gn[i][n]:
            ie = gn[i][n]
            c = n

    return (ie,c)

def max_c(gn,ind):
    # constrained maximum search over incremental energies
    # for each index in ind(:), find maximum gn(index) if index within bounds

    max_ind = len(gn)
    nsubc = len(gn[0])

    ie = 0.0
    c = 0
    for n in range(nsubc):
        i = ind[n]
        if i >= max_ind:
            continue
        if ie < gn[i][n]:
            ie = gn[i][n]
            c = n
    return (ie,c)

# Energy efficiency
#
# make bit loading vector b energy efficient
#
# smallest bit increment: beta
# bit loading: b
# minimum search over incremental energy: min_ie
# maximum search over incremental energy: max:ie
def EF(b,beta,min_ie,max_ie):
  (ie_m,m) = min_ie(b+beta)
  (ie_n,n) = max_ie(b)

  # EF
  while (m >= 0 and n >= 0) and (ie_m < ie_n): # inc_energy(b+beta,m) < inc_energy(b,n)
      b[m] = b[m] + beta
      b[n] = b[n] - beta

#      print "Swapping bits from %d to %d" %(m,n)

      (ie_m,m) = min_ie(b+beta)
      (ie_n,n) = max_ie(b)

  return b

#def EF(inc_energy,b,beta,ie1,ie2):
#  m = argmin(ie1)
#  n = argmax(ie2)
#
#  i = 0
#
#  while (ie1(m) < ie2(m)) and i < 10000:
#    b[m] += beta
#    b[n] -= beta
#
#    ie1[m] = inc_energy(b+beta, m)
#    ie1[n] = inc_energy(b+beta, n)
#
#    ie2[m] = inc_energy(b, m)
#    ie2[n] = inc_energy(b, n)
#
#    m = argmin(ie1)
#    n = argmax(ie2)
#
#    i += 1
#
#  return (ie1,ie2,b)


# E-Tightness
#
# Ensure energy constraint is met
#
# bit loading vector: b
# smallest bit increment: beta
# energy constraint: K
# current total energy: S
# minimum search over incremental energy: min_ie
# maximum search over incremental energy: max:ie

def ET(b,beta,K,S,min_ie,max_ie):
#function [b] = ET(b,beta,K,S,min_ie,max_ie)

  (ie_m,m) = min_ie(b+beta)

  print "Constraint K",K
  print "Energy level S",S

  # ET
  while ((m >= 0) and ((K - S) >= ie_m)) or ((K - S) < 0):
      if (K-S) < 0:
          (ie_n,n) = max_ie(b)
          if ie_n >= 0:
              S = S - ie_n
              b[n] = b[n] - beta
#              print "Reducing bit loading for subchannel %d to achieve constraint" % (n)
          else:
              raise SystemError, \
                  "ERROR: exceeding constraint, but maximum incremental energy to be reduced is zero"
              break
      else:
          S = S + ie_m
          b[m] = b[m] + beta;
#          print "Increasing bit loading for subchannel %d to achieve constraint" % (m)

      (ie_m,m) = min_ie(b+beta);


  print "Energy level S",S

  return b
#
def BT(b,beta,K,BS,min_ie,max_ie):
#function [b] = ET(b,beta,K,S,min_ie,max_ie)

  #(ie_m,m) = min_ie(b+beta)

  print "Constraint K",K
  print "Bit_rate",BS

  # ET
  while BS != K:
      if (BS-K) > 0:
          (ie_n,n) = max_ie(b)
          if ie_n >= 0:
              BS = BS - beta
              b[n] = b[n] - beta
#              print "Reducing bit loading for subchannel %d to achieve constraint" % (n)
          else:
              raise SystemError, \
                  "ERROR: exceeding constraint, but maximum incremental energy to be reduced is zero"
              break
      else:
          (ie_m,m) = min_ie(b+beta)
          BS = BS + beta
          b[m] = b[m] + beta;
#          print "Increasing bit loading for subchannel %d to achieve constraint" % (m)
#          print "Bit_rate", BS

      #(ie_m,m) = min_ie(b+beta);


  print "Bit_rate",BS

  return b
#
#def ET(b,beta,K,S,inc_energy,ie1):
#  while((K - S) >= min(ie1)) or ((K - S) < 0):
#    if (K - S) < 0:
#      n = argmax(ie1)
#      S = S - inc_energy(b,n)
#      b[n] -= beta
#      ie1[n] = inc_energy(b+beta,n)
#    else:
#      m = argmin(ie1)
#      S = S + inc_energy(b+beta,m)
#      b[m] += beta
#      ie1[m] = inc_energy(b+beta,m)
#
#  return (ie1,b)



#def inc_energy_base(b,n,g,gamma,beta):
#  e = gamma/g(n)*2**b(n)*(1-2**-beta)
#
#  if b(n) > 8:
#    e = 1e8*e
#  if b(n) <= 0:
#    e = 0





################################################################################

def main():
  logger = logging.getLogger("suw")
  logger.setLevel(logging.DEBUG)

#  logfilename = "suw_" + strftime("%Y%m%d%H%M%S",gmtime()) + ".log"


#  fh = logging.FileHandler(logfilename)
#  fh.setLevel(logging.DEBUG)

  ch = logging.StreamHandler()
  ch.setLevel(logging.DEBUG)

#  formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
#  fh.setFormatter(formatter)
#  ch.setFormatter(formatter)

#  logger.addHandler(fh)
  logger.addHandler(ch)

#  logger.info("Log filename is %s" %(logfilename))

  parser = OptionParser(conflict_handler="resolve")

  expert_grp = parser.add_option_group("Expert")

  resource_manager.add_options(parser, expert_grp)

  parser.add_option(
    "-c", "--cfg",
    action="store", type="string", default=None,
    help="Specifiy configuration file, default: none",
    config="false" )

  (options, args) = parser.parse_args()

  if options.cfg is not None:
    (options,args) = parser.parse_args(files=[options.cfg])
    print "Using configuration file %s" % ( options.cfg )


  start_resource_manager(resource_manager, "PA",options)

if __name__ == '__main__':
  try:
    main()
  except KeyboardInterrupt:
    pass
