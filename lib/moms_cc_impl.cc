/* -*- c++ -*- */
/* 
 * Copyright 2014 Institute for Theoretical Information Technology,
 *                RWTH Aachen University
 *                www.ti.rwth-aachen.de
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
#include "moms_cc_impl.h"

#include <iostream>

#define DEBUG 0

namespace gr {
  namespace ofdm {

    moms_cc::sptr
    moms_cc::make(double ip_num, double ip_denom)
    {
      return gnuradio::get_initial_sptr
        (new moms_cc_impl(ip_num, ip_denom));
    }

    /*
     * The private constructor
     */
    moms_cc_impl::moms_cc_impl(double ip_num, double ip_denom)
      : gr::block("moms_cc",
              gr::io_signature::make(1, 1, sizeof( gr_complex )),
              gr::io_signature::make(1, 1, sizeof( gr_complex )))
    	, d_ip_num( ip_num )
      	, d_ip_denom( ip_denom )
        , d_offset_num( 0 )
    {}

    /*
     * Our virtual destructor.
     */
    moms_cc_impl::~moms_cc_impl()
    {
    }

    void
    moms_cc_impl::forecast (int noutput_items, gr_vector_int &ninput_items_required)
    {
        /* <+forecast+> e.g. ninput_items_required[0] = noutput_items */
    	  ninput_items_required[0] = ceil(noutput_items*d_ip_num / d_ip_denom) + 3;
    	  if(ninput_items_required[0] < 4)
    	  {
    	    ninput_items_required[0] = 4;
    	  }
    }

    int
    moms_cc_impl::general_work (int noutput_items,
                       gr_vector_int &ninput_items,
                       gr_vector_const_void_star &input_items,
                       gr_vector_void_star &output_items)
    {
    	  gr_complex const * in = static_cast< gr_complex const * >( input_items[0] );
    	  gr_complex * out = static_cast< gr_complex * >( output_items[0] );

    	  int ninput = static_cast<int>(ninput_items[0]);

    	  // Local Variables
    	  double num = d_offset_num;
    	  double const denom = d_ip_denom;
    	  double const ip_num = d_ip_num;

    	  gr_complex tmp = 0.0;
    	  int i = 0;

    	  if(DEBUG) std::cout << "MOMS_FF gen_work: nin: " << ninput << " nout: " << noutput_items << std::endl;

    	  int j = 0;
    	  for(j=0;j<noutput_items && i<ninput-3;++j)
    	  {

    	    // Calculate values (Farrow Structure)
    	    float const d = num/denom;
    	    tmp =         in[i+3]*gr_complex(1./6,0) - in[i+2]*gr_complex(1./2,0) + in[i+1]*gr_complex(1./2,0) - in[i]*gr_complex(1./6,0);
    	    tmp = d*tmp - in[i+3]*gr_complex(1./6,0) + in[i+2]                    - in[i+1]*gr_complex(3./2,0) + in[i]*gr_complex(2./3,0);
    	    tmp = d*tmp                              + in[i+2]*gr_complex(1./6,0) + in[i+1]*gr_complex(2./3,0) - in[i]*gr_complex(5./6,0);
    	    out[j] = d*tmp                                                        + in[i+1]*gr_complex(2./3,0) + in[i]*gr_complex(1/.3,0);

    	    // Calculate new offset
    	    num += ip_num;

    	    // Handle overflow
    	    while(num >= denom)
    	    {
    	      num -= denom;
    	      ++i;
    	    }
    	  }

    	  consume_each(i);

    	  d_offset_num = num;

    	  return j;
    }

    // GET / SET
    void
    moms_cc_impl ::
    set_init_ip_fraction(double num, double denom)
    {
      set_ip_fraction(num, denom);
      d_offset_num -= num;
    }
    void
    moms_cc_impl ::
    set_ip_fraction(double num,double denom)
    {
      // Correct the offset numerator
      d_offset_num = d_offset_num*denom/d_ip_denom;

      d_ip_num = num;
      d_ip_denom = denom;
    }
    double
    moms_cc_impl ::
    get_ip_fraction_num()
    {
      return d_ip_num;
    }
    double
    moms_cc_impl ::
    get_ip_fraction_denom()
    {
      return d_ip_denom;
    }

    void
    moms_cc_impl ::
    set_offset_num(double num)
    {
      d_offset_num = num;

    }
    double
    moms_cc_impl ::
    get_offset_num()
    {
      return d_offset_num;
    }

  } /* namespace ofdm */
} /* namespace gr */

