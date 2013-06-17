#!/usr/bin/env python


from threading import Timer
from corba_stubs import ofdm_ti
import time

from numpy import concatenate
import numpy

import scipy,math
from scipy import sqrt,log, exp,randn, sum, absolute, multiply, array2string, reshape, ceil, array, zeros,ones, log, floor
from pylab import plot, stem, subplot, show, ylim
from numpy.fft import fftshift

from resource_manager_base import resource_manager_base,start_resource_manager

class rm_old_implementation (resource_manager_base):
  def __init__(self,orb):
    resource_manager_base.__init__(self,orb)

    # set initial parameters
    self.strategy_mode = ofdm_ti.PA_Ctrl.reset
    self.required_ber = 0.01
    self.constraint = 4000.0 # rate or power
    self.setup_time = 3*1000 # ms
    self.data_rate= 365079
    self.tx_amplitude = 50004

  def work(self):
    self.query_sounder()
    self.get_ber()

    snr_vec = self.get_snr()
    snr_mean = 10**(snr_vec[len(snr_vec)-1]/10)
    snr_var = numpy.var(snr_vec)
    print "SNR mean", snr_vec[len(snr_vec)-1],"dB"
    print "SNR mean", snr_mean


    #fft of cir
    # FIXME: coded constant
    no_pilot_subcarrier = 8
    vsubc_left = (self.fft_length-self.subcarriers-no_pilot_subcarrier)/2

    ci=scipy.fft (self.ac_vector,self.fft_length)
    ci=abs(fftshift(ci))
    ci=ci[vsubc_left:vsubc_left+self.subcarriers+no_pilot_subcarrier]

    # FIXME: no need to know about pilot subcarriers
    # compute pilot subcarriers
    pilot_tones=[]
    subc = self.subcarriers+no_pilot_subcarrier
    pilot_dist = subc/2/(no_pilot_subcarrier/2+1)
    for i in range(0,no_pilot_subcarrier/2):
      pilot_tones.append(pilot_dist*(i+1))
      pilot_tones.append(-pilot_dist*(i+1))
    pilot_tones.sort()
    shifted_pilot_tones = map(lambda x: x+subc/2-1, pilot_tones)

    ci_n = [0]*self.subcarriers
    i = 0
    for x in range(len(ci)):
      if not x in shifted_pilot_tones:
        ci_n[i] = ci[x]
        i=i+1
    ci=ci_n

    vector_len=len(ci)
    ci=array(ci)
    ci=ci*ci*ci



    ###############################################

    if self.strategy_mode!=ofdm_ti.PA_Ctrl.reset:
      try:
        #Obtaining requested SNR corrected with self.delta
        self.snr_req_f = 2*(-log(5*self.required_ber)) #Approx. for QPSK AWGN case (Goldsmith's paper)
        #self.snr_req=self.snr_req_f+self.delta

        #Modification of self.snr_req to be dependent of present ber <-> changing the delta
        self.snr_obt_f = 2*(-log(5*self.current_ber))
        self.delta_1 = self.snr_req_f/self.snr_obt_f
        print "delta 1 ", self.delta_1


        #self.snr_req=self.snr_req_f*self.delta*self.delta_1
        self.snr_req=self.snr_req_f*self.delta

        #Obtaining requested TX amplitude
        req_tx=self.tx_amplitude*sqrt(self.snr_req/snr_mean)*vector_len/self.used_subc/math.sqrt(self.factor)
        print "req_tx", req_tx
        print "Requested amplitude",  (req_tx)
        print "Requested power per symbol ",  (req_tx**2)/vector_len
        print "Requested power",  (req_tx**2)
      except:
        self.strategy_mode=ofdm_ti.PA_Ctrl.reset

    ###### Sum of ci excluding pilot subcarriers##########################
    #print ci
    ci_a=array(ci)
    #print "LEN",  len(ci_a),ci_a
    #print ci_i,len(ci_i)
    summ=sum(1./ci_a)
    #print "summ", summ
    #print ci_a
    ######################################################################
    # fixed: 13 -> 14 ofdm blocks per frame
    k=self.bandwidth/self.block_length*self.data_frame_length/self.frame_length
    #*0.92#(options.subcarriers-pilot_subcarriers)/options.subcarriers #bandwidth/(fft_size + cp)*10/14*92/100= 2136.752136752136 max_rate=365079.36507936509
    #con_tx = self.constraint

    #PA part
    if self.strategy_mode==ofdm_ti.PA_Ctrl.rate_adaptive:
        con_tx = self.constraint
        #new power constraint, reduced by gamma
        gamma=(req_tx/con_tx)**2
        if (gamma <=1):
            gamma=1
        nc=1/gamma

        thr=6 # Should be examined what is the optimal one!?
        if (gamma > thr):
          self.fact=gamma/thr
        else:
          self.fact = 1

        print "fact = ", self.fact
        print "Gamma = ", gamma
        print "Constrained amplitude ",  (con_tx)
        print "Constrained power ",  (con_tx**2)

        xi=zeros(len(ci))
        s=0
        for i in range (vector_len):
            xi[i]=(1./ci[i])/(summ)

        print "SUM ", sum(xi)

        #xi=(1./ci)/sum(1./ci)
        while(sum(xi)>1.001*nc):
            ind_max=xi.argmax()
            xi[ind_max]=0.0

        xi=xi*vector_len*gamma/self.fact
        self.pa_vector=xi
        suma= sum(xi)*req_tx**2/vector_len/gamma*self.fact
        real_suma= suma*self.fact
        self.tx_amplitude=math.sqrt(real_suma)
        #self.propagate_changes()
        self.used_subc=xi[xi.nonzero()].size
        self.data_rate = k*2*(self.used_subc)
        print "Tx Power", suma
        print "Real Tx Power", real_suma
        print "Tx Amplitude",math.sqrt(suma) #This should be publish on TX GUI
        print "Real Tx Amplitude",self.tx_amplitude
        print "Data rate ",  self.data_rate

    elif self.strategy_mode==ofdm_ti.PA_Ctrl.margin_adaptive:
        print "Requested data rate", self.constraint
        if (self.constraint >vector_len*2*k ):
            #print "Increase numer of subcarriers,  -s = ", (ceil(self.constraint/k/2)), ", or decrease data rate -d = ",(floor(vector_len*k*2))
            #sys.exit(1)
            self.constraint = vector_len*2*k

        newsc=int(ceil(self.constraint/k/2.))
        print "Numer of subcarriers", newsc

        xi_i=zeros(len(ci))
        xi=zeros(len(ci))
        indeks_sorted=ci_a.argsort()
        ci_sorted=ci_a[indeks_sorted]

        ci_extracted=ci_sorted[(vector_len-newsc):]
        xi_extracted=array([(1./ci_extracted[j])/sum([(1./ci_extracted[i]) for i in range (newsc)]) for j in range (newsc)])

        indeks_extracted=indeks_sorted[(vector_len-newsc):]

        #xi_new=[0.0 for i in range (options.subcarriers)]
        xi_new=zeros(vector_len)

        for i in range (newsc):
            xi_new[indeks_extracted[i]]=xi_extracted[i]
        xi=newsc*xi_new

        self.pa_vector=xi
        suma= sum(xi)*(req_tx**2)/vector_len
        self.tx_amplitude=math.sqrt(suma)
        self.used_subc=xi[xi.nonzero()].size
        self.data_rate = k*2*(self.used_subc)
        #self.propagate_changes()
        print "Transmit power", suma
        print "Transmit amplitude", math.sqrt(suma)
        print "Data rate ",  self.data_rate

    elif self.strategy_mode==ofdm_ti.PA_Ctrl.reset:
        print "reset mode"
        self.used_subc=vector_len
        self.factor = 1
        #Obtaining current SNR according to function
        #0.2/exp(1.5*10**(snr_a/10)/3)
        self.snr_init_f=2*(-log(5*self.current_ber)) #Approx. for AWGN QPSK case (Goldsmith's paper)
        print "BER_init ", self.current_ber
        print "self.snr_init_f ", self.snr_init_f

        #Calculating self.delta = snr_mean - self.snr_init_f
        #self.delta=snr_mean-self.snr_init_f
        self.delta=snr_mean/self.snr_init_f # new delta
        self.delta_1 = 1.0
        print "self.delta", self.delta

        xi=array(ones(vector_len))
        #xi = [float(i**2)/(vector_len**2/2)*8.0+1.0 for i in range(vector_len/2)]
        #xi = numpy.concatenate([xi[::-1],xi])
        #gain = sqrt(sum(absolute(xi)**2))
        #xi = xi/gain*sqrt(vector_len)
        #suma= sum(xi)*req_tx**2/vector_len/gamma
        suma= sum(xi)*self.constraint**2/vector_len
        self.pa_vector=xi
        self.tx_amplitude= math.sqrt(suma)
        print "Tx Power", self.pa_vector
        print "Tx Amplitude",self.tx_amplitude
        print "Data rate ",  k*2*xi[xi.nonzero()].size
        self.data_rate = k*2*xi[xi.nonzero()].size

    # TODO adjust self.pa_vector, self.ac_vector, self.tx_amplitude
    # note that self.ac_vector is a complex vector, represented by a float
    # vector with doubled vector length, i.e. 2 floats per complex. Even indices
    # are real parts, odd indices are imaginary parts.
    # The sum over the pa vector should never exceed the pa_vlen. From the PA's
    # point of view, it can distribute pa_vlen power units within this vector.
    # The same goes for the ac vector. You should have unity gain.

    #self.tx_amplitude = randint(7000,9000)
    #self.pa_vector = [random.uniform(0.7,1.4) for i in range(self.pa_vlen)]
    #self.ac_vector = concatenate([[random.uniform(0.8,1.0),0.0]
                                  #for i in range(self.ac_vlen)])

    print "PA Vector",self.pa_vector

################################################################################

def main():
  start_resource_manager(rm_old_implementation, "PA")

if __name__ == '__main__':
  try:
    main()
  except KeyboardInterrupt:
    pass
