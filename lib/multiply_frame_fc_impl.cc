/* -*- c++ -*- */
/*
 * Copyright 2012 Free Software Foundation, Inc.
 *
 * This file is part of GNU Radio
 *
 * GNU Radio is free software; you can redistribute it and/or modify
 * it under the terms of the GNU General Public License as published by
 * the Free Software Foundation; either version 3, or (at your option)
 * any later version.
 *
 * GNU Radio is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 * GNU General Public License for more details.
 *
 * You should have received a copy of the GNU General Public License
 * along with GNU Radio; see the file COPYING.  If not, write to
 * the Free Software Foundation, Inc., 51 Franklin Street,
 * Boston, MA 02110-1301, USA.
 */

#ifdef HAVE_CONFIG_H
#include "config.h"
#endif

#include "multiply_frame_fc_impl.h"
#include <gnuradio/io_signature.h>
#include <volk/volk.h>

namespace gr {
  namespace ofdm {

    multiply_frame_fc::sptr multiply_frame_fc::make(size_t frame_size, size_t subc)
    {
      return gnuradio::get_initial_sptr(new multiply_frame_fc_impl(frame_size, subc));
    }

    multiply_frame_fc_impl::multiply_frame_fc_impl(size_t frame_size, size_t subc)
      : gr::block("multiply_frame_fc",
              gr::io_signature::make2 (2, 2,sizeof(gr_complex)*subc, sizeof(float)*subc),
              gr::io_signature::make (1,  1, sizeof(gr_complex)*subc)),
        d_subc(subc), d_frame_size(frame_size), d_symbol_counter(0), d_hold_power(std::vector<float>(subc,1.0))
    {
        const int alignment_multiple = volk_get_alignment() / sizeof(gr_complex);
        set_alignment(std::max(1, alignment_multiple));
    }

    multiply_frame_fc_impl::~multiply_frame_fc_impl()
    {
    }



    void
    multiply_frame_fc_impl::forecast (int noutput_items, gr_vector_int &ninput_items_required)
    {
        /* <+forecast+> e.g. ninput_items_required[0] = noutput_items */
        ninput_items_required[0] = noutput_items;
        ninput_items_required[1] = noutput_items/d_frame_size;
    }



    int
    multiply_frame_fc_impl::general_work (int noutput_items,
                       gr_vector_int &ninput_items,
                       gr_vector_const_void_star &input_items,
                       gr_vector_void_star &output_items)
    {
      gr_complex *out = (gr_complex *) output_items[0];
      const gr_complex *in_samples = (const gr_complex *) input_items[0];
      const float *in_power = (const float *) input_items[1];
      int nin_samples = ninput_items[0];
      int nin_power = ninput_items[1];

      int produce = std::min(nin_samples, noutput_items);

      for(int t=0; t<produce; t++)
      {
          if(d_symbol_counter==0)
          {
              if(nin_power==0) return t;
              nin_power--;
              
              d_hold_power.assign(in_power, in_power+d_subc);
              in_power+=d_subc;
              consume(1, 1);
              d_symbol_counter= d_frame_size;
          }
          d_symbol_counter--;

          volk_32fc_32f_multiply_32fc(out, in_samples,&d_hold_power[0], d_subc);
          out+=d_subc;
          in_samples+=d_subc;

          consume(0, 1);
      }
      return produce;
    }

  } /* namespace ofdm */
}/* namespace gr */
