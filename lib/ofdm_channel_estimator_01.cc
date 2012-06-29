#ifdef HAVE_CONFIG_H
#include "config.h"
#endif

#include <gr_sync_block.h>
#include <gr_io_signature.h>
#include <ofdm_channel_estimator_01.h>

#include <cmath>
#include <iostream>

#include <string.h>

#define DEBUG(x)

static const float s_power_threshold = 10e-3;

ofdm_channel_estimator_01_sptr ofdm_make_channel_estimator_01(int vlen)
{
  return ofdm_channel_estimator_01_sptr(new ofdm_channel_estimator_01(vlen));
}

ofdm_channel_estimator_01::ofdm_channel_estimator_01 (int vlen)
  : gr_sync_block ("channel_estimator_01",
           gr_make_io_signature2(2, 2, sizeof(gr_complex)*vlen, sizeof(char)),
           gr_make_io_signature (2, 2, sizeof(gr_complex)*vlen)),
  d_vlen(vlen), d_blk(0)
{
  gr_complex one(1.0,0.0);
  d_inv_ctf_estimate.reset(new gr_complex[vlen]);
  d_ctf_estimate.reset(new gr_complex[vlen]);
  for(int i = 0; i < vlen; ++i){
    d_inv_ctf_estimate[i] = one;
    d_ctf_estimate[i] = one;
  }
}

int ofdm_channel_estimator_01::work (
    int noutput_items,
    gr_vector_const_void_star &input_items,
    gr_vector_void_star &output_items)
{
  const gr_complex *blk = static_cast<const gr_complex*>(input_items[0]);
  const char *trigger = static_cast<const char*>(input_items[1]);
  gr_complex *inv_ctf = static_cast<gr_complex*>(output_items[0]);
  gr_complex *ctf = static_cast<gr_complex*>(output_items[1]);

  DEBUG(std::cout << "nout: " << noutput_items << std::endl;)

  for(int i = 0; i < noutput_items; ++i, ++d_blk){
    if(trigger[i] == 1){ // Frame trigger
      d_blk = 0;
      DEBUG(std::cout << "trigger reset" << std::endl;)
    }

    if(d_blk < d_ofdm_frame.size() && d_ofdm_frame[d_blk].known_block){
      DEBUG(std::cout << "known block found" << std::endl;)
      // block is known, calculate inverse ctf and ctf
      boost::shared_array<gr_complex> inv_ctf_estimate, ctf_estimate;
      calculate_equalization(blk+i*d_vlen,d_ofdm_frame[d_blk].block,
                             inv_ctf_estimate, ctf_estimate);

      // Output new CTF vectors
      memcpy(inv_ctf+i*d_vlen,inv_ctf_estimate.get(),sizeof(gr_complex)*d_vlen);
      memcpy(ctf+i*d_vlen,ctf_estimate.get(),sizeof(gr_complex)*d_vlen);

      if(d_ofdm_frame[d_blk].pilot){
        DEBUG(std::cout << "pilot block" << std::endl;)
        // store inverse ctf and ctf for later reuse
        d_inv_ctf_estimate = inv_ctf_estimate;
        d_ctf_estimate = ctf_estimate;
      }

    } else {
      DEBUG(std::cout << "normal block" << std::endl;)
      DEBUG(std::cout << d_inv_ctf_estimate.get() << " " << d_ctf_estimate.get() << std::endl;)
      DEBUG(std::cout << inv_ctf << " " << ctf << std::endl;)

      // The symbol is unknown or we got more symbols in an ofdm block than
      // expected. Output last known CTF vectors
      memcpy(inv_ctf+i*d_vlen,d_inv_ctf_estimate.get(),sizeof(gr_complex)*d_vlen);
      memcpy(ctf+i*d_vlen,d_ctf_estimate.get(),sizeof(gr_complex)*d_vlen);
    }
  }

  return noutput_items;
}

void ofdm_channel_estimator_01::calculate_equalization(
    const gr_complex* blk,
    const boost::shared_array<gr_complex> &known_block,
    boost::shared_array<gr_complex> &inv_ctf,
    boost::shared_array<gr_complex> &ctf)
{
  inv_ctf.reset(new gr_complex[d_vlen]);
  ctf.reset(new gr_complex[d_vlen]);

  for(int i = 0; i < d_vlen; ++i) {
    if(abs(known_block[i]) > 10e-6 && abs(blk[i]) > s_power_threshold) {
      inv_ctf[i] = known_block[i] / blk[i];
      ctf[i] = blk[i] / known_block[i];
    } else {
      // leave unaffected
      inv_ctf[i] = 0.0;
      ctf[i] = 0.0;
    }
  }
}

void ofdm_channel_estimator_01::set_known_block(
  int no,const std::vector<gr_complex> &block, bool pilot)
{
  assert(no >= 0);
  assert(block.size() == static_cast<unsigned>(d_vlen));

  if(d_ofdm_frame.size() <= no){
    d_ofdm_frame.resize(no+1); // TODO: does this delete the content?
  }
  d_ofdm_frame[no].known_block = true;
  d_ofdm_frame[no].pilot = pilot;

  boost::shared_array<gr_complex> vec(new gr_complex[d_vlen]);
  for(int i = 0; i < d_vlen; ++i){
    vec[i] = block[i];
  }

  d_ofdm_frame[no].block = vec;

  d_blk = d_ofdm_frame.size();
}
