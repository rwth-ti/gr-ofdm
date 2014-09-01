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
#include "fbmc_oqam_postprocessing_vcvc_impl.h"

namespace gr {
  namespace ofdm {

	fbmc_oqam_postprocessing_vcvc::sptr
	fbmc_oqam_postprocessing_vcvc::make(unsigned int M, int offset, int theta_sel)
	{
	  return gnuradio::get_initial_sptr
		(new fbmc_oqam_postprocessing_vcvc_impl(M, offset, theta_sel));
	}

	/*
	 * The private constructor
	 */
	fbmc_oqam_postprocessing_vcvc_impl::fbmc_oqam_postprocessing_vcvc_impl(unsigned int M, int offset, int theta_sel)
	  : gr::sync_decimator("fbmc_oqam_postprocessing_vcvc",
				gr::io_signature::make(1, 1, sizeof(gr_complex)*M),
				gr::io_signature::make(1, 1, sizeof(gr_complex)*M), 2),
		d_M(M),
		d_offset(offset),
		d_theta_sel(theta_sel),
		d_tc(M,0)
	{
		if (d_theta_sel==0){
			for(int i=0;i<4;i++){
				for(int j=0;j<4;j++){
					thetas[i][j] = pow(gr_complex(0,-1),i+j);
				}
			}
		}else{
			for(int i=0;i<4;i++){
				for(int j=0;j<4;j++){
					if((j+i)%2==0){
						thetas[i][j] = 1;
					}else{
						thetas[i][j] = gr_complex(0,-1);
					}
					
				}
			}
		}
	}

	/*
	 * Our virtual destructor.
	 */
	fbmc_oqam_postprocessing_vcvc_impl::~fbmc_oqam_postprocessing_vcvc_impl()
	{
	}

	int
	fbmc_oqam_postprocessing_vcvc_impl::work(int noutput_items,
			  gr_vector_const_void_star &input_items,
			  gr_vector_void_star &output_items)
	{
		const gr_complex *in = (const gr_complex *) input_items[0];
		gr_complex *out = (gr_complex *) output_items[0];

		// Do <+signal processing+>
		gr_complex *buf = new gr_complex[d_M];
		int bi(0); //buffer counter
		int oo(0);
		gr_complex theta = gr_complex(0,0);
		// for(int i=0;i<300;i++){
		//  std::cout<<i<<":\t"<<in[i]<<std::endl;
		// }
		for(int i=0;i<noutput_items*d_M*2;i++){
			// out[i] = in[i-1];//+(gr_complex)in[i-d_M+1]*gr_complex(0,1);
			// std::cout<<i<<":\t";
			if((((int)(floor(i/d_M)))%2)==0){
				// first part of the oqam sample. we should apply theta
				// multiplier take the real part and store the value,
				if(i%2==0){
					buf[bi++] = real(in[i]*thetas[i%4][(d_tc[i%d_M]++)%4]);
				}else{
					buf[bi++] = real(in[i]*thetas[i%4][(d_tc[i%d_M]++)%4])*gr_complex(0,1);
				}       
				// std::cout<<in[i+40]<<std::endl;
				if(bi==d_M){
					bi = 0; //reset buffer counter
				}
			}else{
				// second part of the oqam sample. we should apply theta
				// multiplier, take the real part, sum and output.
				if(i%2==0){
					out[oo] = real(in[i]*thetas[i%4][(d_tc[i%d_M]++)%4])*gr_complex(0,1)+buf[bi++];
				}else{
					out[oo] = real(in[i]*thetas[i%4][(d_tc[i%d_M]++)%4])+buf[bi++];
				}
				// std::cout<<in[i]<<std::endl;
				oo++;
				if(bi==d_M){
					bi = 0; //reset buffer counter
				}
			}

		}

		// Tell runtime system how many output items we produced.
		return noutput_items;
	}

  } /* namespace ofdm */
} /* namespace gr */

