#!/usr/bin/env python

from numpy import concatenate,mean,var,arange,sqrt, log10, ceil, logspace
import numpy
import array

from resource_manager_base import resource_manager_base,start_resource_manager

from time import time, strftime, gmtime

import logging
from optparse import OptionParser
from gnuradio.eng_option import eng_option


class resource_manager (resource_manager_base):
  def __init__(self,orb,options):
    resource_manager_base.__init__(self,orb,options=options,loggerbase="mber.")

    self.localenv = options.le
    self.logger = logging.getLogger("mber.sm")
    self.logger.setLevel(logging.DEBUG)
    self.num_points = options.points

#    self.rm_logger.setLevel(logging.ERROR)

    # set initial parameters
    self.setup_time = 3000     # ms

    if self.localenv is not None:
      self.tx_max_log = log10(10000**2)
      self.tx_min_log = log10(500**2)
    else:
      if self.options.usrp2:
        self.scale = 1/32768.
      self.tx_max_log = log10(options.ub**2)
      self.tx_min_log = log10(options.lb**2)

    self.txpow_range = logspace(self.tx_max_log,self.tx_min_log,self.num_points)
    #self.txpow_range = range(10000**2,500**2,-(500**2))

    self.nbits = [1, 2, 3, 4, 5, 6, 7, 8]
    self.state = 0
    self.curmod = 0
    self.curtxpowind = 0

    if self.options.usrp2:
      self.scale = 1/32768.
      self.tx_amplitude = sqrt(self.txpow_range[0])*self.scale
    else:
      self.tx_amplitude = sqrt(self.txpow_range[0])

    self.buffer = []

    self.data_rate = 0

    self.current_rx_id = -1
    self.expected_rx_id = -1

    self.expire_cnt = 0

    self.start_time = ""
    self.options = options

  def work(self):

    self.do_update = False

    rxperf = self.get_rx_perf_meas()
    if len(rxperf) == 0:
      self.logger.warning("Did not receive any performance measure event")
      self.expire_cnt += 1
      if self.expire_cnt > 10:
        self.state = 0
        self.logger.warning( "RECOVER")
        self.expire_cnt = 0
      else:
        return

    self.logger.debug( "In state %d" % (self.state))

    if self.state == 0:

      # setup initial conditions for good link
      self.pa_vector = [float(1.0)]*self.subcarriers
      self.mod_map = [2]*self.subcarriers
      self.assignment_map = [1]*self.subcarriers
      if self.options.usrp2:
        self.tx_amplitude = 10000*self.scale
      else:
        self.tx_amplitude = 10000
      self.buffer = []
      self.do_update = True

      self.state = 1

    elif self.state == 1:

      # collect 1000 measurements
      self.buffer.extend( rxperf )

      self.logger.info( "Collecting, already have %d" %(len(self.buffer)))

      if len(self.buffer) >= 2000:

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

        self.logger.debug( "last rx id was %d" %(last_rxid))
        self.logger.debug( "RX ID stable for %d" %(rxid_stable))
        if rxid_stable > 500:
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

      self.logger.info( "Next power %f and mod %d" %(self.txpow_range[self.curtxpowind],self.nbits[self.curmod]))

      self.pa_vector = [float(1.0)]*self.subcarriers
      self.mod_map = [self.nbits[self.curmod]]*self.subcarriers
      self.assignment_map = [1]*self.subcarriers
      if self.options.usrp2:
        self.tx_amplitude = sqrt(self.txpow_range[self.curtxpowind])*self.scale
      else:
        self.tx_amplitude = sqrt(self.txpow_range[self.curtxpowind])

      self.buffer = []
      self.do_update = True

      self.expected_rx_id = ( self.current_rx_id + 1 ) % 1024

      self.logger.debug( "expected rx id: %d" % (self.expected_rx_id))

      self.state = 3
      self.start_time = strftime("%a, %d %b %Y %H:%M:%S +0000", gmtime())


    elif self.state == 3:

      skipped_items = 0
      for x in rxperf:
        if x.rx_id == self.expected_rx_id:
          self.buffer.append(x)
        else:
          skipped_items += 1

      self.logger.debug( "filtered buffer length: %d, skipped %d" % (len(self.buffer),skipped_items))

      if len(self.buffer) > 10000:
        self.state = 4

        filename_prefix = strftime("%Y%m%d%H%M%S",gmtime())

        bervec = []
        snrvec = []

        for x in self.buffer:
          bervec.append(x.ber)
          snrvec.append(x.snr)

        bervec = numpy.array(bervec)
        snrvec = numpy.array(snrvec)

        ber_mean = mean(bervec)
        snr_mean = mean(snrvec)
        ber_var = var(bervec)
        snr_var = var(snrvec)

        berout = array.array('f')
        snrout = array.array('f')
        berout.fromlist(bervec.astype(float).tolist())
        snrout.fromlist(snrvec.astype(float).tolist())

        f_ber = open( filename_prefix+"_ber.float", "wb" )
        f_snr = open( filename_prefix+"_snr.float", "wb" )
        f_nfo = open( filename_prefix+"_nfo.txt", "w" )


        berout.tofile(f_ber)
        snrout.tofile(f_snr)

        f_nfo.write( "Start time: %s\n" %(self.start_time) )
        f_nfo.write( "End time: %s\n" %(strftime("%a, %d %b %Y %H:%M:%S +0000", gmtime())))
        f_nfo.write( "Mod: %d\n" %(self.nbits[self.curmod]))
        f_nfo.write( "Power: %f\n" %(self.txpow_range[self.curtxpowind]))
        f_nfo.write( "expected rx id: %d\n" %(self.expected_rx_id))
        f_nfo.write( "Mean SNR %.8g   Var SNR %.8g\n" %(snr_mean,snr_var))
        f_nfo.write( "Mean BER %.8g   Var BER %.8g\n" %(ber_mean,ber_var))

        self.logger.info("Mean SNR %.8g   Var SNR %.8g" %(snr_mean,snr_var))
        self.logger.info("Mean BER %.8g   Var BER %.8g" %(ber_mean,ber_var))

        f_ber.close()
        f_snr.close()
        f_nfo.close()

        self.logger.info( "Wrote to files %s and %s" % (filename_prefix+"_ber.float",filename_prefix+"_snr.float"))

        self.buffer = []

    elif self.state == 4:

      self.curmod += 1
      if self.curmod >= len(self.nbits):
        self.curmod = 0
        self.curtxpowind += 1
        if self.curtxpowind >= len(self.txpow_range):
          self.curtxpowind = 0

      self.logger.info( "Next power %f and mod %d" %(self.txpow_range[self.curtxpowind],self.nbits[self.curmod]))

      self.expected_rx_id += 1
      self.state = 3
      self.start_time = strftime("%a, %d %b %Y %H:%M:%S +0000", gmtime())


      self.pa_vector = [float(1.0)]*self.subcarriers
      self.mod_map = [self.nbits[self.curmod]]*self.subcarriers
      self.assignment_map = [1]*self.subcarriers

      if self.options.usrp2:
        self.tx_amplitude = sqrt(self.txpow_range[self.curtxpowind])*self.scale
      else:
        self.tx_amplitude = sqrt(self.txpow_range[self.curtxpowind])

      self.buffer = []
      self.do_update = True

  def add_options(normal, expert):
    """
    Adds receiver-specific options to the Options Parser
    """

    normal.add_option("", "--le", action="store_true", default=False, help="Enable BER measurement in Local Environment")
    expert.add_option("", "--lb", type="eng_float", default=1000,
                      help="Lower Bound for Tx Digital Amplitude [default=%default]");
    expert.add_option("", "--ub", type="eng_float", default=10000,
                      help="Upper Bound for Tx Digital Amplitude [default=%default]");
    expert.add_option("", "--points", type="int", default=25,
                      help="Number of points in given range [default=%default]");
    expert.add_option("", "--usrp2",
                      action="store_true",
                      default=False,
                      help="USRP2")

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

  logfilename = "berlog_" + strftime("%Y%m%d%H%M%S",gmtime()) + ".log"


  fh = logging.FileHandler(logfilename)
  fh.setLevel(logging.DEBUG)

  ch = logging.StreamHandler()
  ch.setLevel(logging.DEBUG)

  formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
  fh.setFormatter(formatter)
#  ch.setFormatter(formatter)

  logger.addHandler(fh)
  logger.addHandler(ch)

  logger.info("Log filename is %s" %(logfilename))


  start_resource_manager(resource_manager, "PA",options)

if __name__ == '__main__':
  try:
    main()
  except KeyboardInterrupt:
    pass
