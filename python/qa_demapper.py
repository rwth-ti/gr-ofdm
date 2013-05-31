#!/usr/bin/env python

from gnuradio import gr, gr_unittest
import ofdm_swig as ofdm
from random import seed,randint
from numpy import concatenate
import numpy

from sys import stderr


class qa_demapper (gr_unittest.TestCase):
  def setUp (self):
    self.fg = gr.top_block ("test_block")

  def tearDown (self):
    self.fg = None

  def std_test (self, vlen, data, bitmap, trig):
    dut = ofdm.generic_demapper_vcb(vlen)
    
    sym_src = gr.vector_source_c(data,False, vlen)
    bmap_src = gr.vector_source_b(bitmap,False, vlen)
    trig_src = gr.vector_source_b(trig,False)
    dst = gr.vector_sink_b()
    
    self.fg.connect(sym_src,(dut,0))
    self.fg.connect(bmap_src,(dut,1))
    self.fg.connect(trig_src,(dut,2))
    self.fg.connect(dut,dst)
    
    self.fg.run()
    
    return list(dst.data())

  # one bitmap
  def test_001(self):
    vlen = 16
    blks = 5
    
    bitmap = [1]*vlen
    
    trig = [0]*blks
    trig[0] = 1
    
    bitdata = [randint(0,1) for i in range(blks*vlen)]
    data = numpy.array(bitdata)*(-2)+1
    
    d = self.std_test(vlen, data.tolist(), bitmap, trig)
    
    if d != list(bitdata):
      self.assert_(False)
    else:
      self.assert_(True)

  # new bitmap for each data block
  def test_002(self):
    vlen = 16
    blks = 5
    
    bitmap = [1]*(vlen*blks)
    
    trig = [1]*blks
    
    bitdata = [randint(0,1) for i in range(blks*vlen)]
    data = numpy.array(bitdata)*(-2)+1
    
    d = self.std_test(vlen, data.tolist(), bitmap, trig)
    
    if d != list(bitdata):
      self.assert_(False)
    else:
      self.assert_(True) 
  
  # two identical bitmaps, first 3 blocks, second 2 blocks
  def test_003(self):
    vlen = 16
    blks = 5
    
    bitmap = [1]*(vlen*2)
    
    trig = [0]*blks
    trig[0] = 1
    trig[3] = 1
    
    bitdata = [randint(0,1) for i in range(blks*vlen)]
    data = numpy.array(bitdata)*(-2)+1
    
    d = self.std_test(vlen, data.tolist(), bitmap, trig)
    
    if d != list(bitdata):
      self.assert_(False)
    else:
      self.assert_(True)
  
  # two different bitmaps, first 3 blocks, second 2 blocks  
  def test_005(self):
    vlen = 16
    blks = 5
    
    bitmap = concatenate([[1]*vlen,[0]*vlen]).tolist()
    
    trig = [0]*blks
    trig[0] = 1
    trig[3] = 1
    
    bitdata = [randint(0,1) for i in range(3*vlen)]
    data = numpy.array(bitdata)*(-2)+1
    data = concatenate([data, [1j]*(2*vlen)]).tolist()
        
    d = self.std_test(vlen, data, bitmap, trig)
    
    if d != list(bitdata):
      self.assert_(False)
    else:
      self.assert_(True)
      
  # three different bitmaps  
  def test_006(self):
    vlen = 16
    blks = 5
    
    bitmap = concatenate([[1]*vlen,[0]*vlen,[1]*vlen]).tolist()
    
    trig = [0]*blks
    trig[0] = 1
    trig[2] = 1
    trig[3] = 1
    
    bitdata = [randint(0,1) for i in range(4*vlen)]
    data = numpy.array(bitdata)*(-2)+1
    data = concatenate([data[0:(2*vlen)], [1j]*(1*vlen), 
                        data[(2*vlen):(4*vlen)], [1j]*(1*vlen)])
    
    d = self.std_test(vlen, data.tolist(), bitmap, trig)
    
    if d != list(bitdata):
      self.assert_(False)
    else:
      self.assert_(True)
    
    
  # enforce reuse of internally saved bitmap
  def test_007(self):
    vlen = 16
    blks = 10000
    
    bitmap = [1]*vlen
    
    trig = [0]*blks
    trig[0] = 1
    
    bitdata = [randint(0,1) for i in range(blks*vlen)]
    data = numpy.array(bitdata)*(-2)+1
    
    d = self.std_test(vlen, data.tolist(), bitmap, trig)
    
    if d != list(bitdata):
      self.assert_(False)
    else:
      self.assert_(True)

  # enforce reuse of internally saved bitmap
  # two bitmaps, second scheduled very late 
  def test_008(self):
    vlen = 16
    blks = 10000
    
    bitmap = concatenate([[1]*vlen,[0]*vlen]).tolist()
    
    trig = [0]*blks
    trig[0] = 1
    trig[blks-2] = 1
    
    bitdata = [randint(0,1) for i in range((blks-2)*vlen)]
    data = numpy.array(bitdata)*(-2)+1
    data = concatenate([data,[1j]*(vlen*2)]).tolist()
    
    d = self.std_test(vlen, data, bitmap, trig)
    
    if d != list(bitdata):
      self.assert_(False)
    else:
      self.assert_(True)
       
    
  # three bitmaps, second uses half number of subcarriers
  def test_009(self):
    vlen = 16
    blks = 10
    
    bitmap = concatenate([[1]*vlen,[1]*(vlen/2),[0]*(vlen/2),[1]*vlen]).tolist()
    
    trig = [0]*blks
    trig[0] = 1
    trig[6] = 1
    trig[8] = 1
    
    bitdata = [randint(0,1) for i in range((blks-1)*vlen)]
    data = numpy.array(bitdata)*(-2)+1

    data = concatenate([data[0:(vlen*6)].tolist(),
                        data[(vlen*6):(vlen*6+vlen/2)],
                        [1j]*(vlen/2),
                        data[(vlen*6+vlen/2):(vlen*7)],
                        [1j]*(vlen/2),
                        data[(vlen*7):len(data)]])

    d = self.std_test(vlen, data, bitmap, trig)
    
    if d != list(bitdata):
      self.assert_(False)
    else:
      self.assert_(True)
    
  # three bitmaps, second uses half number of subcarriers
  # force save first bitmap, reuse very oftem
  # scheduled other bitmaps very late
  def test_010(self):
    vlen = 16
    blks = 10000
    
    bitmap = concatenate([[1]*vlen,[1]*(vlen/2),[0]*(vlen/2),[1]*vlen]).tolist()
    
    trig = [0]*blks
    trig[0] = 1
    trig[(blks-4)] = 1
    trig[(blks-2)] = 1
    
    bitdata = [randint(0,1) for i in range((blks-1)*vlen)]
    data = numpy.array(bitdata)*(-2)+1

    data = concatenate([data[0:(vlen*(blks-4))].tolist(),
                        data[(vlen*(blks-4)):(vlen*(blks-4)+vlen/2)],
                        [1j]*(vlen/2),
                        data[(vlen*(blks-4)+vlen/2):(vlen*(blks-3))],
                        [1j]*(vlen/2),
                        data[(vlen*(blks-3)):len(data)]])

    d = self.std_test(vlen, data, bitmap, trig)
    
    if d != list(bitdata):
      self.assert_(False)
    else:
      self.assert_(True)
    
  # three bitmaps, second uses half number of subcarriers
  def test_011(self):
    vlen = 16
    blks = 3
    
    bitmap = concatenate([[1]*vlen,[1]*(vlen/2),[0]*(vlen/2),[1]*vlen]).tolist()
    
    trig = [1]*blks
    
    bitdata = [randint(0,1) for i in range((blks-1)*vlen+vlen/2)]
    data = numpy.array(bitdata)*(-2)+1

    data = concatenate([data[0:vlen].tolist(),
                        data[(vlen):(vlen+vlen/2)],
                        [1j]*(vlen/2),
                        data[(vlen+vlen/2):len(data)]])

    d = self.std_test(vlen, data.tolist(), bitmap, trig)
    
    if d != list(bitdata):
      self.assert_(False)
    else:
      self.assert_(True)
    
  def test_012(self):
    vlen = 16
    blks = 10000
    
    bitmap = concatenate([[1]*vlen,[1]*(vlen/2),[0]*(vlen/2)]).tolist()
    bitmap = concatenate([bitmap]*(blks/2)).tolist()
    
    trig = [1]*blks
    
    bitdata = [randint(0,1) for i in range((blks/2)*vlen+(blks/2)*vlen/2)]
    t = numpy.array(bitdata)*(-2)+1
    
    data = []
    ind = 0
    for i in range(blks/2):
      data.append(t[ind:(ind+3*vlen/2)])
      data.append([1j]*(vlen/2))
      ind = ind + 3*vlen/2

    data = concatenate(data).tolist()

    d = self.std_test(vlen, data, bitmap, trig)
    
    if d != list(bitdata):
      self.assert_(False)
    else:
      self.assert_(True)
    


if __name__ == '__main__':
  gr_unittest.main()
