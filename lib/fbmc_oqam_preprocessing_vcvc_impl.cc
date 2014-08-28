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
#include "fbmc_oqam_preprocessing_vcvc_impl.h"

namespace gr {
  namespace ofdm {

	fbmc_oqam_preprocessing_vcvc::sptr
	fbmc_oqam_preprocessing_vcvc::make(unsigned int M, int offset, int theta_sel)
	{
	  return gnuradio::get_initial_sptr
		(new fbmc_oqam_preprocessing_vcvc_impl(M, offset, theta_sel));
	}

	/*
	 * The private constructor
	 */
	fbmc_oqam_preprocessing_vcvc_impl::fbmc_oqam_preprocessing_vcvc_impl(unsigned int M, int offset, int theta_sel)
	  : gr::sync_interpolator("fbmc_oqam_preprocessing_vcvc",
			  gr::io_signature::make(1, 1, sizeof(gr_complex)*M),
			  gr::io_signature::make(1, 1, sizeof(gr_complex)*M), 2),
		d_M(M),
		d_offset(offset),
		d_theta_sel(theta_sel),
		d_offsets(d_M,offset%2)
	{
		if(d_theta_sel==0){
			vre0[0] = gr_complex(1,0);
			vre0[1] = gr_complex(-1,0);
			vim0[0] = gr_complex(0,1);
			vim0[1] = gr_complex(0,-1);
			vre1[0] = gr_complex(-1,0);
			vre1[1] = gr_complex(1,0);
			vim1[0] = gr_complex(0,-1);
			vim1[1] = gr_complex(0,1);
		}else{
			vre0[0] = gr_complex(1,0);
			vre0[1] = gr_complex(1,0);
			vim0[0] = gr_complex(0,1);
			vim0[1] = gr_complex(0,1);
			vre1[0] = gr_complex(1,0);
			vre1[1] = gr_complex(1,0);
			vim1[0] = gr_complex(0,1);
			vim1[1] = gr_complex(0,1);
		}
	}

	/*
	 * Our virtual destructor.
	 */
	fbmc_oqam_preprocessing_vcvc_impl::~fbmc_oqam_preprocessing_vcvc_impl()
	{
	}

	int
	fbmc_oqam_preprocessing_vcvc_impl::work(int noutput_items,
			  gr_vector_const_void_star &input_items,
			  gr_vector_void_star &output_items)
	{
		const gr_complex *in = (const gr_complex *) input_items[0];
		gr_complex *out = (gr_complex *) output_items[0];

		int ii(0); // input counter
		for(int i=0;i<d_M*noutput_items;i++){
			if(i%4==0){
				out[i] = real(in[ii])*vre0[d_offsets[i%d_M]];
				out[i+d_M] = imag(in[ii])*vim0[(d_offsets[i%d_M])];
				d_offsets[i%d_M]=(d_offsets[i%d_M]+1)%2;
				ii++;
			}
			else if(i%4==1){
				out[i] = imag(in[ii])*vim0[d_offsets[i%d_M]];
				out[i+d_M] = real(in[ii])*vre1[d_offsets[i%d_M]];
				d_offsets[i%d_M]=(d_offsets[i%d_M]+1)%2;
				ii++;
			}
			else if(i%4==2){
				out[i] = real(in[ii])*vre1[d_offsets[i%d_M]];
				out[i+d_M] = imag(in[ii])*vim1[d_offsets[i%d_M]];
				d_offsets[i%d_M]=(d_offsets[i%d_M]+1)%2;
				ii++;
			}
			else{
				out[i] = imag(in[ii])*vim1[d_offsets[i%d_M]];
				out[i+d_M] = real(in[ii])*vre0[d_offsets[i%d_M]];
				d_offsets[i%d_M]=(d_offsets[i%d_M]+1)%2;
				if(i%d_M==(d_M-1)){
					i=i+d_M;
				}
				ii++;
			}
		}

		// Tell runtime system how many output items we produced.
		return noutput_items;
	}

	unsigned int 
	fbmc_oqam_preprocessing_vcvc_impl::get_M(){
	  return d_M;
	}
	void 
	fbmc_oqam_preprocessing_vcvc_impl::set_M(unsigned int new_M){
	  d_M=new_M;
	}
	int 
	fbmc_oqam_preprocessing_vcvc_impl::get_offset(){
	  return d_offset;
	}
	void 
	fbmc_oqam_preprocessing_vcvc_impl::set_offset(int new_offset){
	  d_offset=new_offset;
	}

  } /* namespace ofdm */
} /* namespace gr */

