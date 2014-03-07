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

#ifndef INCLUDED_OFDM_CODED_BPSK_SOFT_DECODER_IMPL_H
#define INCLUDED_OFDM_CODED_BPSK_SOFT_DECODER_IMPL_H

#include <ofdm/coded_bpsk_soft_decoder.h>

#include <vector>

namespace gr {
  namespace ofdm {

    class coded_bpsk_soft_decoder_impl : public coded_bpsk_soft_decoder
    {
     private:
      int   d_vlen;
	  int   d_output_bits;
	  std::vector<float>   d_whitener;

	  std::vector< bool >  d_mask;

     public:
      coded_bpsk_soft_decoder_impl(int vlen, int output_bits, const std::vector<int>& whitener, std::vector< int > const &mask );
      ~coded_bpsk_soft_decoder_impl();

      // Where all the action really happens
      int work(int noutput_items,
	       gr_vector_const_void_star &input_items,
	       gr_vector_void_star &output_items);
    };

  } // namespace ofdm
} // namespace gr

#endif /* INCLUDED_OFDM_CODED_BPSK_SOFT_DECODER_IMPL_H */

