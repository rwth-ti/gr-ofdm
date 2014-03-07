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

#ifndef INCLUDED_OFDM_SKIP_H
#define INCLUDED_OFDM_SKIP_H

#include <ofdm/api.h>
#include <gnuradio/block.h>

namespace gr {
  namespace ofdm {


  /*!
   * \brief Skip items
   *
   * This block skips items within an item block of size \param blocklen. You
   * specify the items to be skipped via the public interface skip(no).
   *
   * First input is the item stream, first output the filtered stream.
   * Second input is a trigger (char) that should be 1 for the first item in
   * an item block, and 0 else. If connected, the second output is a trigger
   * stream with same properties as the first input, but its block length
   * diminuished by the number of skipped items.
   */

    class OFDM_API skip : virtual public gr::block
    {
     public:
      typedef boost::shared_ptr<skip> sptr;

      /*!
       * \brief Return a shared_ptr to a new instance of ofdm::skip.
       *
       * To avoid accidental use of raw pointers, ofdm::skip's
       * constructor is in a private implementation
       * class. ofdm::skip::make is the public interface for
       * creating new instances.
       */
      static sptr make(std::size_t itemsize, unsigned int blocklen);
      virtual void skip_call (unsigned int no) = 0;
    };

  } // namespace ofdm
} // namespace gr

#endif /* INCLUDED_OFDM_SKIP_H */

