#!/usr/bin/env python

from numpy import concatenate,mean,var,arange,sqrt, log10, ceil, logspace
import numpy
import array

from resource_manager_base import resource_manager_base,start_resource_manager

from time import time, strftime, gmtime

import logging
from optparse import OptionParser
from gnuradio.eng_option import eng_option
import sys
import os

class resource_manager (resource_manager_base):
  def __init__(self,orb,options):
    resource_manager_base.__init__(self,orb,options=options,loggerbase="mber.")

    self.localenv = options.le
    self.snr = options.snr
    self.amplitude = options.rms_amplitude
    self.init_mod = options.init_mod
    self.logger = logging.getLogger("mber.sm")
    self.logger.setLevel(logging.DEBUG)
    self.num_points = options.points

#    self.rm_logger.setLevel(logging.ERROR)

    # set initial parameters
    self.setup_time = 1000     # ms

    if self.localenv is not None:
      self.tx_max_log = log10(10000**2)
      self.tx_min_log = log10(500**2)
    else:
      if self.options.usrp2:
        self.scale = 1/32768.
      self.tx_max_log = log10(options.ub**2)
      self.tx_min_log = log10(options.lb**2)

    #self.txpow_range = logspace(self.tx_max_log,self.tx_min_log,self.num_points)
    #self.txpow_range = range(10000**2,500**2,-(500**2))

    #self.nbits = [1, 2, 3, 4, 5, 6, 7, 8]
    self.nbits = [options.init_mod]
  
        
    available_modulations = ["BPSK", "QPSK", "8-PSK","16-QAM","32-QAM", "64-QAM","128-QAM", "256-QAM"]
    self.modulations = available_modulations[ self.init_mod-1]
    self.state = 0
    self.curmod = 0
    self.curtxpowind = 0

    if self.options.usrp2:
      self.scale = 1/32768.
      self.tx_amplitude = self.amplitude*self.scale
    else:
      self.tx_amplitude = self.amplitude

    self.buffer = []

    self.data_rate = 0

    self.current_rx_id = -1
    self.expected_rx_id = -1

    self.expire_cnt = 0

    self.start_time = ""
    self.options = options

  def work(self):

    self.do_update = False
    self.query_sounder()
    #print self.ac_vector

    self.ac_vector = [0.0+0.0j]*self.ac_vlen
    if self.ac_vlen>=8:
	#self.ac_vector[0] = 2*10**(-0.452)
	#self.ac_vector[3] = 10**(-0.651)
	#self.ac_vector[7] = 10**(-1.151)
        self.ac_vector[3] = 0.3267 
        self.ac_vector[4] = 0.8868
	self.ac_vector[5] = 0.3267
	#print self.ac_vector

    rxperf = self.get_rx_perf_meas()
    if len(rxperf) == 0:
      #self.logger.warning("Did not receive any performance measure event")
      self.expire_cnt += 1
      if self.expire_cnt > 10:
        self.state = 0
        #self.logger.warning( "RECOVER")
        self.expire_cnt = 0
      else:
        return

    ##self.logger.debug( "In state %d" % (self.state))

    if self.state == 0:

      # setup initial conditions for good link
      self.pa_vector = [float(1.0)]*self.subcarriers
      self.mod_map = [ self.init_mod]*self.subcarriers
      self.assignment_map = [1]*self.subcarriers
      if self.options.usrp2:
        self.tx_amplitude = self.amplitude*self.scale
      else:
        self.tx_amplitude = self.amplitude
      self.buffer = []
      self.do_update = True

      self.state = 1

    elif self.state == 1:

      # collect 1000 measurements
      self.buffer.extend( rxperf )

      ##self.logger.info( "Collecting, already have %d" %(len(self.buffer)))

      if len(self.buffer) >= 400:

        rxid = []
        for x in self.buffer:
          rxid.append( x.rx_id )

        rxid_stable = 0
        last_rxid = int(self.buffer[len(self.buffer)-1].rx_id)
        for i in arange(len(self.buffer)-1,-1,-1):
          if int(self.buffer[i].rx_id) == last_rxid:
            rxid_stable += 1
          else:
            break

        #self.logger.debug( "last rx id was %d" %(last_rxid))
        #self.logger.debug( "RX ID stable for %d" %(rxid_stable))
        if rxid_stable > 40:
          self.current_rx_id = last_rxid
          self.state = 2

        else:
          self.state = 0
          for x in self.buffer:
            print x.rx_id," ",
          print ""

    elif self.state == 2:

      self.curmod = 0
      self.curtxpowind = 0

      self.logger.info( "Next mod %d" %(self.nbits[self.curmod]))
      self.logger.info( "Next modulation " + self.modulations)

      self.pa_vector = [float(1.0)]*self.subcarriers
      self.mod_map = [self.nbits[self.curmod]]*self.subcarriers
      self.assignment_map = [1]*self.subcarriers
      if self.options.usrp2:
        self.tx_amplitude = self.amplitude*self.scale
      else:
        self.tx_amplitude = self.amplitude

      self.buffer = []
      self.do_update = True

      self.expected_rx_id = ( self.current_rx_id + 1 ) % 1024

      #self.logger.debug( "expected rx id: %d" % (self.expected_rx_id))

      self.state = 3
      self.start_time = strftime("%a, %d %b %Y %H:%M:%S +0000", gmtime())


    elif self.state == 3:

      skipped_items = 0
      for x in rxperf:
        if x.rx_id == self.expected_rx_id:
          self.buffer.append(x)
        else:
          skipped_items += 1

      ##self.logger.debug( "filtered buffer length: %d, skipped %d" % (len(self.buffer),skipped_items))

      if len(self.buffer) > 500:
        self.state = 4

        #filename_prefix = strftime("%Y%m%d%H%M%S",gmtime())
        omnilogdir = os.path.expanduser('~/omnilog/')
        filename_prefix = str(self.modulations)

        bervec = []
        snrvec = []
        ctfmat = []

        for x in self.buffer:
          bervec.append(x.ber)
          snrvec.append(x.snr)
          ctfmat.append(x.ctf)

        bervec = numpy.array(bervec)
        snrvec = numpy.array(snrvec)
        ctfmat = numpy.array(ctfmat)

        ber_mean = mean(bervec)
        snr_mean = mean(snrvec)
        ctf_mean = mean(ctfmat,axis=0)

        ber_var = var(bervec)
        snr_var = var(snrvec)
        ctf_var = var(ctfmat,axis=0)

        berout = array.array('f')
        snrout = array.array('f')
        berout.fromlist(bervec.astype(float).tolist())
        snrout.fromlist(snrvec.astype(float).tolist())

        #f_ber = open( filename_prefix+"_ber.float", "wb" )
        #f_snr = open( filename_prefix+"_snr.float", "wb" )
        if (self.curmod == 0):
	    filee = omnilogdir+filename_prefix+"_freq_select_1e-2.txt"
            self.f_nfo = open( filee, "w" )
        
        #ind_max_vec = numpy.zeros(200)
        #max_vec = numpy.zeros(200)
        #ctf_mean_pom = ctf_mean
        #for i in range (100):
         #  max_v = ctf_mean.max()
	 #  arg_max_v = ctf_mean.argmax()
         #  ind_max_vec[arg_max_v] = int(1)
         #  ctf_mean_pom[arg_max_v] = 0
         #  max_vec[arg_max_v] = max_v


        #berout.tofile(f_ber)
        #snrout.tofile(f_snr)

        self.f_nfo.write( "Start time: %s\n" %(self.start_time) )
        self.f_nfo.write( "End time: %s\n" %(strftime("%a, %d %b %Y %H:%M:%S +0000", gmtime())))
        #f_nfo.write( "Mod: %d\n" %(self.nbits[self.curmod]))
        self.f_nfo.write( "Mod: " + str(self.modulations) + "\n")
        #f_nfo.write( "Power: %f\n" %(self.txpow_range[self.curtxpowind]))
        #f_nfo.write( "expected rx id: %d\n" %(self.expected_rx_id))
        self.f_nfo.write( "Mean SNR %.8g   Var SNR %.8g\n" %(snr_mean,snr_var))
        self.f_nfo.write( "Mean BER %.8g   Var BER %.8g\n\n" %(ber_mean,ber_var))

	#self.f_nfo.write( "Mean CTF: ")
        #print>> self.f_nfo,ctf_mean.tolist()
        #self.f_nfo.write( "\n")
        #self.f_nfo.write( "Strong CTF: ")
        #print>> self.f_nfo,max_vec.tolist()
        #self.f_nfo.write( "\n")
        #self.f_nfo.write( "Subcarriers with strong CTF: ")
        #print>> self.f_nfo,ind_max_vec.tolist()
        #self.f_nfo.write( "\n")


        self.logger.info("Mean SNR %.8g   Var SNR %.8g" %(snr_mean,snr_var))
        self.logger.info("Mean BER %.8g   Var BER %.8g" %(ber_mean,ber_var))

        #self.logger.info("Mean CTF "+ctf_mean.tostring())
        #self.logger.info( "Strong CTF "+max_vec.tostring())
        #self.logger.info( "Subcarriers with strong CTF "+ind_max_vec.tostring())

        #self.logger.info( "Mean CTF: "+ctf_mean.tostring()+"\n")
        #self.logger.info( "Strong CTF: "+max_vec.tostring()+"\n")
        #self.logger.info( "Subcarriers with strong CTF: "+ind_max_vec.tostring()+"\n")

        #f_ber.close()
        #f_snr.close()
        if (self.curmod == len(self.nbits)-1):
            self.f_nfo.close()

        #self.logger.info( "Wrote to files %s and %s" % (filename_prefix+"_ber.float",filename_prefix+"_snr.float"))

        self.buffer = []

    elif self.state == 4:

      self.curmod += 1
      if self.curmod >= len(self.nbits):
        #self.curmod = 0
        #sys.exit("Simulation finished")
        print "Simulation for SNR = %f dB finished" %(self.snr)
        print "Press <STRG> C to stop the resource manager"
        quit()
        #self.curtxpowind += 1
        #if self.curtxpowind >= len(self.txpow_range):
          #self.curtxpowind = 0

      ##self.logger.info( "Next mod %d" %(self.nbits[self.curmod]))
      print "Next modulation ", self.modulations

      self.expected_rx_id += 1
      self.state = 3
      self.start_time = strftime("%a, %d %b %Y %H:%M:%S +0000", gmtime())


      self.pa_vector = [float(1.0)]*self.subcarriers
      self.mod_map = [self.nbits[self.curmod]]*self.subcarriers
      self.assignment_map = [1]*self.subcarriers

      if self.options.usrp2:
        self.tx_amplitude = self.amplitude*self.scale
      else:
        self.tx_amplitude = self.amplitude

      self.buffer = []
      self.do_update = True

  def add_options(normal, expert):
    """
    Adds receiver-specific options to the Options Parser
    """

    normal.add_option("", "--le", action="store_true", default=False, help="Enable BER measurement in Local Environment")
    normal.add_option("-a", "--rms-amplitude",
                      type="eng_float", default=8000, metavar="AMPL",
                      help="set transmitter digital rms amplitude: 0"+
                           " <= AMPL < 32768 [default=%default]")
    expert.add_option("", "--lb", type="eng_float", default=1000,
                      help="Lower Bound for Tx Digital Amplitude [default=%default]");
    expert.add_option("", "--ub", type="eng_float", default=10000,
                      help="Upper Bound for Tx Digital Amplitude [default=%default]");
    expert.add_option("", "--snr", type="eng_float", default=10,
                      help="SNR value in dB [default=%default]");
    expert.add_option("", "--points", type="int", default=25,
                      help="Number of points in given range [default=%default]");
    expert.add_option("", "--usrp2",
                      action="store_true",
                      default=False,
                      help="USRP2")
    expert.add_option("","--init-mod",type="intx",
                      default=2,help="Set init modulation")

    resource_manager_base.add_options(normal,expert)
  add_options = staticmethod(add_options)



################################################################################

def main():
  parser = OptionParser(option_class=eng_option, conflict_handler="resolve")
  normal_grp = parser.add_option_group("Normal")
  expert_grp = parser.add_option_group("Expert")
  resource_manager.add_options(normal_grp,expert_grp)
  (options, args) = parser.parse_args()

  logger = logging.getLogger("mber")
  logger.setLevel(logging.DEBUG)

  #logfilename = "berlog_" + strftime("%Y%m%d%H%M%S",gmtime()) + ".log"


  #fh = logging.FileHandler(logfilename)
  #fh.setLevel(logging.DEBUG)

  ch = logging.StreamHandler()
  ch.setLevel(logging.DEBUG)

  formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
  #fh.setFormatter(formatter)
  ch.setFormatter(formatter)

  #logger.addHandler(fh)
  logger.addHandler(ch)

  #logger.info("Log filename is %s" %(logfilename))


  start_resource_manager(resource_manager, "PA",options)

if __name__ == '__main__':
  try:
    main()
  except KeyboardInterrupt:
    pass
