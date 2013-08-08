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

#ifndef INCLUDED_OFDM_GENERIC_SOFTDEMAPPER_VCF_IMPL_H
#define INCLUDED_OFDM_GENERIC_SOFTDEMAPPER_VCF_IMPL_H

#include <ofdm/generic_softdemapper_vcf.h>

#include <boost/shared_array.hpp>
#include <ofdm/ofdmi_mod.h>

/*!
 * \brief Generic demapper for OFDM
 *
 * Input ports:
 *  1. data blocks
 *  2. bit maps
 *  3- channel state informations (proportional to subchannel SNRs)
 *  4. update trigger
 *
 * Output ports:
 *  1. bit stream
 *
 * Demap incoming data blocks according to last bit map. On update trigger,
 * the next available bit map is stored and will be used for next data blocks.
 * There must be one trigger point per data block with value of either 1 or 0.
 *
 *   Currently supported: 0, 1, 2, 3, 4, 5, 6, 7, 8 bits per symbol
 *   Supported modulations: BPSK, QPSK, 8PSK, 16-QAM, 32-QAM, 64-QAM, 128-QAM, 256-QAM
 */

namespace gr {
  namespace ofdm {

    class generic_softdemapper_vcf_impl : public generic_softdemapper_vcf
    {
     private:
      int d_vlen, d_items_req, d_need_bitmap, d_need_csi;
	  bool d_coding;

	  boost::shared_array<float> d_csi;

	  // internal state
	  boost::shared_array<char> d_bitmap;

	  boost::shared_ptr<ofdmi_modem> d_demod;

     public:
      generic_softdemapper_vcf_impl(int vlen,bool coding);
      ~generic_softdemapper_vcf_impl();

      // Where all the action really happens
      void forecast (int noutput_items, gr_vector_int &ninput_items_required);

      int general_work(int noutput_items,
		       gr_vector_int &ninput_items,
		       gr_vector_const_void_star &input_items,
		       gr_vector_void_star &output_items);

      virtual int noutput_forecast( gr_vector_int &ninput_items,
            int available_space, int max_items_avail,
            std::vector<bool> &input_done );

      std::vector<gr_complex> get_constellation( int bits, bool coding=false );
    };

  } // namespace ofdm
} // namespace gr

#endif /* INCLUDED_OFDM_GENERIC_SOFTDEMAPPER_VCF_IMPL_H */

