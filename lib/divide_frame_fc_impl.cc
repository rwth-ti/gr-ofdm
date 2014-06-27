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

#include "divide_frame_fc_impl.h"
#include <gnuradio/io_signature.h>
#include <volk/volk.h>

namespace gr {
  namespace ofdm {

    divide_frame_fc::sptr divide_frame_fc::make(const unsigned int frame_size, size_t subc)
    {
      return gnuradio::get_initial_sptr(new divide_frame_fc_impl(frame_size, subc));
    }

    divide_frame_fc_impl::divide_frame_fc_impl(const unsigned int frame_size, size_t subc)
      : gr::block("divide_frame_fc",
                      gr::io_signature::make2 (2, 2,sizeof(float)*subc ,sizeof(gr_complex)*subc),
                      gr::io_signature::make (1,  1, sizeof(gr_complex)*subc)),
        d_subc(subc), d_frame_size(frame_size), d_symbol_counter(0), d_hold_power(std::vector<float>(subc,1))
    {
      const int alignment_multiple =
        volk_get_alignment() / sizeof(gr_complex);
      set_alignment(std::max(1, alignment_multiple));
    }

    divide_frame_fc_impl::~divide_frame_fc_impl()
    {
    }



    void
    divide_frame_fc_impl::forecast (int noutput_items, gr_vector_int &ninput_items_required)
    {
        /* <+forecast+> e.g. ninput_items_required[0] = noutput_items */
          ninput_items_required[0] = noutput_items/d_frame_size;

          for(int i = 1; i < ninput_items_required.size(); ++i)
            ninput_items_required[i] = noutput_items;

    }



    int
    divide_frame_fc_impl::general_work (int noutput_items,
                       gr_vector_int &ninput_items,
                       gr_vector_const_void_star &input_items,
                       gr_vector_void_star &output_items)
    {
      gr_complex *out = (gr_complex *) output_items[0];
      float *in_power = (float *) input_items[0];
      gr_complex *in_samples = (gr_complex *) input_items[1];
      
      for(int t=0; t<noutput_items; t++)
      {
          if(d_symbol_counter==0)
          {
              d_hold_power.assign(in_power,in_power+d_subc);
              in_power+=d_subc;
              consume(0, 1);
              d_symbol_counter= d_frame_size;
          }
          d_symbol_counter--;
          
          for(int i=0;i<d_subc;i++)
          {
              *out=(*in_samples)/(d_hold_power[i]);
              out++;in_samples++;
          }
          consume(1, 1);
      }

      return noutput_items;
    }

  } /* namespace ofdm */
}/* namespace gr */
