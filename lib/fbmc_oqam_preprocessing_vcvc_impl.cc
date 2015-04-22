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
#include "malloc16.h"
#include <volk/volk.h>

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
		d_offsets(d_M,offset%2),
		d_tracker(0),
		d_v1_re(M,0.0),
		d_v1_im(M,0.0),
		d_v2_re(M,0.0),
		d_v2_im(M,0.0),
		d_v3_re(M,0.0),
		d_v3_im(M,0.0),
		d_v4_re(M,0.0),
		d_v4_im(M,0.0),
		xreal( static_cast< float* >( malloc16Align( sizeof( float ) *M ) ) ),
		ximag( static_cast< float* >( malloc16Align( sizeof( float ) *M ) ) ),
		sum1_i( static_cast< float* >( malloc16Align( sizeof( float ) *M ) ) ),
		sum1_q( static_cast< float* >( malloc16Align( sizeof( float ) *M ) ) ),
		sum2_i( static_cast< float* >( malloc16Align( sizeof( float ) *M ) ) ),
		sum2_q( static_cast< float* >( malloc16Align( sizeof( float ) *M ) ) ),
		sum3_i( static_cast< float* >( malloc16Align( sizeof( float ) *M ) ) ),
		sum3_q( static_cast< float* >( malloc16Align( sizeof( float ) *M ) ) ),
		sum4_i( static_cast< float* >( malloc16Align( sizeof( float ) *M ) ) ),
		sum4_q( static_cast< float* >( malloc16Align( sizeof( float ) *M ) ) ),
		sumc_i( static_cast< float* >( malloc16Align( sizeof( float ) *M ) ) ),
		sumc_q( static_cast< float* >( malloc16Align( sizeof( float ) *M ) ) ),
		sumcc_i( static_cast< float* >( malloc16Align( sizeof( float ) *M ) ) ),
		sumcc_q( static_cast< float* >( malloc16Align( sizeof( float ) *M ) ) ),
		sum1( static_cast< gr_complex * >( malloc16Align( sizeof( gr_complex ) *M ) ) ),
		sum2( static_cast< gr_complex * >( malloc16Align( sizeof( gr_complex ) *M ) ) ),
		sum3( static_cast< gr_complex * >( malloc16Align( sizeof( gr_complex ) *M ) ) ),
		sum4( static_cast< gr_complex * >( malloc16Align( sizeof( gr_complex ) *M ) ) ),
		sumc( static_cast< gr_complex * >( malloc16Align( sizeof( gr_complex ) *M ) ) ),
		sumcc( static_cast< gr_complex * >( malloc16Align( sizeof( gr_complex ) *M ) ) )
	{
	      const int alignment_multiple = volk_get_alignment() / sizeof(gr_complex);
	      set_alignment(std::max(1, alignment_multiple));
		/*if(d_theta_sel==0){
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
		}*/

	     for (int i = 0; i< M/4;i++)
	    	  {
	    	  d_v1_re[4*i] = gr_complex(1,0);
	    	  d_v1_re[4*i+2] = gr_complex(-1,0);

	    	  d_v1_im[4*i+1] = gr_complex(0,1);
	    	  d_v1_im[4*i+3 ]= gr_complex(0,-1);

	    	  d_v2_im[4*i] = gr_complex(0,1);;
	    	  d_v2_im[4*i+2]= gr_complex(0,-1);

	       	  d_v2_re[4*i+1] = gr_complex(-1,0);
	    	  d_v2_re[4*i+3 ]= gr_complex(1,0);

	    	  d_v3_re[4*i] = gr_complex(-1,0);
	    	  d_v3_re[4*i+2] = gr_complex(1,0);

	    	  d_v3_im[4*i+1] = gr_complex(0,-1);
	    	  d_v3_im[4*i+3 ]= gr_complex(0,1);

	    	  d_v4_im[4*i] = gr_complex(0,-1);;
	    	  d_v4_im[4*i+2]= gr_complex(0,1);

	       	  d_v4_re[4*i+1] = gr_complex(1,0);
	    	  d_v4_re[4*i+3 ]= gr_complex(-1,0);
	      	  //std::cout<<d_ones[i]<<std::endl;
	    	  }

/*	     for (int i = 0; i< M;i++)
	    	  {
	      	  std::cout<<d_v4_im[i]<<std::endl;
	    	  }*/
	}

	/*
	 * Our virtual destructor.
	 */
	fbmc_oqam_preprocessing_vcvc_impl::~fbmc_oqam_preprocessing_vcvc_impl()
	{
		if( xreal )
		    	    free16Align( xreal );
		if( ximag )
		    	    free16Align( ximag );
		if( sum1_i)
		    	    free16Align( sum1_i );
		if( sum1_q )
		    	    free16Align( sum1_q );
		if( sum2_i)
		    	    free16Align( sum2_i );
		if( sum2_q )
		    	    free16Align( sum2_q );
		if( sum3_i)
		    	    free16Align( sum3_i );
		if( sum3_q )
		    	    free16Align( sum3_q );
		if( sum4_i)
		    	    free16Align( sum4_i );
		if( sum4_q )
		    	    free16Align( sum4_q );
		if( sumc_i)
		    	    free16Align( sumc_i );
		if( sumc_q )
		    	    free16Align( sumc_q );
		if( sumcc_i)
		    	    free16Align( sumcc_i );
		if( sumcc_q )
		    	    free16Align( sumcc_q );
		if( sum1 )
				    	    free16Align( sum1 );
		if( sum2)
				    	    free16Align( sum2 );
		if( sum3 )
				    	    free16Align( sum3 );
		if( sum4)
				    	    free16Align( sum4 );
		if( sumc )
				    	    free16Align( sumc );
		if( sumcc )
				    	    free16Align( sumcc );
		if( sumcc)
				    	    free16Align( sumcc );
	}

	int
	fbmc_oqam_preprocessing_vcvc_impl::work(int noutput_items,
			  gr_vector_const_void_star &input_items,
			  gr_vector_void_star &output_items)
	{
		const gr_complex *in = (const gr_complex *) input_items[0];
		gr_complex *out = (gr_complex *) output_items[0];

/*		float *xreal = new float[d_M];
		float *ximag = new float[d_M];
		gr_complex *sum1 = new gr_complex[d_M];
		gr_complex *sum2 = new gr_complex[d_M];
		gr_complex *sum3 = new gr_complex[d_M];
		gr_complex *sum4 = new gr_complex[d_M];
		gr_complex *sumc = new gr_complex[d_M];
		gr_complex *sumcc = new gr_complex[d_M];
		float *sum1_i = new float[d_M];
		float *sum1_q= new float[d_M];
		float *sum2_i = new float[d_M];
		float *sum2_q= new float[d_M];
		float *sum3_i = new float[d_M];
		float *sum3_q= new float[d_M];
		float *sum4_i = new float[d_M];
		float *sum4_q= new float[d_M];
		float *sumc_i = new float[d_M];
		float *sumc_q= new float[d_M];
		float *sumcc_i = new float[d_M];
		float *sumcc_q= new float[d_M];*/

/*		int ii(0); // input counter

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
		}*/
		//int ii(0); // input counter
		d_tracker = d_tracker%2;
		for(int i=0;i<noutput_items/2;i++){
			volk_32fc_deinterleave_real_32f(&xreal[0],&in[i*d_M],d_M);
			volk_32fc_deinterleave_imag_32f(&ximag[0],&in[i*d_M],d_M);

			if(d_tracker%2==0){
				volk_32fc_32f_multiply_32fc(&sum1[0],&d_v1_re[0],&xreal[0],d_M);
				volk_32fc_32f_multiply_32fc(&sum2[0],&d_v1_im[0],&ximag[0],d_M);

				volk_32fc_deinterleave_32f_x2(&sum1_i[0],&sum1_q[0],&sum1[0],d_M);
				volk_32fc_deinterleave_32f_x2(&sum2_i[0],&sum2_q[0],&sum2[0],d_M);

				volk_32f_x2_add_32f(&sumc_i[0],&sum1_i[0],&sum2_i[0],d_M);
				volk_32f_x2_add_32f(&sumc_q[0],&sum1_q[0],&sum2_q[0],d_M);

				volk_32f_x2_interleave_32fc(&out[2*i*d_M],&sumc_i[0],&sumc_q[0],d_M);

				volk_32fc_32f_multiply_32fc(&sum3[0],&d_v2_im[0],&ximag[0],d_M);
				volk_32fc_32f_multiply_32fc(&sum4[0],&d_v2_re[0],&xreal[0],d_M);

				volk_32fc_deinterleave_32f_x2(&sum3_i[0],&sum3_q[0],&sum3[0],d_M);
				volk_32fc_deinterleave_32f_x2(&sum4_i[0],&sum4_q[0],&sum4[0],d_M);

				volk_32f_x2_add_32f(&sumcc_i[0],&sum3_i[0],&sum4_i[0],d_M);
				volk_32f_x2_add_32f(&sumcc_q[0],&sum3_q[0],&sum4_q[0],d_M);

				volk_32f_x2_interleave_32fc(&out[(2*i+1)*d_M],&sumcc_i[0],&sumcc_q[0],d_M);
				d_tracker++;
				//i++;
				//ii++;
			}


			else {
				volk_32fc_32f_multiply_32fc(&sum1[0],&d_v3_re[0],&xreal[0],d_M);
				volk_32fc_32f_multiply_32fc(&sum2[0],&d_v3_im[0],&ximag[0],d_M);

				volk_32fc_deinterleave_32f_x2(&sum1_i[0],&sum1_q[0],&sum1[0],d_M);
				volk_32fc_deinterleave_32f_x2(&sum2_i[0],&sum2_q[0],&sum2[0],d_M);

				volk_32f_x2_add_32f(&sumc_i[0],&sum1_i[0],&sum2_i[0],d_M);
				volk_32f_x2_add_32f(&sumc_q[0],&sum1_q[0],&sum2_q[0],d_M);

				volk_32f_x2_interleave_32fc(&out[2*i*d_M],&sumc_i[0],&sumc_q[0],d_M);

				volk_32fc_32f_multiply_32fc(&sum3[0],&d_v4_im[0],&ximag[0],d_M);
				volk_32fc_32f_multiply_32fc(&sum4[0],&d_v4_re[0],&xreal[0],d_M);

				volk_32fc_deinterleave_32f_x2(&sum3_i[0],&sum3_q[0],&sum3[0],d_M);
				volk_32fc_deinterleave_32f_x2(&sum4_i[0],&sum4_q[0],&sum4[0],d_M);

				volk_32f_x2_add_32f(&sumcc_i[0],&sum3_i[0],&sum4_i[0],d_M);
				volk_32f_x2_add_32f(&sumcc_q[0],&sum3_q[0],&sum4_q[0],d_M);

				volk_32f_x2_interleave_32fc(&out[(2*i+1)*d_M],&sumcc_i[0],&sumcc_q[0],d_M);
				d_tracker++;
				//i++;

				//ii++;
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

