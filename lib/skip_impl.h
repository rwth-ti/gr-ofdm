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

#ifndef INCLUDED_OFDM_SKIP_IMPL_H
#define INCLUDED_OFDM_SKIP_IMPL_H

#include <ofdm/skip.h>


namespace gr {
  namespace ofdm {

    class skip_impl : public skip
    {
     private:
        std::size_t   d_itemsize;
        unsigned int d_blocklen;
        unsigned int d_item;
        unsigned int d_skip;

        std::vector<bool> d_items;
        std::vector<bool> d_first_item;

        int fixed_rate_ninput_to_noutput(int ninput);
        int fixed_rate_noutput_to_ninput(int noutput);

     public:
      skip_impl(std::size_t itemsize, unsigned int blocklen);
      ~skip_impl();

      // Where all the action really happens
      void forecast (int noutput_items, gr_vector_int &ninput_items_required);

      int general_work(int noutput_items,
		       gr_vector_int &ninput_items,
		       gr_vector_const_void_star &input_items,
		       gr_vector_void_star &output_items);

      void skip_call(unsigned int no);

      virtual int noutput_forecast( gr_vector_int &ninput_items,
          int available_space, int max_items_avail,
          std::vector<bool> &input_done );
    };

  } // namespace ofdm
} // namespace gr

#endif /* INCLUDED_OFDM_SKIP_IMPL_H */

