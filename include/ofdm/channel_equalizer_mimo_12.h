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

#ifndef INCLUDED_OFDM_CHANNEL_EQUALIZER_MIMO_12_H
#define INCLUDED_OFDM_CHANNEL_EQUALIZER_MIMO_12_H

#include <ofdm/api.h>
#include <gnuradio/block.h>

namespace gr {
  namespace ofdm {

    /*!
     * \brief <+description of block+>
     * \ingroup ofdm
     *
     */
    class OFDM_API channel_equalizer_mimo_12 : virtual public gr::block
    {
     public:
      typedef boost::shared_ptr<channel_equalizer_mimo_12> sptr;

      /*!
       * \brief Return a shared_ptr to a new instance of ofdm::channel_equalizer_mimo_12.
       *
       * To avoid accidental use of raw pointers, ofdm::channel_equalizer_mimo_12's
       * constructor is in a private implementation
       * class. ofdm::channel_equalizer_mimo_12::make is the public interface for
       * creating new instances.
       */
      static sptr make(int vlen);
    };

  } // namespace ofdm
} // namespace gr

#endif /* INCLUDED_OFDM_CHANNEL_EQUALIZER_MIMO_12_H */

