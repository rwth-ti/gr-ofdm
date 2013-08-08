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


#ifndef INCLUDED_OFDM_TRIGGER_SURVEILLANCE_H
#define INCLUDED_OFDM_TRIGGER_SURVEILLANCE_H

#include <ofdm/api.h>
#include <gnuradio/sync_block.h>

namespace gr {
  namespace ofdm {

    /*!
     * \brief <+description of block+>
     * \ingroup ofdm
     *
     */
    class OFDM_API trigger_surveillance : virtual public gr::sync_block
    {
     public:
      typedef boost::shared_ptr<trigger_surveillance> sptr;

      /*!
       * \brief Return a shared_ptr to a new instance of ofdm::trigger_surveillance.
       *
       * To avoid accidental use of raw pointers, ofdm::trigger_surveillance's
       * constructor is in a private implementation
       * class. ofdm::trigger_surveillance::make is the public interface for
       * creating new instances.
       */
      static sptr make(int ideal_distance, int max_shift);

      //virtual unsigned long long lost_triggers() const = 0; //{ return d_lost; };
      //virtual void reset_counter() = 0; //{ d_lost = 0; };
    };

  } // namespace ofdm
} // namespace gr

#endif /* INCLUDED_OFDM_TRIGGER_SURVEILLANCE_H */

