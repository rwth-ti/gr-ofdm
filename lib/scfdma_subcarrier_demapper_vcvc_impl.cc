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
#include "scfdma_subcarrier_demapper_vcvc_impl.h"

namespace gr {
  namespace ofdm {

	scfdma_subcarrier_demapper_vcvc::sptr
	scfdma_subcarrier_demapper_vcvc::make(int N, int M, int start, int mode)
	{
	  return gnuradio::get_initial_sptr
		(new scfdma_subcarrier_demapper_vcvc_impl(N, M, start, mode));
	}

	/*
	 * The private constructor
	 */
	scfdma_subcarrier_demapper_vcvc_impl::scfdma_subcarrier_demapper_vcvc_impl(int N, int M, int start, int mode)
	  : gr::sync_block("scfdma_subcarrier_demapper_vcvc",
			  gr::io_signature::make(1, 1, sizeof(gr_complex)*M),
			  gr::io_signature::make(1, 1, sizeof(gr_complex)*N)),
		d_M(M),
		d_N(N),
		d_start(start),
		d_mode(mode),
		d_indices(NULL)
	{
	  get_indices();	  
	}

	/*
	 * Our virtual destructor.
	 */
	scfdma_subcarrier_demapper_vcvc_impl::~scfdma_subcarrier_demapper_vcvc_impl()
	{
	}

	void 
	scfdma_subcarrier_demapper_vcvc_impl::get_indices(){
		if(d_mode==0){ // mode = Localized mapping
			d_indices = new int[d_N];
			for(int i=0;i<d_N;i++){
				*(d_indices+i) = (d_start+i); // maybe later %d_M;
			}
		}else{ // mode = Distributed mapping
			d_indices = new int[d_N];
			for(int i=0;i<d_N;i++){
				*(d_indices+i) = (d_start+i*int(floor(d_M/d_N))); // maybe later %d_M;
			}
		}
	}

	bool
	scfdma_subcarrier_demapper_vcvc_impl::index_included(int index){
		for(int i=0;i<d_N;i++){
			if(d_indices[i] == index){
				return true;
			}
		}
		return false;
	}

	int
	scfdma_subcarrier_demapper_vcvc_impl::work(int noutput_items,
			  gr_vector_const_void_star &input_items,
			  gr_vector_void_star &output_items)
	{
		const gr_complex *in = (const gr_complex *) input_items[0];
		gr_complex *out = (gr_complex *) output_items[0];

		// Do <+signal processing+>
		int oo(0);
		// Do <+signal processing+>
		for(int i=0;i<d_M*noutput_items;i++){
			if(index_included(i%d_M)){
				out[oo++] = in[i];
			}
			// else{
			// 	ii++;
			// }
		}

		// Tell runtime system how many output items we produced.
		return noutput_items;
	}

  } /* namespace ofdm */
} /* namespace gr */

