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
#include "reference_data_source_02_ib_impl.h"

#define DEBUG 0

namespace gr {
  namespace ofdm {

    reference_data_source_02_ib::sptr
    reference_data_source_02_ib::make(const std::vector<char> &ref_data)
    {
      return gnuradio::get_initial_sptr
        (new reference_data_source_02_ib_impl(ref_data));
    }

    /*
     * The private constructor
     */
    reference_data_source_02_ib_impl::reference_data_source_02_ib_impl(const std::vector<char> &ref_data)
      : gr::sync_interpolator("reference_data_source_02_ib",
              gr::io_signature::make2 (2, 2, sizeof(short), sizeof(unsigned int)),
              gr::io_signature::make(1, 1, sizeof(char)),1800)
        , d_ref_data(ref_data)
        , d_bitcount(0)
    {}

    /*
     * Our virtual destructor.
     */
    reference_data_source_02_ib_impl::~reference_data_source_02_ib_impl()
    {
    }

    int
    reference_data_source_02_ib_impl::work(int noutput_items,
                                           gr_vector_const_void_star &input_items,
                                           gr_vector_void_star &output_items)
    {
        const short *in_id = static_cast<const short*>(input_items[0]);
        const unsigned int *in_cnt = static_cast<const unsigned int*>(input_items[1]);
        char *out_bits = static_cast<char*>(output_items[0]);

        if (*in_cnt != d_bitcount) {
            d_bitcount = *in_cnt;
            set_interpolation(d_bitcount);
            return 0;
        } else {
            memcpy(out_bits, &d_ref_data[in_id[0]*in_cnt[0]], sizeof(char)*(d_bitcount));
            // Tell runtime system how many output items we produced.
            return d_bitcount;
        }
    }
  } /* namespace ofdm */
} /* namespace gr */

