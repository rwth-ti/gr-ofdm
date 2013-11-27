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
      : gr::block("reference_data_source_02_ib",
              gr::io_signature::make2 (2, 2, sizeof(short), sizeof(unsigned int)),
              gr::io_signature::make(1, 1, sizeof(char)))
        , d_ref_data(ref_data)
        , d_vec_pos(0)
        , d_produced(0)
    {}

    /*
     * Our virtual destructor.
     */
    reference_data_source_02_ib_impl::~reference_data_source_02_ib_impl()
    {
    }

    void
    reference_data_source_02_ib_impl::forecast (int noutput_items, gr_vector_int &ninput_items_required)
    {
        /* <+forecast+> e.g. ninput_items_required[0] = noutput_items */
        ninput_items_required[0] = 1;
        ninput_items_required[1] = 1;
    }

    int
    reference_data_source_02_ib_impl::general_work (int noutput_items,
                       gr_vector_int &ninput_items,
                       gr_vector_const_void_star &input_items,
                       gr_vector_void_star &output_items)
    {
        const short *in_id = static_cast<const short*>(input_items[0]);
        const unsigned int *in_cnt = static_cast<const unsigned int*>(input_items[1]);
        char *out = static_cast<char*>(output_items[0]);

        if(DEBUG)
            std::cout << "[dref.src " << unique_id() << "] entered, state "
                << "nin=" << ninput_items[0] << " nout=" << noutput_items
                << " d_produced=" << d_produced
                << " in_cnt[0]=" << in_cnt[0]
                << std::endl;

        if(in_cnt[0] == 0){

            std::cerr << "warning: bitcount = 0" << std::endl;
            consume_each(1);
            return 0;

        } else if(in_cnt[0] > d_produced){
            //how many bits should be produced?
            int nout = std::min(in_cnt[0]-d_produced,(unsigned int)noutput_items);

            if(DEBUG)
                std::cout << "produce " << nout << " items" << std::endl;

            //copy as many bits as needed
            for (int i = 0 ; i < nout; ++i) {
                //reset if end of input vector reached
                assert((unsigned int)d_vec_pos <= d_ref_data.size());
                out[i] = d_ref_data[in_id[0]*in_cnt[0]+d_vec_pos];
                d_vec_pos++;
            }
            d_produced += nout;

            // if frame end reached restart counter and call consume
            if(d_produced >= in_cnt[0]){
                d_produced = 0;
                d_vec_pos = 0;
                consume_each(1);
                if(DEBUG)
                    std::cout << "consume input value" << std::endl;
            }

            return nout;

        }

        assert(false && "should never get here");
        return -1;
    }

  } /* namespace ofdm */
} /* namespace gr */

