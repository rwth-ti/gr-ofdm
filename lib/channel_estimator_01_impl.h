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

#ifndef INCLUDED_OFDM_CHANNEL_ESTIMATOR_01_IMPL_H
#define INCLUDED_OFDM_CHANNEL_ESTIMATOR_01_IMPL_H

#include <ofdm/channel_estimator_01.h>

#include <vector>
#include <boost/shared_array.hpp>

namespace gr {
  namespace ofdm {

    class channel_estimator_01_impl : public channel_estimator_01
    {
     private:
	  int d_vlen;
	  int d_blk;
	  boost::shared_array<gr_complex> d_inv_ctf_estimate;
	  boost::shared_array<gr_complex> d_ctf_estimate;

	  /*!
	   * Known Symbol: compute CTF for this symbol.
	   * Pilot: Store CTF.
	   * Symbol: Known data
	   */
	  struct ofdm_block
	  {
		ofdm_block() : known_block(false), pilot(false) {};
		bool known_block;
		bool pilot;
		boost::shared_array<gr_complex> block;
	  };

	  std::vector<ofdm_block> d_ofdm_frame;

	  void calculate_equalization(
		  const gr_complex* blk,
		  const boost::shared_array<gr_complex>& known_blk,
		  boost::shared_array<gr_complex> &inv_ctf,
		  boost::shared_array<gr_complex> &ctf);

     public:
      channel_estimator_01_impl(int vlen);
      ~channel_estimator_01_impl();

      void set_known_block(int no, const std::vector<gr_complex> &block, bool pilot);

      // Where all the action really happens
      int work(int noutput_items,
	       gr_vector_const_void_star &input_items,
	       gr_vector_void_star &output_items);
    };

  } // namespace ofdm
} // namespace gr

#endif /* INCLUDED_OFDM_CHANNEL_ESTIMATOR_01_IMPL_H */

