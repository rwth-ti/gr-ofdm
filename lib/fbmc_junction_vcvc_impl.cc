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
#include "fbmc_junction_vcvc_impl.h"

namespace gr {
  namespace ofdm {

    fbmc_junction_vcvc::sptr
    fbmc_junction_vcvc::make(unsigned int M, unsigned int num_input)
    {
      return gnuradio::get_initial_sptr
        (new fbmc_junction_vcvc_impl(M, num_input));
    }

    /*
     * The private constructor
     */
    fbmc_junction_vcvc_impl::fbmc_junction_vcvc_impl(unsigned int M, unsigned int num_input)
      : gr::sync_interpolator("fbmc_junction_vcvc",
              gr::io_signature::make(num_input, num_input, sizeof(gr_complex)*M),
              gr::io_signature::make(1, 1, sizeof(gr_complex)*M), num_input),
      d_M(M),
      d_num_input(num_input)
    {
        // for now we just consider num_input==2
        assert(num_input==2);
    }

    /*
     * Our virtual destructor.
     */
    fbmc_junction_vcvc_impl::~fbmc_junction_vcvc_impl()
    {
    }

    int
    fbmc_junction_vcvc_impl::work(int noutput_items,
			  gr_vector_const_void_star &input_items,
			  gr_vector_void_star &output_items)
    {
        const gr_complex *in0 = (const gr_complex *) input_items[0];
        const gr_complex *in1 = (const gr_complex *) input_items[1];
        gr_complex *out = (gr_complex *) output_items[0];

        // Do <+signal processing+>
        int current_input = 0;
        unsigned int timeout = 1; //d_M;
        unsigned int i0(0), i1(0);
/*        for(int i=0;i<noutput_items*d_M;i++){
            if(current_input==0){
                out[i] = in0[i0];
                i0++;
                timeout--;
                if(timeout==0){
                    timeout = d_M;
                    current_input = 1;
                }
            }else if(current_input==1){
                out[i] = in1[i1];
                i1++;
                timeout--;
                if(timeout==0){
                    timeout = d_M;
                    current_input = 0;
                }
            }
        }*/

        for(int i=0;i<noutput_items;i++){
            if(current_input==0){
                //out[i] = in0[i0];
                memcpy(&out[i*d_M], &in0[i0*d_M], sizeof(gr_complex)*d_M);
                i0++;
                timeout--;
                if(timeout==0){
                    timeout = 1;
                    current_input = 1;
                }
            }else if(current_input==1){
                //out[i] = in1[i1];
                memcpy(&out[i*d_M], &in1[i1*d_M], sizeof(gr_complex)*d_M);
                i1++;
                timeout--;
                if(timeout==0){
                    timeout = 1;
                    current_input = 0;
                }
            }
        }

        // Tell runtime system how many output items we produced.
        return noutput_items;
    }

  } /* namespace ofdm */
} /* namespace gr */

