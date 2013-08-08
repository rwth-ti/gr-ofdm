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

#ifndef INCLUDED_OFDM_DEPUNCTURE_FF_IMPL_H
#define INCLUDED_OFDM_DEPUNCTURE_FF_IMPL_H

#include <ofdm/depuncture_ff.h>

#include <boost/shared_array.hpp>

namespace gr {
  namespace ofdm {

    class depuncture_ff_impl : public depuncture_ff
    {
     private:
		//unsigned int weight (const std::vector<unsigned char> &punctpat);
		void set_punctpat (char mode);

		int d_need_bits;
		int d_out_bits;
		int d_vlen;
		float d_fillval;
		std::vector<unsigned char> d_punctpat;

		int d_need_modemap;
		boost::shared_array<char> d_modemap;
		int d_rep_per_mode[9];

		int calc_bit_amount( const char* modemap, const int& vlen);
		int calc_out_bit_amount( const char* modemap, const int& vlen);

     public:
      depuncture_ff_impl(int vlen, float fillval);
      ~depuncture_ff_impl();

      // Where all the action really happens
      void forecast (int noutput_items, gr_vector_int &ninput_items_required);

      int general_work(int noutput_items,
		       gr_vector_int &ninput_items,
		       gr_vector_const_void_star &input_items,
		       gr_vector_void_star &output_items);
      virtual int noutput_forecast( gr_vector_int &ninput_items,
      						int available_space, int max_items_avail,
      						std::vector<bool> &input_done );
    };

  } // namespace ofdm
} // namespace gr

#endif /* INCLUDED_OFDM_DEPUNCTURE_FF_IMPL_H */

