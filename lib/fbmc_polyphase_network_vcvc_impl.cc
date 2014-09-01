/* -*- c++ -*- */
/* 
 * Copyright 2014 <+YOU OR YOUR COMPANY+>.
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
#include "fbmc_polyphase_network_vcvc_impl.h"

namespace gr {
  namespace ofdm {

	fbmc_polyphase_network_vcvc::sptr
	fbmc_polyphase_network_vcvc::make(unsigned int M, unsigned int K, unsigned int lp, bool reverse)
	{
	  return gnuradio::get_initial_sptr
		(new fbmc_polyphase_network_vcvc_impl(M, K, lp, reverse));
	}

	/*
	 * The private constructor
	 */
	fbmc_polyphase_network_vcvc_impl::fbmc_polyphase_network_vcvc_impl(unsigned int M, unsigned int K, unsigned int lp, bool reverse)
	  : gr::sync_block("fbmc_polyphase_network_vcvc",
		gr::io_signature::make(1, 1, sizeof(gr_complex)*M),
		gr::io_signature::make(1, 1, sizeof(gr_complex)*M)),
	d_M(M),
	d_K(K),
	d_lp(M*K-1), //for now only filters of length KM-1 are supported
	d_reverse(reverse)
	{ 
		assert(M>0 && log(M)/log(2) = (int)(log(M)/log(2)));
		assert(K==2 || K==3 || K==4);
		d_taps = new float[d_lp+1];
		createTaps(d_M,d_K,d_lp,d_reverse,&d_taps[0]);
		set_history(K);
		tapdata.open ("../../matlab/taps.txt",std::ios::out);
		// tapdata<<"M="<<d_M<<"\n";
		// tapdata<<"syms_per_frame="<<d_syms_per_frame<<"\n";
		// tapdata<<"sel_eq="<<d_sel_eq<<"\n";
	}

	/*
	 * Our virtual destructor.
	 */
	fbmc_polyphase_network_vcvc_impl::~fbmc_polyphase_network_vcvc_impl()
	{
	  tapdata.close();
	}

	void
	fbmc_polyphase_network_vcvc_impl::createTaps(unsigned int M, unsigned int K, unsigned int lp, bool reverse, float* taps)
	{
	  // coefficients
	  float **P = new float*[3];
	  float P0[]={1, sqrt(2)/2}; //K=2
	  float P1[]={1,0.911438,0.411438}; //K=3
	  float P2[]={1,0.97195983,sqrt(2)/2,0.23514695}; //K=4
	  P[0] = P0;
	  P[1] = P1;
	  P[2] = P2;

	  float denom = P[K-2][0];
	  for(int i=1;i<K;i++){
		denom = denom + 2*P[K-2][i];
	  }
	  
	  taps[0] = 0; //delay
	  tapdata<<0<<"\t";
	  for(int m=0;m<lp;m++){
		float summed = P[K-2][0];
		for(int k=1;k<K;k++){
		  summed = summed + 2* pow(-1,k) * (P[K-2][k]) * cos(2*M_PI*k*(m+1)/(K*M));
		}
		taps[m+1] = summed/denom;
		// std::cout<<m<<"\t"<<taps[m+1]<<"\n";
		// tapdata<<summed/denom<<"\t";
	  }
	  tapdata<<"\n";


	  //if analysis filter, swap the 
	  if(reverse){
		float temp;
		for(int i=0;i<d_K;i++){
		  for(int j=0;j<d_M/2;j++){
			temp = taps[i*d_M+j];
			taps[i*d_M+j] = taps[(i+1)*d_M-1-j];
			taps[(i+1)*d_M-1-j] = temp;
			// std::cout<<i*d_M+j<<"\t"<<(i+1)*d_M-1-j<<std::endl;
		  }
		}
	  }
	}

	int
	fbmc_polyphase_network_vcvc_impl::work(int noutput_items,
			  gr_vector_const_void_star &input_items,
			  gr_vector_void_star &output_items)
	{
	  const gr_complex *in = (const gr_complex *) input_items[0];
	  gr_complex *out = (gr_complex *) output_items[0];

	  // Do <+signal processing+>
	  for(int i=0;i<noutput_items*d_M;i++){
		// note: following expression is valid only when K=4. For other K values, one should employ
		// a for loop from 0 to K-1 and sum values. I did not, so as to avoid unnecessary calculations (iteration of the index etc.)
		out[i] =in[i+(d_K-1)*d_M]*d_taps[(i%d_M)]+in[i+(d_K-1)*d_M-d_M]*d_taps[(i%d_M)+d_M]+in[i+(d_K-1)*d_M-2*d_M]*d_taps[(i%d_M)+2*d_M]+in[i+(d_K-1)*d_M-3*d_M]*d_taps[(i%d_M)+3*d_M];
	  }
	  // Tell runtime system how many output items we produced.
	  return noutput_items;
	}

  } /* namespace ofdm */
} /* namespace gr */

