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
#include "snr_estimator_dc_null_impl.h"

#include <string.h>
#include <iostream>

#define DEBUG 0

namespace gr {
    namespace ofdm {

        snr_estimator_dc_null::sptr
        snr_estimator_dc_null::make(int vlen, int skip, int dc_null)
        {
            return gnuradio::get_initial_sptr
                (new snr_estimator_dc_null_impl(vlen, skip, dc_null));
        }

        /*
         * The private constructor
         */
        snr_estimator_dc_null_impl::snr_estimator_dc_null_impl(int vlen, int skip, int dc_null)
            : gr::sync_block("snr_estimator_dc_null",
                    gr::io_signature::make(1, 1, sizeof(gr_complex) * vlen),
                    gr::io_signature::make(2, 2, sizeof( float )))
              , d_vlen( vlen )
              , d_skip( skip )
              , d_dc_null ( dc_null )
        {
            assert( d_vlen > 0 );
        }

        /*
         * Our virtual destructor.
         */
        snr_estimator_dc_null_impl::~snr_estimator_dc_null_impl()
        {
        }

        int
        snr_estimator_dc_null_impl::work(int noutput_items,
                gr_vector_const_void_star &input_items,
                gr_vector_void_star &output_items)
        {
            const gr_complex *in = static_cast< const gr_complex* >( input_items[0] );
            float *out_snr = static_cast< float* >( output_items[0] );
            float *out_noise = static_cast< float* >( output_items[1] );
            float sum_load;
            float sum_null;
            float estim_snr;
            float estim_signalplusnoise;
            float estim_noise;
            float square;
            int idx;

            for( int j = 0; j < noutput_items; ++j)
            {
                sum_load = 0.0;
                sum_null = 0.0;
                for( int i = d_dc_null/2; i < d_vlen/2 ; ++i )
                {
                    idx = j*d_vlen + i;
                    // square = std::abs(in[idx]*std::conj(in[idx]));
                    square = in[idx].real()*in[idx].real() + in[idx].imag()*in[idx].imag();
                    if ( (i - (d_skip/2 + d_dc_null/2)) % d_skip == 0 ) {
                        sum_load+=square;
                    }
                    else {
                        sum_null+=square;
                    }
                }

                for( int i = d_vlen-1-d_dc_null/2; i >= d_vlen/2  ; --i )
                {
                    idx = j*d_vlen + i;
                    // square = std::abs(in[idx]*std::conj(in[idx]));
                    square = in[idx].real()*in[idx].real() + in[idx].imag()*in[idx].imag();
                    if ( (i + (d_skip/2 + d_dc_null/2)) % d_skip == 0 ) {
                        sum_load+=square;

                    }
                    else {
                        sum_null+=square;
                    }
                }
                estim_signalplusnoise = sum_load / (d_vlen/d_skip);
                estim_noise = sum_null / ((d_skip-1)*((d_vlen)/d_skip)-d_dc_null);
                estim_snr = (estim_signalplusnoise - estim_noise) / (estim_noise * d_skip);
                out_snr[j] = estim_snr;
                out_noise[j] = estim_noise;
            }
            return noutput_items;
        }
    } /* namespace ofdm */
} /* namespace gr */

