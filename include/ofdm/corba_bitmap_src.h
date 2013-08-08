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


#ifndef INCLUDED_OFDM_CORBA_BITMAP_SRC_H
#define INCLUDED_OFDM_CORBA_BITMAP_SRC_H

#include <ofdm/api.h>
#include <gnuradio/sync_interpolator.h>

namespace gr {
  namespace ofdm {

    /*!
     * \brief <+description of block+>
     * \ingroup ofdm
     *
     */
    class OFDM_API corba_bitmap_src : virtual public gr::sync_interpolator
    {
     public:
      typedef boost::shared_ptr<corba_bitmap_src> sptr;

      /*!
       * \brief Return a shared_ptr to a new instance of ofdm::corba_bitmap_src.
       *
       * To avoid accidental use of raw pointers, ofdm::corba_bitmap_src's
       * constructor is in a private implementation
       * class. ofdm::corba_bitmap_src::make is the public interface for
       * creating new instances.
       */
      static sptr make(int vlen, int station_id, std::string event_channel, std::string nameservice_ip, std::string nameservice_port);
    };

  } // namespace ofdm
} // namespace gr

#endif /* INCLUDED_OFDM_CORBA_BITMAP_SRC_H */

