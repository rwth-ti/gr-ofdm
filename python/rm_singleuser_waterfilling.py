#!/usr/bin/env python

from numpy import concatenate,abs,numarray,argmin,argmax,zeros,inf,sqrt,log10
from scipy.special import erfcinv
import numpy
import time

from resource_manager_base import resource_manager_base,start_resource_manager

from corba_stubs import ofdm_ti

class resource_manager (resource_manager_base):
  def __init__(self,orb):
    resource_manager_base.__init__(self,orb)

    # set initial parameters
    self.required_ber = 1e-4
    self.constraint = 4000.0   # rate or power, RMS!
    self.setup_time = 3*1000   # ms
    self.data_rate= 365079     # implicitly exposed to GUI
    self.tx_amplitude = 5000   # RMS!
    
    self.strategy_mode = ofdm_ti.PA_Ctrl.rate_adaptive
    
    self.ber_state = 1e-7
    self.last_ber_err = 0.0

    # self.subcarriers

  def work(self):
    #self.query_sounder()
    
    rxperf = self.get_rx_perf_meas()
    if len(rxperf) == 0:
      return

    rxperf = rxperf[len(rxperf)-1]
    current_ber = rxperf.ber
    snr_mean = rxperf.snr
    ctf = rxperf.ctf
    
#    print "Received performance measure estimate:"
#    print repr(rxperf)
#    print "======================================"
    
    cur_tx_power = self.tx_amplitude**2     # average power
    cur_tx_constraint = self.constraint**2  # dito

    # Input:
    #  self.required_ber
    #  self.constraint
    #  self.current_ber
    #  self.ac_vector (if sounder connected)

    if self.is_reset_mode():
      print "Current mode is reset mode"
      self.pa_vector = [1.0]*self.subcarriers
      self.mod_map = [2]*self.subcarriers
      self.assignment_map = [1] * self.subcarriers
      pass
    elif self.is_margin_adaptive_policy():
      print "Current mode is margin adaptive mode"
      pass
    elif self.is_rate_adaptive_policy():
      print "Current mode is rate adaptive mode"
      self.rate_adaptive_policy(ctf, cur_tx_power, cur_tx_constraint, snr_mean, current_ber)

    # Modify:
    #  self.pa_vector:      power allocation, sqrt(vec) is gain
    #  self.mod_map:        bit loading/modulation scheme
    #  self.assignment_map: subcarrier to user assignment
    #  self.tx_amplitude:   RMS level of sent sigself.subcarriers
    #  self.ac_vector:      artificial channel, channel impulse response (complex)
    #                       if sounder not connected

  def rate_adaptive_policy(self,ctf,cur_tx_power,cur_tx_constraint,snr_db,cur_ber):
    ber = max(self.required_ber,1e-7)
    
#    a=0.0004
#    b=0.00001
#    
#    
#    ber_err = ber-cur_ber
#    self.ber_state = max(1e-12,self.ber_state + (a+b)*ber_err - b*self.last_ber_err)
#    self.last_ber_err = ber_err
#    
#    ber = min(.5,max(1e-12,self.ber_state))
#    
#    print "current ber",cur_ber
#    print "ber_err",ber_err
#    print "ber state",self.ber_state


    gamma = (2.0/3.0)*(erfcinv(ber)**2.0)   *3.2
    #gamma = ((2./3.)*(erfcinv(ber))**2.0)
    print "input ber",ber,"required ber",self.required_ber
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
#    print numarray.array(map(lambda x: "%.2f" % (x), e))
#    print numarray.array(map(lambda x: "%d" % (x),b))

    #return

    self.tx_amplitude = sqrt(txpow)
    self.mod_map = list(b)
    self.pa_vector = list(e)
    self.assignment_map = list(a)

    frame_length_samples = 12*self.block_length # FIXME constant
    bits_per_frame = sum(b)*9                   # FIXME constant
    frame_duration = frame_length_samples/self.bandwidth
    self.data_rate = bits_per_frame/frame_duration
    print "Datarate",self.data_rate

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
    c = -1
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
    c = -1
    for n in range(nsubc):
        i = ind[n]
        if i >= max_ind:
            continue
        if i <= 1:
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
          if ie_n >= 0 and n >= 0:
              S = S - ie_n
              b[n] = b[n] - beta
#              print "Reducing bit loading for subchannel %d to achieve constraint" % (n)
          else:
#              raise SystemError, \
#                  "ERROR: exceeding constraint, but maximum incremental energy to be reduced is zero"
              print "ERROR: exceeding constraint, but maximum incremental energy to be reduced is zero"
              break
      else:
          S = S + ie_m
          b[m] = b[m] + beta;
#          print "Increasing bit loading for subchannel %d to achieve constraint" % (m)

      (ie_m,m) = min_ie(b+beta);


  print "Energy level S",S

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
  start_resource_manager(resource_manager, "PA")

if __name__ == '__main__':
  try:
    main()
  except KeyboardInterrupt:
    pass
