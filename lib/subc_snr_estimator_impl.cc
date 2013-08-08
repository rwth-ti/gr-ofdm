/* -*- c++ -*- */
/* 
 * Copyright 2013 <+YOU OR YOUR COMPANY+>.
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
#include "subc_snr_estimator_impl.h"

namespace gr {
  namespace ofdm {

    subc_snr_estimator::sptr
    subc_snr_estimator::make(int vlen)
    {
      return gnuradio::get_initial_sptr
        (new subc_snr_estimator_impl(vlen));
    }

    /*
     * The private constructor
     */
    subc_snr_estimator_impl::subc_snr_estimator_impl(int vlen)
      : gr::sync_block("subc_snr_estimator",
              gr::io_signature::make(1, 1, sizeof(gr_complex)*vlen),
              gr::io_signature::make(1, 1, sizeof(float)))
    	, d_vlen(vlen)
    {}

    /*
     * Our virtual destructor.
     */
    subc_snr_estimator_impl::~subc_snr_estimator_impl()
    {
    }

    int
    subc_snr_estimator_impl::work(int noutput_items,
			  gr_vector_const_void_star &input_items,
			  gr_vector_void_star &output_items)
    {
    	const gr_complex *in = static_cast<const gr_complex*>(input_items[0]);
    	  float *out = static_cast<float*>(output_items[0]);

    	  const int N = d_vlen/2;

    	  for(int i = 0; i < noutput_items; ++i, in+=d_vlen){

    	    // compute correlation between first half and second half
    	    gr_complexd p(0.0,0.0);
    	//    p = recursive_p_sum(in,d_vlen,N);
    	//    double r = recursive_r_sum(in,d_vlen);
    	    double r = 0.0;
    	    for(int k = 0; k < N; ++k){
    	      p += std::conj(in[k])*in[k+N];
    	      r += in[k].real()*in[k].real()+in[k].imag()*in[k].imag()
    	           +in[k+N].real()*in[k+N].real()+in[k+N].imag()*in[k+N].imag();
    	    }

    	    double p_mag = std::abs(p);
    	//    double diff = r - p_mag;
    	    double m = p_mag/(r*0.5);

    	//    if(diff < 0.0){
    	//      // uh maybe simulation?
    	//      diff = 1e-6;
    	//    }
    	    double m_lim = std::max(1.-(2e-5),std::min(-1000.,m));
    	//    double snr_est = p_mag/diff;
    	    double snr_est = m / (1 - m_lim);

    	    // numerically unstable, avoid large absolute values
    	    double snr_lim = std::max(0.1, std::min(1000000.0, snr_est));

    	    out[i] = (float)snr_lim;
    	//    std::cout << "[SNR] " << p_mag << " " << r << " "  << snr_est << " -- " << snr_lim << std::endl;
    	//    std::cout << "[SNR] " << p_mag << " " << r << " " << diff << " "  << snr_est << " -- " << snr_lim << std::endl;

    	  }

    	  return noutput_items;
    }

  } /* namespace ofdm */
} /* namespace gr */

