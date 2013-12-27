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
#include "tx_mux_ctrl_impl.h"

namespace gr {
  namespace ofdm {

    tx_mux_ctrl::sptr
    tx_mux_ctrl::make(int subcarriers)
    {
      return gnuradio::get_initial_sptr
        (new tx_mux_ctrl_impl(subcarriers));
    }

    /*
     * The private constructor
     */
    tx_mux_ctrl_impl::tx_mux_ctrl_impl(int subcarriers)
        : gr::sync_interpolator("tx_mux_ctrl",
                                gr::io_signature::make(1, 1, sizeof(int)),
                                gr::io_signature::make(1, 1, sizeof(char)), 1),
        d_subcarriers(subcarriers), d_prev_bitcount(0)
    {
    }

    /*
     * Our virtual destructor.
     */
    tx_mux_ctrl_impl::~tx_mux_ctrl_impl()
    {
    }

    int
    tx_mux_ctrl_impl::work(int noutput_items,
                           gr_vector_const_void_star &input_items,
                           gr_vector_void_star &output_items)
    {
        const int *in = (const int *) input_items[0];
        char *out = (char *) output_items[0];

        if (*in != d_prev_bitcount) {
            d_prev_bitcount = *in;
            d_mux_ctrl.clear();
            // switch mux to ID
            for(int i=0;i<d_subcarriers;i++)
            {
                d_mux_ctrl.push_back(0);
            }
            // switch mux to DATA
            for(int i=0;i<*in;i++)
            {
                d_mux_ctrl.push_back(1);
            }
            set_interpolation(d_subcarriers+d_prev_bitcount);
            return 0;
        } else if ((d_subcarriers + d_prev_bitcount) < noutput_items) {
            memcpy(out, &d_mux_ctrl[0], sizeof(char)*(d_subcarriers + d_prev_bitcount));
            // Tell runtime system how many output items we produced.
            return (d_subcarriers + d_prev_bitcount);
        } else {
            return 0;
        }

    }

  } /* namespace ofdm */
} /* namespace gr */

