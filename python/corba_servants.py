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

from omniORB import CORBA, PortableServer
from corba_stubs import ofdm_ti, ofdm_ti__POA
import CosNaming

import sys,array

from gnuradio import gr
from gnuradio import eng_notation

from numpy import concatenate

"""
CORBA servant for GR message_queues
"""
class data_buffer_i(ofdm_ti__POA.data_buffer):
  def __init__(self,vector_length,msgq):
    self.vec_len = vector_length
    self.msgq = msgq

  def get_data(self):
    data = []
    try:
      while (not self.msgq.empty_p()):
        x = self.msgq.delete_head().to_string()
        vec = array.array('f')
        vec.fromstring(x)
        data.append(vec)
    except:
      pass

    if len(data) == 0:
      return []
    else:
      data = list(concatenate(data))
      return data

  def flush(self):
    self.msgq.flush()

  def vlen(self):
    return self.vec_len

class corba_data_buffer_servant:
  def __init__(self,unique_id,vector_length,msgq):
    self.uid = unique_id

    orb = CORBA.ORB_init(sys.argv,CORBA.ORB_ID)
    poa = orb.resolve_initial_references("RootPOA")

    poaManager = poa._get_the_POAManager()
    poaManager.activate()

    self.corba_servant_i = data_buffer_i(vector_length,msgq)
    self.corba_servant_o = self.corba_servant_i._this()

    try:
      obj = orb.resolve_initial_references("NameService")
      self.rootContext = obj._narrow(CosNaming.NamingContext)
    except Exception, ex:
      print "CORBA Servant: databuffer servant %s: Failed to get NamingContext" %(unique_id)
      print repr(ex)
      sys.exit(1)

    self.corba_name = [CosNaming.NameComponent("ofdm_ti",unique_id)]
    try:
      self.rootContext.bind(self.corba_name,self.corba_servant_o)
    except: # CosNaming.NamingContext.AlreadyBound, ex:
      self.rootContext.rebind(self.corba_name,self.corba_servant_o)

  def __del__(self):
    print "Unbinding corba name",self.uid
    if hasattr(self, "rootContext") and self.rootContext is not None:
      self.rootContext.unbind(self.corba_name)


################################################################################
################################################################################

"""
CORBA servant for number display
"""
class ndata_buffer_i(ofdm_ti__POA.data_buffer):
  def __init__(self,get_number,reset):
    self.get_number = get_number
    self.reset = reset

  def get_data(self):
    try:
      data = [float(self.get_number())]
    except:
      data = -1
    return data

  def flush(self):
    self.reset()

  def vlen(self):
    return 1

class corba_ndata_buffer_servant:
  def __init__(self,unique_id,get_number,reset):
    self.uid = unique_id

    orb = CORBA.ORB_init(sys.argv,CORBA.ORB_ID)
    poa = orb.resolve_initial_references("RootPOA")

    poaManager = poa._get_the_POAManager()
    poaManager.activate()

    self.corba_servant_i = ndata_buffer_i(get_number,reset)
    self.corba_servant_o = self.corba_servant_i._this()

    try:
      obj = orb.resolve_initial_references("NameService")
      self.rootContext = obj._narrow(CosNaming.NamingContext)
    except Exception,ex:
      print "CORBA servant: ndatabuffer servant : Failed to get NamingContext"
      print repr(ex)
      sys.exit(1)

    self.corba_name = [CosNaming.NameComponent("ofdm_ti",unique_id)]
    try:
      self.rootContext.bind(self.corba_name,self.corba_servant_o)
    except: #CosNaming.NamingContext.AlreadyBound, ex:
      self.rootContext.rebind(self.corba_name,self.corba_servant_o)

  def __del__(self):
    print "Unbinding corba name",self.uid
    if hasattr(self, "rootContext") and self.rootContext is not None:
      self.rootContext.unbind(self.corba_name)

################################################################################
################################################################################

"""
CORBA servant to set power allocation etc.
"""
class push_vector_f_i(ofdm_ti__POA.push_vector_f):
  def __init__(self,vector_length,push_vector_func,msg):
    self.vec_len = vector_length
    self.push_vector_func = push_vector_func
    self.msg = msg

  def push(self, vector):
    try:
      assert(len(vector) == self.vec_len)
      self.push_vector_func(vector)
      sys.stdout.write(self.msg)
      sys.stdout.flush()
    except:
      sys.stderr.write("push failed for ",self.msg)
      sys.stderr.flush()

  def vlen(self):
    return self.vec_len

class corba_push_vector_f_servant:
  def __init__(self,unique_id,vector_length,push_vector_func,msg):
    orb = CORBA.ORB_init(sys.argv,CORBA.ORB_ID)
    poa = orb.resolve_initial_references("RootPOA")

    self.uid = unique_id

    poaManager = poa._get_the_POAManager()
    poaManager.activate()

    self.corba_servant_i = push_vector_f_i(vector_length,push_vector_func,msg)
    self.corba_servant_o = self.corba_servant_i._this()

    try:
      obj = orb.resolve_initial_references("NameService")
      #obj = orb.string_to_object("corbaloc::hestia/NameService")
      self.rootContext = obj._narrow(CosNaming.NamingContext)
    except Exception,ex:
      print "CORBA servant : pushvectorf servant : Failed to get NamingContext"
      print repr(ex)
      sys.exit(1)

    self.corba_name = [CosNaming.NameComponent("ofdm_ti",unique_id)]
    try:
      self.rootContext.bind(self.corba_name,self.corba_servant_o)
    except:
      self.rootContext.unbind(self.corba_name)
      self.rootContext.rebind(self.corba_name,self.corba_servant_o)

  def __del__(self):
    print "Unbinding corba name",self.uid
    self.rootContext.unbind(self.corba_name)


################################################################################
################################################################################

"""
CORBA servant to set power allocation etc.
"""
class push_vector_c_i(ofdm_ti__POA.push_vector_c):
  def __init__(self,vector_length,push_vector_func,msg):
    self.vec_len = vector_length
    self.push_vector_func = push_vector_func
    self.msg = msg

  def push(self, vector):
    try:
      vec = [vector[2*i] + 1j*vector[2*i+1] for i in range(len(vector)/2)]
      assert(len(vec) == self.vec_len)
      self.push_vector_func(vec)
      sys.stdout.write(self.msg)
      sys.stdout.flush()
    except:
      sys.stderr.write("push failed for %s"%(self.msg))
      sys.stderr.flush()

  def vlen(self):
    return self.vec_len

class corba_push_vector_c_servant:
  def __init__(self,unique_id,vector_length,push_vector_func,msg):
    orb = CORBA.ORB_init(sys.argv,CORBA.ORB_ID)
    poa = orb.resolve_initial_references("RootPOA")

    self.uid = unique_id

    poaManager = poa._get_the_POAManager()
    poaManager.activate()

    self.corba_servant_i = push_vector_c_i(vector_length,push_vector_func,msg)
    self.corba_servant_o = self.corba_servant_i._this()

    try:
      obj = orb.resolve_initial_references("NameService")
      #obj = orb.string_to_object("corbaloc::hestia/NameService")
      self.rootContext = obj._narrow(CosNaming.NamingContext)
    except Exception,ex:
      print "CORBA servant : pushvectorc servant : Failed to get NamingContext"
      print repr(ex)
      sys.exit(1)

    self.corba_name = [CosNaming.NameComponent("ofdm_ti",unique_id)]
    try:
      self.rootContext.bind(self.corba_name,self.corba_servant_o)
    except:
      self.rootContext.unbind(self.corba_name)
      self.rootContext.rebind(self.corba_name,self.corba_servant_o)

  def __del__(self):
    print "Unbinding corba name",self.uid
    self.rootContext.unbind(self.corba_name)

################################################################################
################################################################################

class general_corba_servant:
  def __init__(self,unique_id,servant_i):
    orb = CORBA.ORB_init(sys.argv,CORBA.ORB_ID)
    poa = orb.resolve_initial_references("RootPOA")

    self.uid = unique_id

    poaManager = poa._get_the_POAManager()
    poaManager.activate()

    self.corba_servant_i = servant_i
    self.corba_servant_o = self.corba_servant_i._this()

    try:
      obj = orb.resolve_initial_references("NameService")
      self.rootContext = obj._narrow(CosNaming.NamingContext)
    except Exception,ex:
      print "CORBA servant : general corba servant : Failed to get NamingContext"
      print repr(ex)
      sys.exit(1)

    self.corba_name = [CosNaming.NameComponent("ofdm_ti",unique_id)]
    try:
      self.rootContext.bind(self.corba_name,self.corba_servant_o)
    except:
      self.rootContext.unbind(self.corba_name)
      self.rootContext.rebind(self.corba_name,self.corba_servant_o)

  def __del__(self):
    print "Unbinding corba name",self.uid
    self.rootContext.unbind(self.corba_name)
