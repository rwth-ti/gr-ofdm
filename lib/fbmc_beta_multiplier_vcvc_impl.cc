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
#include "fbmc_beta_multiplier_vcvc_impl.h"
#include <volk/volk.h>

namespace gr {
  namespace ofdm {

    fbmc_beta_multiplier_vcvc::sptr
    fbmc_beta_multiplier_vcvc::make(unsigned int M, unsigned int K, unsigned int lp, unsigned int offset)
    {
      return gnuradio::get_initial_sptr
        (new fbmc_beta_multiplier_vcvc_impl(M, K, lp, offset));
    }

    /*
     * The private constructor
     */
    fbmc_beta_multiplier_vcvc_impl::fbmc_beta_multiplier_vcvc_impl(unsigned int M, unsigned int K, unsigned int lp, unsigned int offset)
      : gr::sync_block("fbmc_beta_multiplier_vcvc",
              gr::io_signature::make(1, 1, sizeof(gr_complex)*M),
              gr::io_signature::make(1, 1, sizeof(gr_complex)*M)),
      d_M(M),
      d_K(K),
      d_lp(lp),
      d_offset(offset),
      d_ones(M,1),
      alternating_flag(false)
    {
      assert(M>0 && (log(M)/log(2)) == (round(log(M)/log(2))));
      assert(K==4); //later we might also support K=3
      d_lp = K*M-1; //for now we will only support for this filter length, which will make the process less complex.
      // bool alternating_flag = false; //indicates alternating vector
      for (int i = 0; i< M/2;i++)
    	  d_ones[2*i+1]=-1;
    }

    /*
     * Our virtual destructor.
     */
    fbmc_beta_multiplier_vcvc_impl::~fbmc_beta_multiplier_vcvc_impl()
    {
    }

    int
    fbmc_beta_multiplier_vcvc_impl::work(int noutput_items,
			  gr_vector_const_void_star &input_items,
			  gr_vector_void_star &output_items)
    {
        const gr_complex *in = (const gr_complex *) input_items[0];
        gr_complex *out = (gr_complex *) output_items[0];


        //std::copy(in,in+noutput_items*d_M,out);
        //volk_32fc_32f_multiply_32fc(out, in,&d_ones[0], d_M*);


/*        if(!alternating_flag)
        	{
        	std::copy(in,in+noutput_items*d_M,out);
        	//out+=d_M;
        	in+=d_M;
        	alternating_flag=!alternating_flag;
        	}
        else
        	{
        	volk_32fc_32f_multiply_32fc(out, in,&d_ones[0], d_M);
        	alternating_flag=!alternating_flag;
        	}*/

        //volk_32fc_32f_multiply_32fc(out, in,&d_ones[0], d_M);


        // Do <+signal processing+>
        // beta = (-1)^kn * (-1)^kK
        for(int i=0;i<noutput_items*d_M;i++){
          // int k = i%d_M;
          // int n = floor(i/d_M);
          // out[i] = in[i]*((gr_complex)(pow(-1,k*n)*pow(-1,d_K*k)));
          if(!alternating_flag){
            out[i] = in[i];
          }
          else {
            if(i%2==0){ //even sc
              out[i]=in[i];
            }
            else { //odd sc
              out[i] = gr_complex(-1,0)*in[i];
            }
          }

          if(i%d_M==d_M-1){
            // std::cout<<i<<std::endl;
            alternating_flag=!alternating_flag;
          }


        }

        // Tell runtime system how many output items we produced.
        return noutput_items;
    }

  } /* namespace ofdm */
} /* namespace gr */

