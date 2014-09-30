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
#include "fbmc_subchannel_processing_vcvc_impl.h"
#include <volk/volk.h>

namespace gr {
	namespace ofdm {

		fbmc_subchannel_processing_vcvc::sptr
		fbmc_subchannel_processing_vcvc::make(unsigned int M, unsigned int syms_per_frame, int sel_preamble, int zero_pads, bool extra_pad, int sel_eq)
		{
			return gnuradio::get_initial_sptr
				(new fbmc_subchannel_processing_vcvc_impl(M, syms_per_frame, sel_preamble, zero_pads, extra_pad, sel_eq));
		}

		/*
		 * The private constructor
		 */
		fbmc_subchannel_processing_vcvc_impl::fbmc_subchannel_processing_vcvc_impl(unsigned int M, unsigned int syms_per_frame, int sel_preamble, int zero_pads, bool extra_pad, int sel_eq)
			: gr::sync_block("fbmc_subchannel_processing_vcvc",
				gr::io_signature::make(1, 1, sizeof(gr_complex)*M),
				gr::io_signature::make(2, 2, sizeof(gr_complex)*M)),
		d_M(M),
		d_syms_per_frame(syms_per_frame),
		d_preamble(),
		d_sel_eq(sel_eq),
		d_sel_preamble(sel_preamble),
		d_estimation(M,1),
		d_eq_coef(3*d_M,1),
		ii(0),
		fr(0),
		// ,
		normalization_factor(1),
		// d_zero_v(M,0),
		// d_center
		d_zero_pads(zero_pads),
		d_extra_pad(extra_pad)
		{
			if(d_sel_eq==1 || d_sel_eq==2){ //three taps
				set_history(3);
			}

			//prepare preamble
			//prepare center
			if(d_sel_preamble == 0){ // standard one vector center preamble [1,-j,-1,j]
				normalization_factor = 1;
				std::vector<gr_complex> dummy;
				dummy.push_back(gr_complex(1,0));
				dummy.push_back(gr_complex(0,-1));
				dummy.push_back(gr_complex(-1,0));
				dummy.push_back(gr_complex(0,1));				
				for(int i=0;i<(int)(d_M/4);i++){
					d_preamble.insert(d_preamble.end(), dummy.begin(), dummy.end());
				}
				d_preamble_length = d_M*(1+2*d_zero_pads);
				if(d_extra_pad){
					d_preamble_length+=d_M;
				}
			}else if(d_sel_preamble == 1){ // standard preamble with triple repetition
				// normalization_factor = 1;
				normalization_factor = 2.128;
				std::vector<gr_complex> dummy;
				dummy.push_back(gr_complex(1,0));
				dummy.push_back(gr_complex(0,-1));
				dummy.push_back(gr_complex(-1,0));
				dummy.push_back(gr_complex(0,1));				
				for(int i=0;i<(int)(d_M/4);i++){
					d_preamble.insert(d_preamble.end(), dummy.begin(), dummy.end());
				}
				d_preamble_length = d_M*(3+2*d_zero_pads);
				if(d_extra_pad){
					d_preamble_length+=d_M;
				}
			}else if(d_sel_preamble == 2){ // IAM-R preamble [1, -1,-1, 1]
				normalization_factor = 1;
				std::vector<gr_complex> dummy;
				dummy.push_back(gr_complex(1,0));
				dummy.push_back(gr_complex(-1,0));
				dummy.push_back(gr_complex(-1,0));
				dummy.push_back(gr_complex(1,0));
				
				for(int i=0;i<(int)(d_M/4);i++){
					d_preamble.insert(d_preamble.end(), dummy.begin(), dummy.end());
				}
				d_preamble_length = d_M*(1+2*d_zero_pads);
				if(d_extra_pad){
					d_preamble_length+=d_M;
				}
			}else{ // standard one vector center preamble [1,-j,-1,j]
				normalization_factor = 1;
				std::vector<gr_complex> dummy;
				dummy.push_back(gr_complex(0,1));
				dummy.push_back(gr_complex(-1,0));
				dummy.push_back(gr_complex(0,-1));
				dummy.push_back(gr_complex(1,0));
				
				for(int i=0;i<(int)(d_M/4);i++){
					d_preamble.insert(d_preamble.end(), dummy.begin(), dummy.end());
				}
				d_preamble_length = d_M*(1+2*d_zero_pads);
				if(d_extra_pad){
					d_preamble_length+=d_M;
				}
			}

			d_frame_length=d_preamble_length+2*syms_per_frame*d_M;
			estimation_point=(((int(d_preamble_length/d_M)-1)/2)+1)*d_M-1;
			// if(extra_pad){
			// 	estimation_point = estimation_point;
			// }

			// equalizer_data.open ("../../matlab/sp_equ_cpp_output.txt",std::ios::out); //|std::ios::app
			// estimation_data.open("../../matlab/sp_est_cpp_output.txt",std::ios::out);
			
			// equalizer_data<<"M="<<d_M<<"\n";
			// equalizer_data<<"syms_per_frame="<<d_syms_per_frame<<"\n";
			// equalizer_data<<"sel_eq="<<d_sel_eq<<"\n";
			// equalizer_data<<"preamble_length="<<d_preamble_length<<"\n";

			// estimation_data<<"M="<<d_M<<"\n";
			// estimation_data<<"syms_per_frame="<<d_syms_per_frame<<"\n";
			// estimation_data<<"sel_eq="<<d_sel_eq<<"\n";
			// estimation_data<<"preamble_length="<<d_preamble_length<<"\n";
			// estimation_data<<"estimation_point="<<estimation_point<<"\n";
			// // equalizer_data<<"estimation="<<d_estimation<<"\n";
			// // std::cout<<preamble.size()<<std::endl;
			// // for(int i=0;i<3*d_M;i++) std::cout<<d_eq_coef[i]<<std::endl;
			// for(int i=0;i<d_M;i++) std::cout<<i<<"\t"<<d_preamble[i]<<std::endl;

		}

		/*
		 * Our virtual destructor.
		 */
		fbmc_subchannel_processing_vcvc_impl::~fbmc_subchannel_processing_vcvc_impl()
		{
			// equalizer_data.close();
			// estimation_data.close();
		}

		void 
		fbmc_subchannel_processing_vcvc_impl::get_estimation(const gr_complex * start)
		{
			// int offset = estimation_point - d_M+1;
			for(int i=0;i<d_M;i++){
				d_estimation[i] = *(start-d_M+i+1)/(d_preamble[i]*normalization_factor);//*gr_complex(0.6863,0));
				// // *(start-d_M+i+1) = d_estimation[i];
				// //logging
				// estimation_data<<"fr "<<fr<<"\t"<<i<<"\t"<<*(start-d_M+i+1)<<"\t"<<(d_preamble[i+d_M])<<"\t"<<d_estimation[i]<<"\t"<<((abs(d_estimation[i])-abs(*(start-d_M+i+1)))>0?"TR":"FA")<<"\n";
				
			}

			// // equalizer_data<<"----------------------------------"<<"\n";
			fr++;		
		}

		void 
		fbmc_subchannel_processing_vcvc_impl::get_equalizer_coefficients(int order){
			for(int i=0;i<d_M;i++){
				// std::cout<<i<<"\t"<<fmod(i-1,d_M)<<"\t"<<fmod(i+1,d_M)<<"\tbefor"<<std::endl;
				// std::cout<<i<<"\t"<<d_estimation[i]<<"\t"<<d_estimation[fmod(i-1,d_M)]<<"\t"<<d_estimation[fmod(i+1,d_M)]<<"\tbefor"<<std::endl;
				gr_complex EQi = gr_complex(1,0)/d_estimation[i];
				gr_complex EQmin = gr_complex(1,0)/d_estimation[fmod(i-1+d_M,d_M)];
				gr_complex EQplus = gr_complex(1,0)/d_estimation[fmod(i+1+d_M,d_M)];

				gr_complex EQ1, EQ2;
				if(d_sel_eq==1){ // linear interpolation
					EQ1 = (EQmin+EQi)/gr_complex(2,0);
					EQ2 = (EQplus+EQi)/gr_complex(2,0);
				}else if(d_sel_eq==2){
					float ro = 0.5;
					EQ1 = (gr_complex)EQmin*pow((EQi/EQmin),ro);
	                EQ2 = (gr_complex)EQi*pow((EQplus/EQi),ro);
				}

				// 0:2-> new implementation, 3< -> old implementation
				if(order == 0){
					d_eq_coef[i+2*d_M]= pow(gr_complex(-1,0),i)*((EQ1-gr_complex(2,0)*EQi+EQ2)-gr_complex(0,1)*(EQ2-EQ1))/gr_complex(4,0); // change this first
				}else if (order == 1){
					d_eq_coef[i+d_M]= (gr_complex)(EQ1+EQ2)/gr_complex(2,0); // then this
				}else if(order == 2){
					d_eq_coef[i]= pow(gr_complex(-1,0),i)*((EQ1-gr_complex(2,0)*EQi+EQ2)+gr_complex(0,1)*(EQ2-EQ1))/gr_complex(4,0); // lastly this
				}else{
					d_eq_coef[i]= pow(gr_complex(-1,0),i)*((EQ1-gr_complex(2,0)*EQi+EQ2)+gr_complex(0,1)*(EQ2-EQ1))/gr_complex(4,0);
					d_eq_coef[i+d_M]= (gr_complex)(EQ1+EQ2)/gr_complex(2,0);
					d_eq_coef[i+2*d_M]= pow(gr_complex(-1,0),i)*((EQ1-gr_complex(2,0)*EQi+EQ2)-gr_complex(0,1)*(EQ2-EQ1))/gr_complex(4,0);
				}

				// //logging
				// equalizer_data<<(fr-1)<<"\t"<<i<<"\t"<<real(d_estimation[i])<<"\t"<<imag(d_estimation[i])<<"j\t";//((imag(d_estimation[i])>0)?"+":"-")
				// equalizer_data<<real(d_eq_coef[i])<<"\t"<<imag(d_eq_coef[i])<<"j\t";
				// equalizer_data<<real(d_eq_coef[i+d_M])<<"\t"<<imag(d_eq_coef[i+d_M])<<"j\t";
				// equalizer_data<<real(d_eq_coef[i+2*d_M])<<"\t"<<imag(d_eq_coef[i+2*d_M])<<"j\n"; //<<"fr " est: "
			}
			// fr++;
		}

		int
		fbmc_subchannel_processing_vcvc_impl::work(int noutput_items,
				gr_vector_const_void_star &input_items,
				gr_vector_void_star &output_items)
		{
			const gr_complex *in = (const gr_complex *) input_items[0];
			gr_complex *out = (gr_complex *) output_items[0];
			gr_complex *out_estimation = (gr_complex *) output_items[1];

			//gr_complex estimout = 1;
			//int low, size;
			//low = 0;
			//size = noutput_items*d_M;

			//volk_32fc_x2_multiply_conjugate_32fc(out, in, &d_estimation[low%(int)(d_M)], size);
			//volk_32fc_s32fc_multiply_32fc(out_estimation, &d_estimation[low%(int)(d_M)],estimout, size);


			//out_estimation[i] = d_estimation[i%(int)(d_M)];


			//if(ii%d_frame_length == estimation_point)
										//get_estimation(in+low);
			//ii++;
			// Do <+signal processing+>
			for(int i=0;i<noutput_items*d_M;i++){
				
				if(d_sel_eq==0){
					// one tap zero forcing equalizer
					out[i] = in[i]/(d_estimation[i%(int)(d_M)]); //sumfactor?????
					out_estimation[i] = d_estimation[i%(int)(d_M)];
					// std::cout<<out[i]<<"\t"<<d_estimation[i%d_M]<<"\t"<<in[i]<<std::endl;
				}else if(d_sel_eq==1 || d_sel_eq==2){
					// three taps with linear(=1) or geometric(=2) interpolation
					out[i] = (d_eq_coef[i%d_M]*in[i+2*d_M]+d_eq_coef[(i%d_M)+d_M]*in[i+d_M]+d_eq_coef[(i%d_M)+2*d_M]*in[i]);///gr_complex(3,0);
					out_estimation[i] = d_estimation[i%(int)(d_M)];
				}else{
					// no equalization
					out[i] = in[i];
					out_estimation[i] = d_estimation[i%(int)(d_M)];
				}

				// old implementation
				if(d_sel_eq<3){
					if(d_sel_eq == 1 || d_sel_eq == 2){
						if(ii%d_frame_length == estimation_point){
							get_estimation(in+i+2*d_M);
							get_equalizer_coefficients(999);
						}
					}
					else if(d_sel_eq==0){
						if(ii%d_frame_length == estimation_point){
							get_estimation(in+i);
						}
					}
					ii++;
				}

				// new implementation, we dont change the coefficients immediately after they are generated, instead we will use the old 
				// coeffs until samples from previous symbol is processed.
				// if(d_sel_eq<3){
				// 	if(d_sel_eq == 1 || d_sel_eq == 2){
				// 		if(ii%d_frame_length==(2*d_M-1)){
				// 			get_estimation(in+i+2*d_M);
				// 			get_equalizer_coefficients(0);
				// 		}
				// 		else if(ii%d_frame_length==(2*d_M-1)+d_M){
				// 			get_equalizer_coefficients(1);
				// 		}else if(ii%d_frame_length==(2*d_M-1)+2*d_M){
				// 			get_equalizer_coefficients(2);
				// 		}
				// 	}
				// 	else if(d_sel_eq==0){
				// 		if(ii%d_frame_length==(2*d_M-1)){
				// 			get_estimation(in+i);
				// 		}
				// 	}
				// 	ii++;
				// }
			}

			// Tell runtime system how many output items we produced.
			return noutput_items;
		}

	} /* namespace ofdm */
} /* namespace gr */

