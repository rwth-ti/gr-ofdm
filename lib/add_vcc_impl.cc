/* -*- c++ -*- */
/* 
 * Copyright 2015 <+YOU OR YOUR COMPANY+>.
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
#include "add_vcc_impl.h"
#include "malloc16.h"
#include <volk/volk.h>


namespace gr {
  namespace ofdm {

    add_vcc::sptr
    add_vcc::make(size_t vlen)
    {
      return gnuradio::get_initial_sptr
        (new add_vcc_impl(vlen));
    }

    /*
     * The private constructor
     */
    add_vcc_impl::add_vcc_impl(size_t vlen)
      : gr::sync_block("add_vcc",
              gr::io_signature::make(1, 2, sizeof(gr_complex)*vlen),
              gr::io_signature::make(1,  1, sizeof(gr_complex)*vlen)),
              d_inp_i( static_cast< float* >( malloc16Align( sizeof( float ) *vlen ) ) ),
              d_inp_q( static_cast< float* >( malloc16Align( sizeof( float ) *vlen ) ) ),
              d_i( static_cast< float* >( malloc16Align( sizeof( float ) *vlen ) ) ),
              d_q( static_cast< float* >( malloc16Align( sizeof( float ) *vlen ) ) ),
              d_vlen(vlen)
    {
        const int alignment_multiple = volk_get_alignment() / sizeof(gr_complex);
        set_alignment(std::max(1, alignment_multiple));
    }

    /*
     * Our virtual destructor.
     */
    add_vcc_impl::~add_vcc_impl()
    {
    	//if( d_i )
    		//	free16Align( d_i );
    	//if( d_q )
    	    			//free16Align( d_q );
    }

    int
    add_vcc_impl::work(int noutput_items,
			  gr_vector_const_void_star &input_items,
			  gr_vector_void_star &output_items)
    {
    	//const gr_complex *in = (const gr_complex *) input_items[0];
    	gr_complex *out = (gr_complex *) output_items[0];
    	//int noi = d_vlen*noutput_items;
    	const gr_complex *in0 = (const gr_complex *) input_items[0];
    	const gr_complex *in1 = (const gr_complex *) input_items[1];


    	for(int j=0;j<noutput_items;j++){
    		//d_i.resize(d_vlen,0.0);
    		//d_q.resize(d_vlen,0.0);

    		//for(size_t i = 1; i < input_items.size(); i++){
    			//const gr_complex *in = (const gr_complex *) input_items[i];
    			//volk_32fc_deinterleave_32f_x2(&d_inp_i[0],&d_inp_q[0],&in[j*d_vlen],d_vlen);
    			//volk_32f_x2_add_32f(&d_i[0], &d_i[0], &d_inp_i[0], d_vlen);
    			//volk_32f_x2_add_32f(&d_q[0], &d_q[0], &d_inp_q[0], d_vlen);

				volk_32fc_deinterleave_32f_x2(&d_inp_i[0],&d_inp_q[0],&in0[j*d_vlen],d_vlen);
				volk_32fc_deinterleave_32f_x2(&d_i[0],&d_q[0],&in1[j*d_vlen],d_vlen);
				volk_32f_x2_add_32f(&d_i[0], &d_i[0], &d_inp_i[0], d_vlen);
				volk_32f_x2_add_32f(&d_q[0], &d_q[0], &d_inp_q[0], d_vlen);
				//}

    		volk_32f_x2_interleave_32fc(&out[j*d_vlen],&d_i[0],&d_q[0],d_vlen);
    	}
        	//volk_32f_x2_add_32f(out, out, (const float*)input_items[i], noi);
        return noutput_items;
    }

  } /* namespace ofdm */
} /* namespace gr */

