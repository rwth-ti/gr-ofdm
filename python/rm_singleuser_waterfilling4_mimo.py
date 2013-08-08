#!/usr/bin/env python

from numpy import concatenate,abs,numarray,argmin,argmax,zeros,inf,sqrt,log10, ceil, logspace
from scipy.special import erfcinv
import numpy
import time, array

from gnuradio import eng_notation
from configparse import OptionParser

from time import strftime, gmtime

import logging

from resource_manager_base_mimo import resource_manager_base,start_resource_manager

from corba_stubs import ofdm_ti
import os

class resource_manager (resource_manager_base):
  def __init__(self,orb,options):
    resource_manager_base.__init__(self,orb,options=options,loggerbase="suw.")

    self.logger = logging.getLogger("suw.rm")
    self.logger.setLevel(logging.DEBUG)
    # set initial parameters
    self.required_ber = 1e-3
    self.constraint = 8000.0   # rate or power, RMS!
    self.setup_time = 4000   # ms
    self.data_rate= 365079     # implicitly exposed to GUI

    #self.data_rate= self.subcarriers*4*9/12/(self.fft_length+self.cp_length)/self.bandwidth
    if self.options.usrp2:
        self.tx_amplitude = 0.3   # RMS!
        self.scale = 1/32768.  #Still experimental
    else:
        self.tx_amplitude = 12000

    # self.subcarriers
    self.store_ctrl_events = False

    self.auto_state = 0
    self.state1_cntr = 0

    self.options = options
    
    if self.options.automode:
        
        self.num_points = options.points
        self.nrounds = options.nrounds
        self.automode_constr = options.berconstr
        self.constr_max_log = log10(options.ub**2)
        self.constr_min_log = log10(options.lb**2)
        self.constr_range = logspace(self.constr_min_log,self.constr_max_log,self.num_points)
        self.cur_constr_ind = 0
        self.start_time = strftime("%a, %d %b %Y %H:%M:%S +0000", gmtime())
        self.dirname = "Rate_Simulation_"+strftime("%Y_%m_%d_%H_%M_%S",gmtime())
        if not os.path.isdir("./" + self.dirname + "/"):
            os.mkdir("./" + self.dirname + "/")
            
        f_info = open( "./" + self.dirname + "/"+"Simulation_nfo.txt", "w" )
        f_info.write("Start time: %s\n"%(self.start_time))
        
        f_info.write( "Lower bound: %d\n" %(options.lb))
        f_info.write( "Upper bound: %d\n" %(options.ub))
        f_info.write( "Required BER: %f\n" %(options.berconstr))
        f_info.write( "Number of points: %d\n" %(options.points))
        f_info.write( "Number of rounds: %d\n" %(options.nrounds))
        f_info.close()
        

  def work(self):
    self.query_sounder()
    print self.ac_vector
    self.ac_vector = [0.0+0.0j]*self.ac_vlen
    if self.ac_vlen >= 8:
      self.ac_vector[0] = (2*10**(-0.452))
      self.ac_vector[3] = (10**(-0.651))
      self.ac_vector[7] = (10**(-1.151))
        #self.ac_vector[3] = 0.3267 
        #self.ac_vector[4] = 0.8868
        #self.ac_vector[5] = 0.3267
    print self.ac_vector

    rxperf = self.get_rx_perf_meas()
    self.required_ber = reqber = self._get_required_ber()
    print "required BER", reqber
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
        self.required_ber = self.automode_constr
        print "Requested BER constraint: ", self.required_ber
        self.auto_state = 1
      elif self.auto_state == 1:
        self.state1_cntr += 1
        if self.state1_cntr > 2:
          self.strategy_mode = ofdm_ti.PA_Ctrl.rate_adaptive
          self.constraint = sqrt(self.constr_range[self.cur_constr_ind])
          self.auto_state = 2
          self.store_ctrl_events = True
          self.start_measurement()
      elif self.auto_state == 2:
        if len(self.bervec) > 20000:
          self.end_measurement()
          self.store_ctrl_events = False
          self.auto_state = 0
          self.cur_constr_ind += 1
          if self.cur_constr_ind >= len(self.constr_range):
              self.cur_constr_ind = 0
              self.nrounds -=1
              print "Finish simulation round: ", self.options.nrounds - self.nrounds
              if self.nrounds ==0:
                  print "Simulation finished"
                  exit()


    rxperf = rxperf[len(rxperf)-1]
    current_ber = rxperf.ber
    snr_mean = rxperf.snr
    ctf = rxperf.ctf

#    print "Received performance measure estimate:"
#    print repr(rxperf)
#    print "======================================"
    if self.options.usrp2:
        cur_tx_power = (self.tx_amplitude*self.scale)**2
    else:
        cur_tx_power = self.tx_amplitude**2     # average power
    #cur_tx_constraint = self.constraint**2  # dito

    # Input:
    #  self.required_ber
    #  self.constraint
    #  self.current_ber
    #  self.ac_vector (if sounder connected)

    if self.is_reset_mode():
      print "Current mode is reset mode :)"
      self.pa_vector = [1.0]*self.subcarriers
      self.mod_map = [1]*self.subcarriers
      self.assignment_map = [1] * self.subcarriers
      
      #for i in range(100):
        #self.mod_map [i] = 0;
        #self.assignment_map [i] = 0;
 
      if self.options.usrp2:
        self.tx_amplitude = 0.2#self.scale*self.constraint
      else:
        self.tx_amplitude = self.constraint

      frame_length_samples = (self.options.data_blocks + 3)*self.block_length
      if self.options.coding:
          bits_per_mode = numpy.array([0.5,1.,1.5,2.,3.,4.,4.5,5.,6.])
          bits_per_frame = 0
          for b_n in self.mod_map:
              if b_n > 0:
                  bits_per_frame += bits_per_mode[b_n-1]*self.options.data_blocks
      else:
          bits_per_frame = sum(self.mod_map)*self.options.data_blocks
      frame_duration = frame_length_samples/self.bandwidth
      self.data_rate = bits_per_frame/frame_duration

      ###################################
      c_ber = max(current_ber, 1e-7)

      snr_mean_lin = 10**(snr_mean/10.0)
      print "Current SNR:", snr_mean
      print "Current BER:", c_ber
      snr_func_lin = 2.0*(erfcinv(2*c_ber)**2.0)
      snr_func = 10*log10(snr_func_lin)
      print "Func. SNR:", snr_func
      delta = self._delta = snr_mean_lin/snr_func_lin
      print "Current delta", delta
      self._agg_rate = 2


      #################################

      pass
    elif self.is_margin_adaptive_policy():
      print "Current mode is margin adaptive mode"
      cur_bit_constraint = ceil(self.constraint*self.block_length/self.bandwidth*(self.options.data_blocks + 3)/self.options.data_blocks)
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
    print "required BER", self.required_ber
    ber = max(self.required_ber,1e-7)

    snrf = (2)*(erfcinv(2*ber)**2.0)   #*3.2
    snr_corr = snrf# snrf*self._delta

    #gamma = (2.0/3.0)*(erfcinv(ber)**2.0)   #*3.2

    #gamma = snr_corr/(2**(self._agg_rate)-1)    #*3.2
    
    if(self.options.coding):                
        if self.options.ideal:
            # ideal
            if(ber<5e-4):
                gamma=numpy.array([0 , 1.5438 , 1.0203 , 2.6097 , 1.0747 , 2.1895 , 1.8000 , 2.8495 , 2.7565 , 3.8327])
            elif(ber<1e-3):
                gamma=numpy.array([0 , 1.3427 , 1.0051 , 1.9527 , 1.0621 , 2.0434 , 1.7049 , 2.3527 , 2.4229 , 2.9408])
            elif(ber<5e-3):
                gamma=numpy.array([0 , 1.1977 , 0.9845 , 1.7411 , 1.0454 , 1.8468 , 1.5733 , 2.0990 , 2.1302 , 2.6036])
            elif(ber<1e-2):
                gamma=numpy.array([0 , 1.5638 , 1.0221 , 2.7209 , 1.0762 , 2.2047 , 1.8102 , 2.8972 , 2.7896 , 3.9578])
            elif(ber<5e-2):
                gamma=numpy.array([0 , 0.9274 , 0.7591 , 1.2975 , 0.8190 , 1.3625 , 1.1739 , 1.4974 , 1.5993 , 1.7374])
            else:
                gamma=numpy.array([0 , 0.7508 , 0.6158 , 1.0464 , 0.6652 , 1.0895 , 0.9582 , 1.1568 , 1.2762 , 1.2394])
        elif self.options.rf:     
            # RF
            if(ber<5e-4):
                gamma=numpy.array([0 , 9.7493 , 7.1363 , 8.6450 , 4.3170 , 9.2212 , 9.1421 ,     100 ,     100 ,    100])
            elif(ber<1e-3):
                gamma=numpy.array([0 , 9.4662 , 6.5808 , 7.4302 , 4.0159 , 7.0582 , 6.3137 , 15.4365 ,     100 ,    100])
            elif(ber<1e-3):
                gamma=numpy.array([0 , 9.1027 , 5.8358 , 6.4078 , 3.6493 , 6.1440 , 5.5040 , 10.4642 , 20.1025 ,    100])
            elif(ber<5e-3):
                gamma=numpy.array([0 , 7.2523 , 3.8643 , 5.0281 , 2.6748 , 4.4787 , 4.3055 ,  5.1118 ,  6.4582 , 9.0607])
            else:
                gamma=numpy.array([0 , 6.2946 , 3.5373 , 4.4424 , 2.4074 , 3.9225 , 3.6520 ,  4.2943 ,  5.0410 , 7.5400])
        else:
            # non-ideal
            if(ber<5e-4):
                gamma=numpy.array([0 , 9.7384 , 5.1097 , 8.2398 , 4.3591 , 7.0798 , 5.8270 , 8.9890 , 8.7163 ,10.0933])
            elif(ber<1e-3):
                gamma=numpy.array([0 , 8.2596 , 4.6989 , 6.4926 , 3.7563 , 6.0941 , 5.2277 , 6.6700 , 6.9333 , 8.2423])
            elif(ber<5e-3):
                gamma=numpy.array([0 , 7.4008 , 4.1930 , 5.8691 , 3.2758 , 5.2829 , 4.5615 , 5.8111 , 6.1704 , 7.0552])
            elif(ber<1e-2):
                gamma=numpy.array([0 , 5.9136 , 3.3531 , 4.4833 , 2.5323 , 3.9716 , 3.4615 , 4.3119 , 4.6051 , 4.9963])
            elif(ber<5e-2):
                gamma=numpy.array([0 , 5.3589 , 3.0716 , 3.9696 , 2.2274 , 3.4659 , 3.0277 , 3.7479 , 4.0684 , 4.2955])
            else:
                gamma=numpy.array([0 , 6.4458 , 2.4096 , 2.9130 , 1.6558 , 2.5083 , 2.2143 , 2.6672 , 2.9499 , 2.8611])
#        if(ber<5e-4):
#            gamma=numpy.array([2.11274916977548 , 1.57912452224191 , 2.51405443306465 , 1.44595166360759 , 2.68091124576277 , 3.16560228173985 , 3.37746949170147 , 3.78151283299188 , 3.70999703823166])
#        elif(ber<1e-3):
#            gamma=numpy.array([1.60419409752167 , 1.21749022632635 , 1.87840751474564 , 1.20305029603270 , 1.93911641364187 , 1.88851036632089 , 2.25716610536513 , 2.56734177041076 , 2.48228391147837])
#        elif(ber<5e-3):
#            gamma=numpy.array([1.43384844917417 , 1.08019017579600 , 1.66430002130788 , 1.08636232319463 , 1.71821018223388 , 1.68650666586592 , 1.99045060413079 , 2.29215687946636 , 2.17592750939293])
#        elif(ber<1e-2):
#            gamma=numpy.array([1.10454652387901 , 0.860312776576655 , 1.38358675163081 , 0.915209379186896 , 1.43038216959072 , 1.37603238862224 , 1.59727097743186 , 1.86729290079063 , 1.70686835096279])
#        elif(ber<5e-2):
#            gamma=numpy.array([0.986838686908210 , 0.786650849752610 , 1.28576911358177 , 0.842624434260575 , 1.33304684638056 , 1.26422805477732 , 1.45606758788434 , 1.70067289226524 , 1.55303738869075])
#        else:
#            gamma=numpy.array([0.772408443646234 , 0.628935350461522 , 1.04605002965141 , 0.679025274980280 , 1.08674818536134 , 1.01128951353326 , 1.16382798159299 , 1.36099942169973 , 1.24562263191628])
    else:
        # no coding
        if self.options.rf:
            if(ber<5e-4):
                gamma = numpy.array([ 0 , 10.2816 , 11.3206 , 24.0437 , 14.8959 ,    1000 ,   1000 ,   1000 ,   1000 ])
            elif(ber<1e-3):
                gamma = numpy.array([ 0 ,  9.7878 ,  9.7958 , 17.3527 , 10.0541 , 17.6911 ,   1000 ,   1000 ,   1000 ])
            elif(ber<5e-3):
                gamma = numpy.array([ 0 ,  9.1347 ,  8.3290 , 14.7530 ,  8.3998 , 14.8062 ,   1000 ,   1000 ,   1000 ])
            elif(ber<1e-2):
                gamma = numpy.array([ 0 ,  7.0443 ,  5.4666 ,  8.3082 ,  5.0629 ,  6.2459 , 9.9221 ,   1000 ,   1000 ])
            elif(ber<5e-2):
                gamma = numpy.array([ 0 ,  6.2690 ,  4.3575 ,  6.4105 ,  3.8124 ,  4.6386 , 5.4114 , 7.2996 ,   1000 ])
            else:
                gamma = numpy.array([ 0 ,  4.3606 ,  2.3287 ,  2.6557 ,  1.6217 ,  1.7026 , 1.4989 , 1.6788 , 1.4688 ])
        else:        
            if(ber<5e-4):
                gamma = numpy.array([ 0 , 8.3676 , 8.9756 ,  14.9901 , 10.9871 , 10.8335 , 10.7062 , 8.8907 , 5.2206 ])
            elif(ber<1e-3):
                gamma = numpy.array([ 0 , 8.1981 , 8.1294 , 12.5150 , 8.5216 , 8.7778 , 8.5994 , 8.0738 , 5.1455 ])
            elif(ber<5e-3):
                gamma = numpy.array([ 0 , 7.9805 , 7.1031 , 10.7740 , 7.3094 , 7.4424 , 7.2455 , 7.0240 , 5.0470 ])
            elif(ber<1e-2):
                gamma = numpy.array([ 0 , 6.4316 , 4.9065 , 7.1997 , 4.6970 , 4.7356 , 4.4947 , 4.2972 , 4.1525 ])
            elif(ber<5e-2):
                gamma = numpy.array([ 0 , 5.5555 , 4.0276 , 5.7328 , 3.6660 , 3.6904 , 3.4265 , 3.2823 , 3.1488 ])
            else:
                gamma = numpy.array([ 0 , 4.0945 , 2.1450 , 2.5297 , 1.5831 , 1.5802 , 1.3290 , 1.2505 , 1.0937 ])
    print "required ber",ber
    print "snr gap (dB) for req. ber",10*log10(gamma)

    N = self.subcarriers

    (b,e) = levin_campello(self.mod_map, N, cur_tx_constraint,
                           snr_db, ctf, gamma, cur_tx_power,ber,self.options.coding)

    b = numarray.array(b)
    e = numarray.array(e)
    a = numarray.array(zeros(len(self.assignment_map)))

    if sum(b < 0) > 0:
      print "WARNING: bit loading < 0"
      b[b < 0] = 0

    a[b > 0] = 1
    
    txpow = sum(e)
    e = e / txpow * N  # normalize tx power

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

    frame_length_samples = (self.options.data_blocks +3)*self.block_length
    if self.options.coding:
        bits_per_mode = numpy.array([0.5,1.,1.5,2.,3.,4.,4.5,5.,6.])
        bits_per_frame = 0
        for b_n in b:
            if b_n > 0:
                bits_per_frame += bits_per_mode[b_n-1]*self.options.data_blocks
    else:
        bits_per_frame = sum(b)*self.options.data_blocks
    frame_duration = frame_length_samples/self.bandwidth
    self.data_rate = bits_per_frame/frame_duration
    print "Datarate",self.data_rate
    print "TX amplitude",self.tx_amplitude
    #print "TX amplitude",self.tx_amplitude/self.scale

    ####New adaptation -> Experimental ########################
    # Calculating the aggregate rate per used subcarrier
    agg_rate = 2 #self._agg_rate = sum(b)/sum(a) ??
    print "Aggregate rate:", agg_rate

    rxperf = self.get_rx_perf_meas()
    if len(rxperf) == 0:
      return

    rxperf = rxperf[len(rxperf)-1]
    current_ber = rxperf.ber
    snr_mean = rxperf.snr
    ctf = rxperf.ctf

    #Taking care of only used subcarriers
    str_corr = 1 #??sum(ctf*a)/sum(a) #Improve lin <-> square
    print"STR CORR:", str_corr

    ##
    c_ber = max(current_ber, 1e-7)
    snr_mean_lin = 10**(snr_mean/10.0)
    print "Current SNR:", snr_mean
    print "Current BER:", c_ber
    snr_func_lin = 2.0*(erfcinv(2*c_ber)**2.0)
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

    frame_length_samples = (self.options.data_blocks + 3)*self.block_length
    if self.options.coding:
        bits_per_mode = numpy.array([0.5,1.,1.5,2.,3.,4.,4.5,5.,6.])
        bits_per_frame = 0
        for b_n in b:
            if b_n > 0:
                bits_per_frame += bits_per_mode[b_n-1]*self.options.data_blocks
    else:
        bits_per_frame = sum(b)*self.options.data_blocks 
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
    str_corr = sum(ctf**2*a)/sum(a) #Improve lin <-> square
    print"STR CORR:", str_corr

    ##
    c_ber = max(current_ber, 1e-7)
    snr_mean_lin = 10**(snr_mean/10.0)
    print "Current SNR:", snr_mean
    print "Current BER:", c_ber
    snr_func_lin = 2.0*(erfcinv(c_ber)**2.0)
    snr_func = 10*log10(snr_func_lin)
    print "Func. SNR:", snr_func
    delta = self._delta = snr_mean_lin/snr_func_lin*(str_corr)
    print "Current delta", delta


    ###########################################################

  def start_measurement(self):
    self.bervec = list()
    self.snrvec = list()
    self.datarate_vec = list()
    self.txamp_vec = list()
    self.start_time = strftime("%a, %d %b %Y %H:%M:%S +0000", gmtime())

    self.filename_prefix = "./" + self.dirname + "/" +"sCONSTR_"+str(int(self.cur_constr_ind+1))+"_ITER_"+str(int(self.options.nrounds-self.nrounds+1))

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
    expert.add_option("", "--lb", type="eng_float", default=500,
                      help="Lower Bound for Tx Digital Amplitude [default=%default]");
    expert.add_option("", "--ub", type="eng_float", default=10000,
                      help="Upper Bound for Tx Digital Amplitude [default=%default]");
    expert.add_option("", "--points", type="int", default=25,
                      help="Number of points in given range [default=%default]");
    
    expert.add_option("-n", "--nrounds", type="eng_float", default=5,
                      help="Number of simulation rounds [default=%default]");
    expert.add_option("-b", "--berconstr", type="eng_float", default=0.0001,
                      help="BER constraint [default=%default]");
    expert.add_option("", "--usrp2",
                      action="store_true",
                      default=False,
                      help="USRP2")
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

def levin_campello(b,N,constraint,snr_db,ctf,gamma,txpow,ber=0,coding=0):
    
     # 1e-2 
  SNR_diff = [3.0, 3.2, 4.0, 3.5, 3.0, 3.0, 3.2, 3.4]
  
  #1e-4
  #SNR_diff = [1.5, 3.5, 4.3, 4.0, 4.1, 4.4, 4.6,  4.8] 
  SNR_diff = numarray.array(SNR_diff)
  
  SNR_diff_lin = 10**(SNR_diff/10)

  ctf = numarray.array(ctf)
  b = numarray.array(b)

  # gain to noise ratio
  snr = 10**(snr_db/10)
  avtxpow = txpow/N # average tx power
  norm_ctf_sqrd = abs(ctf)**2 / (sum(abs(ctf)**2)/N)
  g = snr/avtxpow * norm_ctf_sqrd
  
  # prepare
  beta = 1
  if coding==1:
      nbits = numpy.array([0.,1.,2.,2.,4.,4.,6.,6.,6.,8.]);
      infobits = numpy.array([0.,0.5,1.,1.5,2.,3.,4.,4.5,5.,6.]);
      codingrate = numpy.array([1.,0.5,0.5,0.75,0.5,0.75,0.5,2./3.,0.75,0.75]);
      
      gn = prepare_table(g,gamma,beta,SNR_diff_lin,coding,infobits,codingrate)
      min_ie = lambda b : min_c(gn,b/beta)
      max_ie = lambda b : max_c(gn,b/beta)
      energy = lambda m,n : gamma[m[n]] / g[n] / codingrate[m[n]] * (2**infobits[m[n]]-1)
  else:
      gn = prepare_table(g,gamma,beta,SNR_diff_lin)
      min_ie = lambda b : min_c(gn,b/beta)
      max_ie = lambda b : max_c(gn,b/beta)
      energy = lambda b,n : gamma[b[n]]/g[n]*(2.0**b[n]-1)

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
   # 1e-2 
  SNR_diff = [3.0, 3.2, 4.0, 3.5, 3.0, 3.0, 3.2, 3.4] 

  #1e-4
  #SNR_diff = [1.5, 3.5, 4.3, 4.0, 4.1, 4.4, 4.6,  4.8] 
  SNR_diff = numarray.array(SNR_diff)
  
  SNR_diff_lin = 10**(SNR_diff/10)
  
  ctf = numarray.array(ctf)
  b = numarray.array(b)

  # gain to noise ratio
  snr = 10**(snr_db/10)
  avtxpow = txpow/N # average tx power
  norm_ctf_sqrd = abs(ctf)**2 / (sum(abs(ctf)**2)/N)
  g = snr/avtxpow * norm_ctf_sqrd

  # prepare
  beta = 1
  gn = prepare_table(g,gamma,beta,SNR_diff_lin)
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
def prepare_table(g,gamma,beta,diff_vec,coding=0,infobits=0,codingrate=0):
  
  nsubc = len(g)
  if(coding==1):
      max_mode=9
      
      En = zeros((max_mode+1,nsubc))
      gn = zeros((max_mode+1,nsubc))
      
      for m in range(1,max_mode+1):
          En[m,:] = gamma[m] / codingrate[m] * (2**infobits[m]-1) / g
          if(m==1):
              gn[m,:] = En[m,:]
          else:
              gn[m,:] = En[m,:] - En[m-1,:]
  else:
      max_nbits = 8
      
      En = zeros((max_nbits/beta+1,nsubc))
      gn = zeros((max_nbits/beta+1,nsubc))
      
      for b in range(beta,max_nbits+beta,beta):
          En[b,:] = gamma[b] * (2**b-1) / g
          if(b==1):
              gn[b,:] = En[b,:]
          else:
              gn[b,:] = En[b,:] - En[b-1,:]
#      for b in range(beta,max_nbits+beta,beta):
#        if b ==1:
#            for n in range(nsubc):
#            #gn[b/beta][n] = gamma/g[n]*(2.0**b)*(1.0-2.0**(-beta))
#                 gn[b/beta][n] = gamma/g[n]*(2.0**(b)-1)*diff_vec[0]
#                #gn[b/beta][n] = gamma/g[n]/2*(2.0**(2*b)-1)*diff_vec[0]
#                #    elif b == 2:
#                #        for n in range(nsubc):
#                #        #gn[b/beta][n] = gamma/g[n]*(2.0**b)*(1.0-2.0**(-beta))
#                #        
#                #            gn[b/beta][n] = gamma/g[n]*(2.0**b-1)*diff_vec[1] - gamma/g[n]/2*(2.0**(2*(b-beta))-1)*diff_vec[0]
#        else:
#            for n in range(nsubc):
#            #gn[b/beta][n] = gamma/g[n]*(2.0**b)*(1.0-2.0**(-beta))
#            
#                gn[b/beta][n] = gamma/g[n]*(2.0**b-1)*diff_vec[b-1] - gamma/g[n]*(2.0**(b-beta)-1)*diff_vec[b-2]         
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
  while (m >= 0 and n >= 0) and (ie_m < ie_n) and (m != n): # inc_energy(b+beta,m) < inc_energy(b,n)
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
  print "Energy level S before ET",S
  
  print "ie_m: ",ie_m

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


  print "Energy level S after ET",S

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
