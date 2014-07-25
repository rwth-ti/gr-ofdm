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

#ifndef INCLUDED_OFDM_DIVIDE_FRAME_FC_H
#define INCLUDED_OFDM_DIVIDE_FRAME_FC_H

#include <ofdm/api.h>
#include <gnuradio/sync_block.h>

namespace gr {
  namespace ofdm {

    /*!
     * \brief output = prod (input_0, input_1)
     * \ingroup math_operators_blk
     *
     * \details
     * Multiply across all input streams.
     */
    class OFDM_API divide_frame_fc : virtual public gr::block
    {
    public:

      // gr::blocks::multiply_cc::sptr
      typedef boost::shared_ptr<divide_frame_fc> sptr;

      /*!
       * \brief Multiply OFDM frames with power allocation vector
       * \param frame_size Number of OFDM symbols in frame
       * \param subc Number of subcarriers per OFDM symbol
       * \ingroup ofdm
       */
      static sptr make(size_t frame_size, size_t subc);
    };

  } /* namespace ofdm */
} /* namespace gr */

#endif /* INCLUDED_BLOCKS_DIVIDE_FRAME_FC_H */
