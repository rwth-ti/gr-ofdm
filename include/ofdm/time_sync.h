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


#ifndef INCLUDED_OFDM_TIME_SYNC_H
#define INCLUDED_OFDM_TIME_SYNC_H

#include <ofdm/api.h>
#include <gnuradio/block.h>

namespace gr {
  namespace ofdm {

    /*!
     * \brief <+description of block+>
     * \ingroup ofdm
     *
     */
    class OFDM_API time_sync : virtual public gr::block
    {
     public:
      typedef boost::shared_ptr<time_sync> sptr;

      /*!
       * \brief Return a shared_ptr to a new instance of ofdm::time_sync.
       *
       * To avoid accidental use of raw pointers, ofdm::time_sync's
       * constructor is in a private implementation
       * class. ofdm::time_sync::make is the public interface for
       * creating new instances.
       */
      static sptr make(int vlen, int cplen);
    };

  } // namespace ofdm
} // namespace gr

#endif /* INCLUDED_OFDM_TIME_SYNC_H */

