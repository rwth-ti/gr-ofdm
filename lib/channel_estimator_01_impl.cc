/* -*- c++ -*- */
/* 
 * Copyright 2014 Institute for Theoretical Information Technology,
 *                RWTH Aachen University
 *                www.ti.rwth-aachen.de
 * 
 * This is free software; you can redistribute it and/or modify
 * it under the terms of the GNU General Public License as published by
 * the Free Software Foundation; either version 3, or (at your option)
 * any later version.
 * 
 * This software is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 * GNU General Public License for more details.
 * 
 * You should have received a copy of the GNU General Public License
 * along with this software; see the file COPYING.  If not, write to
 * the Free Software Foundation, Inc., 51 Franklin Street,
 * Boston, MA 02110-1301, USA.
 */

#ifdef HAVE_CONFIG_H
#include "config.h"
#endif

#include <gnuradio/io_signature.h>
#include "channel_estimator_01_impl.h"

#include <cmath>
#include <iostream>

#include <string.h>

#define DEBUG(x)

namespace gr {
  namespace ofdm {

    static const float s_power_threshold = 10e-3;

    channel_estimator_01::sptr
    channel_estimator_01::make(int vlen)
    {
      return gnuradio::get_initial_sptr
        (new channel_estimator_01_impl(vlen));
    }

    /*
     * The private constructor
     */
    channel_estimator_01_impl::channel_estimator_01_impl(int vlen)
      : gr::sync_block("channel_estimator_01",
              gr::io_signature::make2(2, 2, sizeof(gr_complex)*vlen, sizeof(char)),
              gr::io_signature::make(2, 2, sizeof(gr_complex)*vlen))
    , d_vlen(vlen)
    , d_blk(0)
    {
    	  gr_complex one(1.0,0.0);
    	  d_inv_ctf_estimate.reset(new gr_complex[vlen]);
    	  d_ctf_estimate.reset(new gr_complex[vlen]);
    	  for(int i = 0; i < vlen; ++i){
    	    d_inv_ctf_estimate[i] = one;
    	    d_ctf_estimate[i] = one;
    	  }
    }

    /*
     * Our virtual destructor.
     */
    channel_estimator_01_impl::~channel_estimator_01_impl()
    {
    }

    int
    channel_estimator_01_impl::work(int noutput_items,
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
    void channel_estimator_01_impl::calculate_equalization(
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

    void channel_estimator_01_impl::set_known_block(
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
  } /* namespace ofdm */
} /* namespace gr */

