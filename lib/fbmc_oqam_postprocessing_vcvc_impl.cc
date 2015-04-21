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
#include "malloc16.h"
#include <volk/volk.h>

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
		d_tracker(0),
		d_theta_sel(theta_sel),
		d_ones(M,gr_complex(1,0)),
		d_twos(M,gr_complex(0,1)),
		d_buf( static_cast< gr_complex * >( malloc16Align( sizeof( gr_complex ) *M ) ) ),
		d_help2( static_cast< gr_complex * >( malloc16Align( sizeof( gr_complex ) *M ) ) ),
		d_help3( static_cast< float* >( malloc16Align( sizeof( float ) *M ) ) ),
		d_help7( static_cast< gr_complex * >( malloc16Align( sizeof( gr_complex ) *M ) ) ),
		d_help8( static_cast< gr_complex * >( malloc16Align( sizeof( gr_complex ) *M ) ) ),
		d_buf_i( static_cast< float* >( malloc16Align( sizeof( float ) *M ) ) ),
		d_buf_q( static_cast< float* >( malloc16Align( sizeof( float ) *M ) ) ),
		d_help7_i( static_cast< float* >( malloc16Align( sizeof( float ) *M ) ) ),
		d_help7_q( static_cast< float* >( malloc16Align( sizeof( float ) *M ) ) ),
		d_help8_i( static_cast< float* >( malloc16Align( sizeof( float ) *M ) ) ),
		d_help8_q( static_cast< float* >( malloc16Align( sizeof( float ) *M ) ) ),
		d_tc(M,0)
	{
	      const int alignment_multiple = volk_get_alignment() / sizeof(gr_complex);
	      set_alignment(std::max(1, alignment_multiple));

	     for (int i = 0; i< M/2;i++)
	    	  {
	    	  d_ones[2*i+1]=gr_complex(0,1);
	    	  d_twos[2*i+1]=gr_complex(1,0);
	      	  //std::cout<<d_ones[i]<<std::endl;
	    	  }
		//Resize Thetas
		thetas.resize(4);
		for (int i = 0; i < 4; ++i)
		    thetas[i].resize(d_M);


		if (d_theta_sel==0){
			for(int i=0;i<4;i++){
				for(int j=0;j<d_M;j++){
					thetas[i][j] = pow(gr_complex(0,-1),i+j);
				}
			}
		}else{
			for(int i=0;i<4;i++){
				for(int j=0;j<d_M;j++){
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
		if( d_buf )
		    	    free16Align( d_buf );
		if( d_buf_i )
				    free16Align( d_buf_i );
		if( d_buf_q )
				    free16Align( d_buf_q );
		if( d_help2 )
				   	free16Align( d_help2 );
		if( d_help3 )
		    	    free16Align( d_help3 );
		if( d_help7 )
				   	free16Align( d_help7 );
		if( d_help7_i )
					free16Align( d_help7_i );
		if( d_help7_q )
					free16Align( d_help7_q );
		if( d_help8 )
		    	    free16Align( d_help8 );
		if( d_help8_i )
					free16Align( d_help8_i );
		if( d_help8_q )
					free16Align( d_help8_q );
	}

	int
	fbmc_oqam_postprocessing_vcvc_impl::work(int noutput_items,
			  gr_vector_const_void_star &input_items,
			  gr_vector_void_star &output_items)
	{
		const gr_complex *in = (const gr_complex *) input_items[0];
		gr_complex *out = (gr_complex *) output_items[0];

		// Do <+signal processing+>
		//gr_complex *buf = new gr_complex[d_M];
		//std::vector<gr_complex>  help1(d_M,gr_complex(1,0));// = new std::vector<gr_complex>;
		//gr_complex *help2 = new gr_complex[d_M];
		//float *help3 = new float[d_M];
		//std::vector<gr_complex>  help4(d_M,gr_complex(1,0));// = new std::vector<gr_complex>;
		//gr_complex *help5 = new gr_complex [d_M];
		//float *help6 = new float[d_M];
		//gr_complex *help7 = new gr_complex[d_M];
		//gr_complex *help8 = new gr_complex[d_M];
		//float *buf_i = new float[d_M];
		//float *buf_q = new float[d_M];
		//float *help7_i = new float[d_M];
		//float *help7_q = new float[d_M];
		//float *help8_i = new float[d_M];
		//float *help8_q = new float[d_M];

		//int bi(0); //buffer counter
		//int oo(0);
		//gr_complex theta = gr_complex(0,0);
		// for(int i=0;i<300;i++){
		//  std::cout<<i<<":\t"<<in[i]<<std::endl;
		// }
		/*for(int i=0;i<noutput_items*d_M*2;i++){
			// out[i] = in[i-1];//+(gr_complex)in[i-d_M+1]*gr_complex(0,1);
			// std::cout<<i<<":\t";
			if((((int)(floor(i/d_M)))%2)==0){
				// first part of the oqam sample. we should apply theta
				// multiplier take the real part and store the value,
				if(i%2==0){
					//std::cout<<d_tc[i]<<std::endl;
					buf[bi++] = real(in[i]*thetas[i%4][(d_tc[i%d_M]++)%4]);
					//buf[bi++] = real(in[i]*thetas[i%4][0]);
				}else{
					buf[bi++] = real(in[i]*thetas[i%4][(d_tc[i%d_M]++)%4])*gr_complex(0,1);
					//buf[bi++] = real(in[i]*thetas[i%4][0])*gr_complex(0,1);
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

		}*/

/*		std::cout<<noutput_items<<std::endl;
		if (((noutput_items*2)%4)==0)
						d_tracker = 0;
				else
					d_tracker = 2*/;
					//std::cout<<noutput_items<<std::endl;
					//if (d_tracker%4==0)
							//		d_tracker = 0;
					//std::cout<<d_tracker<<std::endl;

					//d_tracker = (((noutput_items)*2)%4);
					//std::cout<<d_tracker<<std::endl;
		for(int i=0;i<noutput_items*2;i++){
					// out[i] = in[i-1];//+(gr_complex)in[i-d_M+1]*gr_complex(0,1);
					// std::cout<<i<<":\t";
/*					if((((int)(floor(i/d_M)))%2)==0){
						// first part of the oqam sample. we should apply theta
						// multiplier take the real part and store the value,
						if(i%2==0){
							//std::cout<<d_tc[i]<<std::endl;
							buf[bi++] = real(in[i]*thetas[i%4][(d_tc[i%d_M]++)%4]);
							//buf[bi++] = real(in[i]*thetas[i%4][0]);
						}else{
							buf[bi++] = real(in[i]*thetas[i%4][(d_tc[i%d_M]++)%4])*gr_complex(0,1);
							//buf[bi++] = real(in[i]*thetas[i%4][0])*gr_complex(0,1);
						}
						// std::cout<<in[i+40]<<std::endl;
						if(bi==d_M){
							bi = 0; //reset buffer counter
						}
					}*/
			if(i%2==0){
					//d_help1 = thetas[(d_tracker++)%4];
					volk_32fc_x2_multiply_32fc(&d_help2[0],&in[i*d_M],&thetas[(d_tracker++)%4][0],d_M);
					volk_32fc_deinterleave_real_32f(&d_help3[0],&d_help2[0],d_M);
					volk_32fc_32f_multiply_32fc(&d_buf[0],&d_ones[0],&d_help3[0],d_M);



			}
			else
			{
/*				help4 = thetas[(d_tracker++)%4];
				volk_32fc_x2_multiply_32fc(&help5[0],&in[(i)*d_M],&help4[0],d_M);
				volk_32fc_deinterleave_real_32f(&help6[0],&help5[0],d_M);
				volk_32fc_32f_multiply_32fc(&help7[0],&d_twos[0],&help6[0],d_M);

				volk_32fc_deinterleave_32f_x2(&buf_i[0],&buf_q[0],&buf[0],d_M);
				volk_32fc_deinterleave_32f_x2(&help7_i[0],&help7_q[0],&help7[0],d_M);

				volk_32f_x2_add_32f(&help8_i[0],&buf_i[0],&help7_i[0],d_M);
				volk_32f_x2_add_32f(&help8_q[0],&buf_q[0],&help7_q[0],d_M);

				volk_32f_x2_interleave_32fc(&out[int((i-1)/2)*d_M],&help8_i[0],&help8_q[0],d_M);*/

				//help1 = thetas[(d_tracker++)%4];
				volk_32fc_x2_multiply_32fc(&d_help2[0],&in[(i)*d_M],&thetas[(d_tracker++)%4][0],d_M);
				volk_32fc_deinterleave_real_32f(&d_help3[0],&d_help2[0],d_M);
				volk_32fc_32f_multiply_32fc(&d_help7[0],&d_twos[0],&d_help3[0],d_M);

				volk_32fc_deinterleave_32f_x2(&d_buf_i[0],&d_buf_q[0],&d_buf[0],d_M);
				volk_32fc_deinterleave_32f_x2(&d_help7_i[0],&d_help7_q[0],&d_help7[0],d_M);

				volk_32f_x2_add_32f(&d_help8_i[0],&d_buf_i[0],&d_help7_i[0],d_M);
				volk_32f_x2_add_32f(&d_help8_q[0],&d_buf_q[0],&d_help7_q[0],d_M);

				volk_32f_x2_interleave_32fc(&out[int((i-1)/2)*d_M],&d_help8_i[0],&d_help8_q[0],d_M);
				//volk_32f_x2_interleave_32fc(&out[int((i)/2)*d_M],&help8_i[0],&help8_q[0],d_M);
			}


/*					else{
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
					}*/

				}
		//d_tracker = ((noutput_items*2)%4);
		// Tell runtime system how many output items we produced.
		return noutput_items;
	}

  } /* namespace ofdm */
} /* namespace gr */

