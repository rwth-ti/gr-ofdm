#!/usr/bin/env python

# Framework for resource managers. Derive specific implementation from this
# base class

from omniORB import CORBA, PortableServer
from corba_stubs import ofdm_ti,ofdm_ti__POA
import CosNaming
import CosEventComm__POA, CosEventComm
import CosEventChannelAdmin
import os,sys,time,threading
from omniORB.any import to_any

from gnuradio import gr

import random,cmath
from array import array as array_f

from random import seed,randint

from corba_servants import *

from threading import Timer
from numpy import concatenate
import numpy

import scipy,math
from scipy import sqrt,log, exp,randn, sum, absolute, multiply, array2string, reshape, ceil, array, zeros,ones, log, floor
from pylab import plot, stem, subplot, show, ylim
from numpy.fft import fftshift

import socket

std_event_channel = "corbaname:rir:/NameService#"

import logging
from time import clock,strftime,gmtime


class ctrl_event:
  def __init__(self,ctrl=None,txamp=0.0,ber=0.0,constraint=0.0,datarate=0.0):
    self.ctrl = ctrl
    self.timestamp = clock()
    self.tx_amplitude = txamp
    self.ber = ber
    self.constraint = constraint
    self.datarate = datarate


class resource_manager_base (ofdm_ti__POA.PA_Ctrl):
  def __init__(self,orb,loggerbase="",options=None):
    self.orb = orb
    self.options = options
    
    self.rm_logger = logging.getLogger(loggerbase+"rmbase")
    self.rm_logger.setLevel(logging.DEBUG)

    self.connect_push_supplier()
    self.connect_push_consumer()

    # set initial parameters
    self.strategy_mode = ofdm_ti.PA_Ctrl.reset
    self.required_ber = 0.001
    self.constraint = 1000.0 # rate or power
    self.setup_time = 2000 # ms
    self.data_rate= 365079
    self.tx_amplitude = 1000
    if options.dyn_freq:
        self.tx_freq = 2450000000
        self.rx_freq =  self.tx_freq
    self.frame_length = options.data_blocks + 1 + 2
    self.data_blocks = options.data_blocks
    self.id_blocks = 1
    self.tx_id = 1
    self.max_tx_id = 1024
    
    
    self.store_ctrl_events = False
    self.ctrl_events = dict()


    # shadow copies
    self._strategy_mode = self.strategy_mode
    self._required_ber = self.required_ber
    self._constraint = self.constraint

    # get object references
    self.info_tx = resolve(orb,"info_tx",ofdm_ti.info_tx)
    self.ci_impulse = resolve(orb,"sounder_cir_c", ofdm_ti.data_buffer)

    self.tx_power_ref = resolve(orb,"txpower", ofdm_ti.push_vector_f)
    self.estim_power_ref = resolve(orb,"estim_power", ofdm_ti.push_vector_f)
    if options.dyn_freq:
      self.tx_freq_ref = resolve(orb,"txfreq", ofdm_ti.push_vector_f)
      self.rx_freq_ref = resolve(orb,"rxfreq", ofdm_ti.push_vector_f)
    self.tx_ac = resolve(orb,"channelcheat", ofdm_ti.push_vector_c)

    # current datarate corba servant
    def dummy():
      pass
    self.datarate_servant = corba_ndata_buffer_servant("cur_datarate",
                                                       self._get_data_rate,
                                                       dummy)
    #self.UDP_client()

    if self.info_tx is None:
      raise SystemExit, "Need TX information"

    # latch tx information
    self.subcarriers = self.info_tx._get_subcarriers() #data subcarriers w/o pilot subcarriers
    self.fft_length = self.info_tx._get_fft_window()
    self.cp_length = self.info_tx._get_cp_length()
    self.block_length = self.fft_length+self.cp_length
    self.data_frame_length = self.info_tx._get_burst_length() # damn
    self.bandwidth = self.info_tx._get_bandwidth()

    # modify these variables to change the power allocation scheme or to
    # influence the artificial channel
    self.pa_vector = [float(1.0)]*self.subcarriers
    try:
      self.ac_vlen = self.tx_ac.vlen()
      self.ac_vector = [0.0+0.0j]*self.ac_vlen
      self.ac_vector[0] = 1.0+0.0j
    except:
      self.ac_vector=[1]
      self.ac_vlen = 1

    self.mod_map = [2]*self.subcarriers
    self.assignment_map = [1]*self.subcarriers

    self.rm_logger.info("Subcarriers: %d"%(self.subcarriers))


    self.pa_msgq = gr.msg_queue(2)
    self.pa_disp_servant = corba_data_buffer_servant("padisp",self.subcarriers,
                                                     self.pa_msgq)

    self.ra_msgq = gr.msg_queue(2)
    self.ra_disp_servant = corba_data_buffer_servant("radisp",self.subcarriers,
                                                     self.ra_msgq)

    # tell transmitter initial settings and wait for it to stabilize
    self.propagate_changes()
    time.sleep(1.0) # seconds

  def UDP_client (self):
    self.clisock = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
    self.serverip = socket.gethostbyname('tabur')

    self.rm_logger.info( "Tabur IP: %s" %(str( self.serverip)))

    vv = self.data_rate
    self.rm_logger.debug( "Data rate: %d"%( vv))

    try:
      self.clisock.connect ((self.serverip,5000))
      self.clisock.send(str(vv)+"\n")
      #print self.clisock.recv(100)
      self.clisock.close()
    except:
      pass

  def connect_push_supplier(self):
    # get event channel
    obj = self.orb.string_to_object(std_event_channel+"GNUradio_EventChannel")
    self.channel = obj._narrow(CosEventChannelAdmin.EventChannel)
    assert(self.channel is not None)

    self.supplier=Supplier_i()
    sptr=self.supplier._this() # SIDE EFFECT: Activates object in POA

    #
    # Get Supplier Admin interface - retrying on Comms Failure.
    while(1):
      try:
          self.supplier_admin=self.channel.for_suppliers()
          if self.supplier_admin is None:
            sys.stderr.write("Event Channel returned nil Supplier Admin!\n")
            sys.exit(1)
          break
      except CORBA.COMM_FAILURE, ex:
        sys.stderr.write("Caught COMM_FAILURE Exception. "+ \
          "obtaining Supplier Admin! Retrying...\n")
        time.sleep(1)
    self.rm_logger.debug( "Obtained SupplierAdmin.")

    #
    # Get proxy consumer - retrying on Comms Failure.
    while (1):
      try:
        self.proxy_consumer=self.supplier_admin.obtain_push_consumer()
        if self.proxy_consumer is None:
          sys.stderr.write("Supplier Admin returned nil proxy_consumer!\n")
          sys.exit(1)
        break
      except CORBA.COMM_FAILURE, ex:
        sys.stderr.write("Caught COMM_FAILURE Exception "+ \
          "obtaining Proxy Push Consumer! Retrying...\n")
        time.sleep(1)
    self.rm_logger.debug( "Obtained ProxyPushConsumer.")

    #
    # Connect Push Supplier - retrying on Comms Failure.
    while (1):
      try:
          self.proxy_consumer.connect_push_supplier(sptr)
          break
      except CORBA.BAD_PARAM, ex:
        sys.stderr.write( \
          'Caught BAD_PARAM Exception connecting Push Supplier!')
        sys.exit(1)
      except CosEventChannelAdmin.AlreadyConnected, ex:
        sys.stderr.write('Proxy Push Consumer already connected!')
        sys.exit(1)
      except CORBA.COMM_FAILURE, ex:
        sys.stderr.write("Caught COMM_FAILURE Exception " +\
          "connecting Push Supplier! Retrying...")
        time.sleep(1)
    self.rm_logger.debug( "Connected Push Supplier.")

  def connect_push_consumer(self):
    obj = self.orb.string_to_object(std_event_channel+"himalaya")
    channel = obj._narrow(CosEventChannelAdmin.EventChannel)
    assert(channel is not None)

    #
    # Get Consumer Admin interface - retrying on Comms Failure.
    while(1):
      try:
          consumer_admin = channel.for_consumers ()
          if consumer_admin is None:
            sys.stderr.write("Event Channel returned nil Consumer Admin!\n")
            sys.exit(1)
          break
      except CORBA.COMM_FAILURE, ex:
        sys.stderr.write("Caught COMM_FAILURE Exception. "+ \
          "obtaining Consumer Admin! Retrying...\n")
        time.sleep(1)
    self.rm_logger.debug( "Obtained ConsumerAdmin.")

    #
    # Make a Push Consumer.
    self.pushconsumer = consumer = Consumer_i()

    #
    # Get proxy supplier - retrying on Comms Failure.
    while (1):
      try:
          proxy_supplier = consumer_admin.obtain_push_supplier ()
          if proxy_supplier is None:
            sys.stderr.write("Consumer Admin return nil proxy_supplier!\n")
            sys.exit(1)
          break
      except CORBA.COMM_FAILURE, ex:
        sys.stderr.write("Caught COMM_FAILURE Exception. "+ \
          "obtaining Proxy Push Supplier! Retrying...\n")
        time.sleep(1)
    self.rm_logger.debug( "Obtained ProxyPushSupplier.")

    #
    # Connect Push Consumer - retrying on Comms Failure.
    while (1):
      try:
          proxy_supplier.connect_push_consumer(consumer._this())
          break
      except CORBA.BAD_PARAM, ex:
        sys.stderr.write( \
          'Caught BAD_PARAM Exception connecting Push Consumer!\n')
        sys.exit(1)
      except CosEventChannelAdmin.AlreadyConnected, ex:
        sys.stderr.write('Proxy Push Supplier already connected!\n')
        sys.exit(1)
      except CORBA.COMM_FAILURE, ex:
        sys.stderr.write("Caught COMM_FAILURE Exception " +\
          "connecting Push Consumer! Retrying...\n")
        time.sleep(1)
    self.rm_logger.debug( "Connected Push Consumer.")

  def push_data(self):
    pa_vector = list(map(lambda x : float(x),self.pa_vector))
    assignment_map = list(map(lambda  x: int(x),self.assignment_map))
    mod_map = array_f('B',self.mod_map).tostring()
    
    bits_per_mode = numpy.array([0.5,1.,1.5,2.,3.,4.,4.5,5.,6.])
    bit_map = numpy.zeros(len(self.mod_map))
    for x in range(len(self.mod_map)):
        if self.mod_map[x] > 0:
            if self.options.coding:
                bit_map[x] = bits_per_mode[self.mod_map[x]-1]
            else:
                bit_map[x] = float(self.mod_map[x])
    bit_map = bit_map.tolist()
    tx_id = self.tx_id
    self.tx_id = (self.tx_id + 1) % self.max_tx_id

    for x in range(len(self.mod_map)):
      if self.mod_map[x] == 0:
        assert(assignment_map[x] == 0)
      else:
        assert(assignment_map[x] > 0)
      if (self.options.coding and self.mod_map[x] not in (0,1,2,3,4,5,6,7,8,9)) or (not self.options.coding and self.mod_map[x] not in (0,1,2,3,4,5,6,7,8)):
        raise SystemError,"Modulation scheme not supported: %d" % (self.mod_map[x])

    if sum(pa_vector) > self.subcarriers+10:
      self.rm_logger.error( "sum(pa_vector) = %d too big" %(sum(pa_vector)))
      pa_vector = numpy.array( pa_vector )
      pa_vector = [0]*len(mod_map)
      pa_vector[numpy.array(mod_map)>0]=1.0
      self.rm_logger.error( "ERROR!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")
      
#    self.rm_logger.debug( "PUSHING PA VECTOR: %s"%(str(pa_vector)))
    if self.options.coding:
        data = ofdm_ti.tx_config_data(
          tx_id = tx_id,
          power_map = pa_vector,
          mod_map = mod_map,
          bit_map = bit_map,
          assignment_map = assignment_map,
          data_blocks = self.data_blocks,
          id_blocks = self.id_blocks
          )
    else:
        data = ofdm_ti.tx_config_data(
          tx_id = tx_id,
          power_map = pa_vector,
          mod_map = mod_map,
          bit_map = bit_map,
          assignment_map = assignment_map,
          data_blocks = self.data_blocks,
          id_blocks = self.id_blocks
          )
    data_any = to_any(data)
    
    if self.store_ctrl_events:
      self.ctrl_events[tx_id] = ctrl_event(data,self.tx_amplitude,
                                           self.required_ber,self.constraint,
                                           self.data_rate)
    

    while (1):
      try:
        self.rm_logger.debug(  "Push Supplier: push() called. ")
        self.proxy_consumer.push(data_any)
        break
      except CosEventComm.Disconnected, ex:
        sys.stderr.write("Failed. Caught Disconnected Exception!")
        sys.exit(1)
      except CORBA.COMM_FAILURE, ex:
        sys.stderr.write("Failed. Caught COMM_FAILURE Exception! Retrying ...")
        self.rm_logger.warning("Failed. Caught COMM_FAILURE Exception! Retrying ...")
        time.sleep(1)
      except:
        sys.stderr.write("Unknown exception, terminating")
        sys.exit(1)

  def start(self):
    self.timer = Timer(self.setup_time/1000, self.periodic_work)
    self.timer.start()

  def periodic_work(self):
    self.rm_logger.info( "Begin of Round -----------------------------------------------------")
    

    self.do_update = True
    self.work()
    
    if self.do_update:
      self.propagate_changes()
    else:
      self.rm_logger.debug("Not performing update")
    self.rm_logger.info( "End of Round -------------------------------------------------------")

    self.start()

  def propagate_changes(self):
    if not(0 < self.tx_amplitude < 32768):
      self.rm_logger.warning( "TX Power %d" %( self.tx_amplitude))
      self.rm_logger.warning( "WARNING!!!  Limiting Power ---------------------------------------")
      self.tx_amplitude = 32768

    assert(len(self.pa_vector) == self.subcarriers)
    assert(len(self.ac_vector) == self.ac_vlen)
    assert(len(self.mod_map) == self.subcarriers)
    assert(len(self.assignment_map) == self.subcarriers)


    # amplifier control
    try:
      self.tx_power_ref.push([float(self.tx_amplitude)])
      self.rm_logger.info( "Pushed new tx power")
    except:
      self.rm_logger.error( "Failed to push new tx power")
      self.tx_power_ref = resolve(self.orb,"txpower", ofdm_ti.push_vector_f)
      
    try:
      self.estim_power_ref.push([float(self.tx_amplitude)])
      print "self.tx_amplitude for estimation", self.tx_amplitude
      self.rm_logger.info( "Pushed new estim power")
    except:
      self.rm_logger.error( "Failed to push new estim power")
      self.estim_power_ref = resolve(self.orb,"estim_power", ofdm_ti.push_vector_f)
    
    try:
      self.tx_freq_ref.push([float(self.tx_freq)])
      self.rm_logger.info( "Pushed new tx frequency")
    except:
      self.rm_logger.error( "Failed to push new tx frequency")
      self.tx_freq_ref = resolve(self.orb,"txfreq", ofdm_ti.push_vector_f)
      
    try:
      self.rx_freq_ref.push([float(self.rx_freq)])
      self.rm_logger.info( "Pushed new rx frequency")
    except:
      self.rm_logger.error( "Failed to push new trx frequency")
      self.rx_freq_ref = resolve(self.orb,"rxfreq", ofdm_ti.push_vector_f)

    acv = self.ac_vector
    acv = acv/sqrt(sum(absolute(acv)**2))
    # artificial channel
    ac_vector = []
    for x in acv:
      ac_vector.append(float(numpy.real(x)))
      ac_vector.append(float(numpy.imag(x)))
      
    try:
      self.tx_ac.push(list(ac_vector))
    except:
      self.rm_logger.error("FAILED push artificial channel")
      self.tx_ac = resolve(self.orb,"channelcheat", ofdm_ti.push_vector_c)

    self.rm_logger.debug( "Pushed artificial channel update")

    # display pa scheme
    pa_vector_s = array_f('f',array(self.pa_vector)**(1./2)).tostring()
    msg = gr.message_from_string(pa_vector_s)
    if not self.pa_msgq.full_p():
      self.pa_msgq.insert_tail(msg)

    self.rm_logger.debug("Pushed pa scheme to GUI")

    ra_vector_s = array_f('f',array(self.mod_map)).tostring()
    msg_ra = gr.message_from_string(ra_vector_s)
    if not self.ra_msgq.full_p():
      self.ra_msgq.insert_tail(msg_ra)

    #self.UDP_client()
    # event channel communication
    self.push_data()

    self.rm_logger.info( "Pushed data")


  ## CORBA interface to control the PA
  ##############################################################################
  def _set_required_ber(self,val):
    self._required_ber = val

  def _get_required_ber(self):
    return self.required_ber

  def _set_constraint(self,val):
    # FIXME check if in acceptable range
    self._constraint = val

  def _get_constraint(self):
    return self.constraint

  def _set_channel_refresh_interval(self,val):
    self._channel_refresh_interval = val

  def _get_channel_refresh_interval(self):
    return self.channel_refresh_interval

  def _get_data_rate(self):
    return self.data_rate

  def change_strategy(self,mode):
    # FIXME check if contraints etc. fit to the new mode
    self._strategy_mode = mode

  def update(self):
    self.strategy_mode = self._strategy_mode
    self.required_ber = self._required_ber
    self.constraint = self._constraint
  ##############################################################################

  def query_sounder(self):
    try:
      #CTF from sounder
      ci_imp = self.ci_impulse.get_data()
      ci_vector_len = self.ac_vlen
      ci_imp=ci_imp[len(ci_imp)-2*ci_vector_len:len(ci_imp)]
      ci_imp=[ci_imp[2*i]+1j*ci_imp[2*i+1] for i in range(ci_vector_len)]
      ci_imp=array(ci_imp)
    except:
      #Stupid CTF#####################################

      ci_imp = concatenate([[1],[0]*(self.ac_vlen-1)])

      self.ci_impulse = resolve(self.orb,"sounder_cir_c", ofdm_ti.data_buffer)

    self.ac_vector = ci_imp

  def get_rx_perf_meas(self):
    return self.pushconsumer.get_received(True)

  def is_reset_mode(self):
    return self.strategy_mode==ofdm_ti.PA_Ctrl.reset

  def is_margin_adaptive_policy(self):
    return self.strategy_mode==ofdm_ti.PA_Ctrl.margin_adaptive

  def is_rate_adaptive_policy(self):
    return self.strategy_mode==ofdm_ti.PA_Ctrl.rate_adaptive
  
      
  def add_options(normal, expert):
    """
    Adds receiver-specific options to the Options Parser
    """
    expert.add_option("","--data-blocks",type="intx",
                      default=9,help="Set number of data blocks per OFDM frame")
    normal.add_option("", "--dyn-freq", action="store_true", default=False,
                      help="enable troughput measure, usrp disabled");
    normal.add_option("", "--coding", action="store_true", default=False,
                      help="Enable channel coding");
    normal.add_option("", "--ideal", action="store_true", default=False,
                      help="Ideal conditions (relevant for coding)");
    normal.add_option("", "--rf", action="store_true", default=False,
                      help="RF conditions (relevant for coding)");
  add_options = staticmethod(add_options)

################################################################################

class Supplier_i(CosEventComm__POA.PushSupplier):
  def disconnect_push_supplier (self):
      print "Push Supplier: disconnected."

################################################################################

class Consumer_i(CosEventComm__POA.PushConsumer):
  def __init__(self):
    self._received = []

  def get_received(self,clear=False):
    t = self._received
    if clear:
      self.clear_received()
    return t

  def clear_received(self):
    self._received = []

  def push(self,data_any):
    v = data_any.value(CORBA.TypeCode(CORBA.id(ofdm_ti.rx_performance_measure)))
    if v is not None:
      self._received.append(v)

  def disconnect_push_consumer(self):
    print "Push Consumer: disconnected."
#end class Consumer_i

################################################################################




def resolve(orb,uid,c):
  try:
    obj = orb.string_to_object("corbaname:rir:/NameService#ofdm_ti."+str(uid))
    obj_ref = obj._narrow(c)
  except:
    print "Couldn't find object reference to "+str(uid)
    obj_ref=None
  return obj_ref

################################################################################

def start_resource_manager(rmanager,unique_id,options=None):
  orb = CORBA.ORB_init(sys.argv,CORBA.ORB_ID)
  poa = orb.resolve_initial_references("RootPOA")

  poaManager = poa._get_the_POAManager()
  poaManager.activate()

  rm_i = rmanager(orb,options)
  rm_o = rm_i._this()
  unique_id = str(unique_id)

  try:
    obj = orb.resolve_initial_references("NameService")
    rootContext = obj._narrow(CosNaming.NamingContext)
  except:
    raise SystemExit, "Failed to get NamingContext"

  corba_name = [CosNaming.NameComponent("ofdm_ti",unique_id)]
  try:
    rootContext.bind(corba_name,rm_o)
  except: # CosNaming.NamingContext.AlreadyBound, ex:
    rootContext.rebind(corba_name,rm_o)

  seed()
  rm_i.start()
  try:
    orb.run()
  except:
    rm_i.timer.cancel()

def main():
  start_resource_manager(PA, "PA")

if __name__ == '__main__':
  try:
    main()
  except KeyboardInterrupt:
    pass
