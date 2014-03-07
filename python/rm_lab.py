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

from numpy import concatenate, abs, numarray, argmin, argmax, zeros, \
        inf, sqrt, log10, ceil
from scipy.special import erfcinv
import numpy
import time
import array

from gnuradio import eng_notation
from configparse import OptionParser

from time import strftime, gmtime

import logging

from resource_manager_base_lab import resource_manager_base_lab, \
        start_resource_manager

from corba_stubs import ofdm_ti


class resource_manager(resource_manager_base_lab):

    def __init__(self, orb, options):
        resource_manager_base_lab.__init__(self, orb, options=options,
                loggerbase='suw.')
        
        self.logger = logging.getLogger("suw.rm")
        self.logger.setLevel(logging.DEBUG)
        # set initial parameters

        self.required_ber = 1e-3
        self.constraint = 4000  # rate or power, RMS!
        self.modulation = options.init_mod
        self.tx_amplitude = 4000
        self.setup_time = 1000  # ms
        self.data_rate = 365079  # implicitly exposed to GUI

        self.store_ctrl_events = False

        self.auto_state = 0
        self.state1_cntr = 0
        self.mod_map = [self.modulation] * self.subcarriers
        self.options = options

    def work(self):
        self.query_sounder()
        print self.ac_vector

        self.ac_vector = [0.0 + 0.0j] * self.ac_vlen
        if self.ac_vlen >= 8:
            self.ac_vector[3] = 0.3267
            self.ac_vector[4] = 0.8868
            self.ac_vector[5] = 0.3267

        rxperf = self.get_rx_perf_meas()

        if self.store_ctrl_events:
            self.process_received_events(rxperf)
        
        if len(rxperf) != 0:
            rxperf = rxperf[len(rxperf) - 1]
            current_ber = rxperf.ber
            snr_mean = rxperf.snr
            ctf = rxperf.ctf
        else:
            print 'Receiver not running or power constraint is too low for receiver...'
            current_ber = 1
            snr_mean = 0
            ctf = 0

        # this is for the lab exercise special case with only half the subcarriers
        if self.options.lab_special_case:
            nl = range(self.subcarriers/4)
            nr = range(3*self.subcarriers/4,self.subcarriers)
            self.null_indeces = nl + nr
            self.pa_vector = [2]*self.subcarriers
            self.mod_map = [self.modulation]*self.subcarriers
            self.assignment_map = [1]*self.subcarriers
            for x in self.null_indeces:
                self.assignment_map[x] = 0
                self.mod_map[x] = 0
                self.pa_vector[x] = 0
        else:
            self.pa_vector = [1.0] * self.subcarriers
            self.mod_map = [self.modulation] * self.subcarriers
            self.assignment_map = [1] * self.subcarriers

        self.tx_amplitude = self.constraint

        frame_length_samples = 12 * self.block_length  # FIXME constant
        bits_per_frame = self.modulation * self.subcarriers * 9  # FIXME constant
        frame_duration = frame_length_samples / self.bandwidth
        self.data_rate = bits_per_frame / frame_duration

        c_ber = max(current_ber, 1e-7)

        snr_mean_lin = 10 ** (snr_mean / 10.0)
        print 'Current SNR:', snr_mean
        print 'Current BER:', c_ber
        snr_func_lin = 2.0 * erfcinv(c_ber) ** 2.0
        snr_func = 10 * log10(snr_func_lin)
        print 'Func. SNR:', snr_func
        delta = self._delta = snr_mean_lin / snr_func_lin
        print 'Current delta', delta
        self._agg_rate = 2

    def start_measurement(self):
        self.bervec = list()
        self.snrvec = list()
        self.datarate_vec = list()
        self.txamp_vec = list()
        self.start_time = strftime('%a, %d %b %Y %H:%M:%S +0000',
                gmtime())

        self.filename_prefix = strftime('%Y%m%d%H%M%S', gmtime())

    def end_measurement(self):
        bervec = numpy.array(self.bervec)
        snrvec = numpy.array(self.snrvec)
        datarate_vec = numpy.array(self.datarate_vec)
        txamp_vec = numpy.array(self.txamp_vec)
        berout = array.array('f')
        snrout = array.array('f')
        datarate_out = array.array('f')
        txamp_out = array.array('f')
        berout.fromlist(bervec.astype(float).tolist())
        snrout.fromlist(snrvec.astype(float).tolist())
        datarate_out.fromlist(datarate_vec.astype(float).tolist())
        txamp_out.fromlist(txamp_vec.astype(float).tolist())

        filename_prefix = self.filename_prefix
        f_ber = open(filename_prefix + '_ber.float', 'wb')
        f_snr = open(filename_prefix + '_snr.float', 'wb')
        f_datarate = open(filename_prefix + '_datarate.float', 'wb')
        f_txamp = open(filename_prefix + '_txamp.float', 'wb')
        f_nfo = open(filename_prefix + '_nfo.txt', 'w')

        berout.tofile(f_ber)
        snrout.tofile(f_snr)
        datarate_out.tofile(f_datarate)
        txamp_out.tofile(f_txamp)

        f_nfo.write('Start time: %s\n' % self.start_time)
        f_nfo.write('End time: %s\n'
                % strftime('%a, %d %b %Y %H:%M:%S +0000', gmtime()))
        f_nfo.write('Required BER: %.8g\n' % self.required_ber)

        f_ber.close()
        f_snr.close()
        f_datarate.close()
        f_txamp.close()

    def process_received_events(self, rxperf):
        assert len(rxperf) > 0

        for x in rxperf:

            if x.rx_id in self.ctrl_events.keys():

                previd = x.rx_id - 1
                if previd < 0:
                    previd += self.max_tx_id

                if previd in self.ctrl_events.keys():
                    del self.ctrl_events[previd]

                ev = self.ctrl_events[x.rx_id]
                self.bervec.append(x.ber)
                self.snrvec.append(x.snr)
                self.datarate_vec.append(ev.datarate)
                self.txamp_vec.append(ev.tx_amplitude)
            else:
                pass
                

    def add_options(normal, expert):
        """
        Adds receiver-specific options to the Options Parser
        """

        resource_manager_base_lab.add_options(normal, expert)
        normal.add_option('', '--automode', action='store_true',
                default=False,
                help='Activate automatic measurement mode')
        expert.add_option('', '--usrp2', action='store_true',
                default=False, help='USRP2')
        expert.add_option('', '--lab_special_case', action='store_true',
                default=False, help='For lab exercise, use only half the subcarriers')

    add_options = staticmethod(add_options)


def main():
    logger = logging.getLogger("suw")
    logger.setLevel(logging.DEBUG)
    ch = logging.StreamHandler()
    ch.setLevel(logging.DEBUG)
    logger.addHandler(ch)
 
    parser = OptionParser(conflict_handler='resolve')

    expert_grp = parser.add_option_group('Expert')

    resource_manager.add_options(parser, expert_grp)

    parser.add_option(
            '-c',
            '--cfg',
            action='store',
            type='string',
            default=None,
            help='Specifiy configuration file, default: none',
            config='false',
            )

    (options, args) = parser.parse_args()

    if options.cfg is not None:
        (options, args) = parser.parse_args(files=[options.cfg])
        print 'Using configuration file %s' % options.cfg

    start_resource_manager(resource_manager, 'PA', options)


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        pass
