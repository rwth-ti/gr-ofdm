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

from gnuradio import gr, gr_unittest
from ofdm import peak_detector2_fb
import ofdm as ofdm

import numpy, random

class qa_peakdetector (gr_unittest.TestCase):
  def setUp (self):
    self.fg = gr.top_block ("test_block")

  def tearDown (self):
    self.fg = None

  def test_001 (self):
    x = [0.1*i for i in range(10)]
    x = numpy.concatenate([x,[1.0],x[::-1],[0.0]*10])

    src = gr.vector_source_f(x)
    dst = gr.vector_sink_b()
    #blk = ofdm.peak_detector2_fb(10)
    blk = peak_detector2_fb(10)

    self.fg.connect(src,blk,dst)
    self.fg.run()
    y = [0]*len(dst.data())
    y[10] = 1
    self.assertEqual(y,list(dst.data()))

#  def test_002 (self):
#    x = [0.1*i for i in range(10)]
#    x = numpy.concatenate([x,[1.0],x[::-1],[0.0]*10])
#
#    src = gr.vector_source_f(x)
#    dst = gr.vector_sink_b()
#    blk = ofdm.peak_detector_fb(10,0.0)
#
#    self.fg.connect(src,blk,dst)
#    self.fg.run()
#    y = [0]*len(dst.data())
#    y[10] = 1
#    self.assertEqual(y,list(dst.data()))

  def test_003 (self):
    x = [0.1*i for i in range(10)]
    x = numpy.concatenate([x,[1.0],x[::-1]])
    x = numpy.concatenate([x,x,[0.0]*10])

    src = gr.vector_source_f(x)
    dst = gr.vector_sink_b()
    blk = ofdm.peak_detector2_fb(10)

    self.fg.connect(src,blk,dst)
    self.fg.run()
    y = [0]*len(dst.data())
    y[10] = 1
    y[31] = 1
    self.assertEqual(y,list(dst.data()))

#  def test_004 (self):
#    x = [0.1*i for i in range(10)]
#    x = numpy.concatenate([x,[1.0],x[::-1]])
#    x = numpy.concatenate([x,x,[0.0]*10])
#
#    src = gr.vector_source_f(x)
#    dst = gr.vector_sink_b()
#    blk = ofdm.peak_detector_fb(10,0.0)
#
#    self.fg.connect(src,blk,dst)
#    self.fg.run()
#    y = [0]*len(dst.data())
#    y[10] = 1
#    y[31] = 1
#    self.assertEqual(y,list(dst.data()))
#
#  def test_005 (self):
#    random.seed(0)
#    x = [random.uniform(0,1) for i in range(500000)]
#
#    src = gr.vector_source_f(x)
#    dst = gr.vector_sink_b()
#    blk = peak_detector2_fb(10)
#
#    self.fg.connect(src,blk,dst)
#    self.fg.run()
#
#    e1= list(dst.data())
#    e = 0
#    #print len(e1),len(e2)
#    for i in range(0,min(len(e1),len(x)-10)):
#      y = numpy.array(x[max(0,i-10):min(len(e1),i+11)])
#      am = numpy.argmax(y)
#      if e1[i] == 1:
#        print "PD ",x[i], " at ",i
#      if am == 10:
#        if e1[i] != 1:
#          e = e+1
#          print "Failed peak detection at ",i
#      else:
#        if e1[i] != 0:
#          e = e+1
#          print "False alert at ",i
#          print y,am

#  def test_005 (self):
#    random.seed(0)
#    x = [random.uniform(0,1) for i in range(500000)]
#
#    src = gr.vector_source_f(x)
#    dst = gr.vector_sink_b()
#    dst2 = gr.vector_sink_b()
#    blk = ofdm.peak_detector_fb(10,0.0)
#    blk2 = peak_detector2_fb(10)
#
#    self.fg.connect(src,blk,dst)
#    self.fg.connect(src,blk2,dst2)
#    self.fg.run()
#
#    e1= list(dst.data())
#    e2= list(dst2.data())
#    if len(e1) != len(e2):
#      l = min(len(e1),len(e2))
#      e1=e1[0:l]
#      e2=e2[0:l]
#    e = 0
#    #print len(e1),len(e2)
#    for i in range(len(e1)):
#      if e1[i] != e2[i]:
#        if e2[i] == 1:
#          y = numpy.array(x[max(0,i-10):min(len(e1),i+11)])
#          if numpy.argmax(y) == 10:
#            print "error at old peak detector",i
#          else:
#            print "error at",i,"in new detector ", numpy.argmax(y)
#            e += 1
#        else:
#          y = numpy.array(x[max(0,i-10):min(len(e1),i+11)])
#          print "mismatch between old and new at",i
#          print y, "argmax at",numpy.argmax(y)
#          e += 1
#          for a in range(i+1,len(e1)):
#            if e1[a] == 1:
#              print "next e1 at",a
#              break
#
#          for a in range(i+1,len(e2)):
#            if e2[a] == 1:
#              print "next e2 at",a
#              break
#
#          for a in range(i-1,-1,-1):
#            if e1[a] == 1:
#              print "prev e1 at",a
#              break
#
#          for a in range(i-1,-1,-1):
#            if e2[a] == 1:
#              print "prev e2 at",a
#              break
##    self.assertEqual(e,0)
#
#        print "at",i,("holla" if e1[i] == 1 else "")#
#        print numpy.array(x[i-10:i+11])
#        print x[i]
#
#        for a in range(i+1,len(e1)):
#          if e1[a] == 1:
#            print "next e1 at",a
#            break
#
#        for a in range(i+1,len(e2)):
#          if e2[a] == 1:
#            print "next e2 at",a
#            break
#
#        for a in range(i-1,-1,-1):
#          if e1[a] == 1:
#            print "prev e1 at",a
#            break
#
#        for a in range(i-1,-1,-1):
#          if e2[a] == 1:
#            print "prev e2 at",a
#            break
#
#    #self.assertEqual(e1,e2)

if __name__ == '__main__':
  gr_unittest.main()
