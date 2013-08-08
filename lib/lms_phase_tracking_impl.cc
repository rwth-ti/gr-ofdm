/* -*- c++ -*- */
/* 
 * Copyright 2013 <+YOU OR YOUR COMPANY+>.
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
#include "lms_phase_tracking_impl.h"

#include <gnuradio/expj.h>
#include <gnuradio/math.h>

#include <iostream>
#include <cmath>
#include <algorithm>

#include <string.h>

#define DEBUG(x)

namespace gr {
  namespace ofdm {

    lms_phase_tracking::sptr
    lms_phase_tracking::make(int vlen, const std::vector<int> &pilot_tones, const std::vector<int> &data_symbols)
    {
      return gnuradio::get_initial_sptr
        (new lms_phase_tracking_impl(vlen, pilot_tones, data_symbols));
    }

    /*
     * The private constructor
     */
    lms_phase_tracking_impl::lms_phase_tracking_impl(int vlen, const std::vector<int> &pilot_tones, const std::vector<int> &data_symbols)
      : gr::sync_block("lms_phase_tracking",
              gr::io_signature::make2(2, 2, sizeof(gr_complex)*vlen,
                      sizeof(char)),
              gr::io_signature::make(1, 1, sizeof(gr_complex)*vlen))
    	, d_blk(0)
    	, d_dblk(0)
    	, d_vlen(vlen)
    	, d_pcount(pilot_tones.size())
    {
	  int size = *std::max_element(data_symbols.begin(), data_symbols.end())+1;
	  d_is_data_symbol.resize(size,false);
	  for(unsigned int i = 0; i < data_symbols.size(); ++i) {
		d_is_data_symbol[data_symbols[i]] = true;
		DEBUG(std::cout << "data sym: " << data_symbols[i] << std::endl;)
	  }

	  d_acc_phase.resize(vlen,0.0);
	  d_pilot_tone.resize(d_pcount,1.0); // FIXME allow different pilot tone value
	  d_is_pilot.resize(vlen,false);
	  d_pilot.resize(d_pcount);

	  int fN = static_cast<float>(d_pcount);
	  float x = 0.0;
	  float y = 0.0;
	  for(int i = 0; i < d_pcount; ++i){
		x += static_cast<float>(pilot_tones[i]*pilot_tones[i]);
		y += static_cast<float>(pilot_tones[i]);

		d_pilot[i] = pilot_tones[i]+vlen/2-1;
		d_is_pilot[d_pilot[i]] = true;
	  }

	  std::vector<float> matrix1(2*2,0.0);
	  float c = x*fN-y*y;
	  matrix1[0] = fN/c;
	  matrix1[1] = -y/c;
	  matrix1[2] = -y/c;
	  matrix1[3] = x/c;

	  d_gamma_coeff.resize(d_pcount);
	  //d_b_coeff.resize(d_pcount);
	  for(int i = 0; i < d_pcount; ++i){
		d_gamma_coeff[i] = static_cast<float>(pilot_tones[i])*matrix1[0]+matrix1[2];
		//d_b_coeff[i] = static_cast<float>(pilot_tones[i])*matrix1[1]+matrix1[3];

		DEBUG(std::cout << "gamma["<<i<<"]=" << d_gamma_coeff[i] << std::endl;)
	  }
    }

    /*
     * Our virtual destructor.
     */
    lms_phase_tracking_impl::~lms_phase_tracking_impl()
    {
    }

    int
    lms_phase_tracking_impl::work(int noutput_items,
			  gr_vector_const_void_star &input_items,
			  gr_vector_void_star &output_items)
    {
    	  const gr_complex *in = static_cast<const gr_complex*>(input_items[0]);
    	  const char* trig = static_cast<const char*>(input_items[1]);
    	  gr_complex *out = static_cast<gr_complex*>(output_items[0]);

    	  DEBUG(std::cout << "nout " << noutput_items << std::endl;)

    	  memcpy(out,in,sizeof(gr_complex)*noutput_items*d_vlen);

    	  for(int item = 0; item < noutput_items; ++item, out += d_vlen, ++d_blk){
    	    if(trig[item] == 1){
    	      d_acc_phase.assign(d_acc_phase.size(), 0.0);
    	      d_dblk = 0;
    	      d_blk = 0;

    	      DEBUG(std::cout << "  phase reset" << std::endl;)
    	    }

    	    DEBUG(std::cout << "   d_blk " << d_blk << std::endl;)

    	    if( d_blk < d_is_data_symbol.size() && !d_is_data_symbol[d_blk] ){
    	      continue;
    	    }


    	    DEBUG(std::cout << "d_dblk: " << d_dblk << std::endl;)

    	    // precompensation
    	    if(d_dblk != 0){
    	      DEBUG(std::cout << "precomp" << std::endl;)
    	      for(int i = 0; i < d_vlen; ++i){
    	        out[i] *= gr_expj(-d_acc_phase[i]);
    	      }
    	    }

    	    float gamma = 0.0;
    	    float b = 0.0;

    	    // LMS coefficient adaptation
    	    for(int i = 0; i < d_pcount; ++i){
    	      const gr_complex x = out[d_pilot[i]]*d_pilot_tone[i];
    	      float beta = std::atan2(x.imag(),x.real()); //gr_fast_atan2f();
    	      gamma += d_gamma_coeff[i]*beta;
    	      b += beta; //d_b_coeff[i]
    	      d_acc_phase[d_pilot[i]] += beta;
    	    }
    	    b /= static_cast<float>(d_pcount);

    	    DEBUG(std::cout << "gamma/b: " << gamma << " " << b << std::endl;)

    	    // phase compensation
    	    for(int i = 0; i < d_vlen; ++i){
    	      float y = gamma*(i-d_vlen/2+1)+b;
    	      out[i] *= gr_expj(-y);

    	      if(!d_is_pilot[i]){
    	        d_acc_phase[i] += y;
    	      }
    	    }

    	    ++d_dblk;
    	  }

    	  return noutput_items;
    }

  } /* namespace ofdm */
} /* namespace gr */

