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
#include "fbmc_separate_vcvc_impl.h"

namespace gr {
  namespace ofdm {

    fbmc_separate_vcvc::sptr
    fbmc_separate_vcvc::make(unsigned int M, unsigned int num_output)
    {
      return gnuradio::get_initial_sptr
        (new fbmc_separate_vcvc_impl(M, num_output));
    }

    /*
     * The private constructor
     */
    fbmc_separate_vcvc_impl::fbmc_separate_vcvc_impl(unsigned int M, unsigned int num_output)
      : gr::sync_decimator("fbmc_separate_vcvc",
              gr::io_signature::make(1, 1, sizeof(gr_complex)*M),
              gr::io_signature::make(num_output, num_output, sizeof(gr_complex)*M), num_output),
      d_M(M),
      d_num_output(num_output)
    {
      assert(num_output==2); // for now only 2 output block is supported
      assert(M>=0 && (log(d_M)/log(2))==round(log(d_M)/log(2)));
    }

    /*
     * Our virtual destructor.
     */
    fbmc_separate_vcvc_impl::~fbmc_separate_vcvc_impl()
    {
    }

    int
    fbmc_separate_vcvc_impl::work(int noutput_items,
			  gr_vector_const_void_star &input_items,
			  gr_vector_void_star &output_items)
    {
        const gr_complex *in = (const gr_complex *) input_items[0];
        gr_complex *out0 = (gr_complex *) output_items[0];
        gr_complex *out1 = (gr_complex *) output_items[1];

        // int* outputs= new int[d_num_output];
        // for(int i=0;i<d_num_output;i++) *(outputs+i) = 

        int timeout = d_M; //after this many samples we will change the output
        int current_output = 0;
        int i0(0), i1(0);
        // Do <+signal processing+>
        for(int i=0;i<noutput_items*d_M*d_num_output;i++){
          if(current_output==0){
            out0[i0] = in[i];
            i0++;
            timeout--;
            if(timeout==0){
              current_output = 1;
              timeout = d_M;
            }
          }else if(current_output==1){
            out1[i1] = in[i];
            i1++;
            timeout--;
            if(timeout==0){
              current_output = 0;
              timeout = d_M;
            }
          }

        }

        // Tell runtime system how many output items we produced.
        return noutput_items;
    }

  } /* namespace ofdm */
} /* namespace gr */

