#!/usr/bin/env python

from gnuradio import gr

def delayline_cc(delay):
    return gr.delay(gr.sizeof_gr_complex,delay)

def delayline_ff(delay):
    return gr.delay(gr.sizeof_float,delay)
