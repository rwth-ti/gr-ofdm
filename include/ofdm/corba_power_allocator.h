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


#ifndef INCLUDED_OFDM_CORBA_POWER_ALLOCATOR_H
#define INCLUDED_OFDM_CORBA_POWER_ALLOCATOR_H

#include <ofdm/api.h>
#include <gnuradio/block.h>



namespace gr {
  namespace ofdm {

  /*! \brief Power De-/Allocator with CORBA control event channel interface
   *
   * \param allocate  If true allocate power, else deallocate
   *
   */

    class OFDM_API corba_power_allocator : virtual public gr::block
    {
     public:
      typedef boost::shared_ptr<corba_power_allocator> sptr;

      /*!
       * \brief Return a shared_ptr to a new instance of ofdm::corba_power_allocator.
       *
       * To avoid accidental use of raw pointers, ofdm::corba_power_allocator's
       * constructor is in a private implementation
       * class. ofdm::corba_power_allocator::make is the public interface for
       * creating new instances.
       */
      static sptr make(int vlen, std::string event_channel, std::string nameservice_ip, std::string nameservice_port, bool allocate);
    };

  } // namespace ofdm
} // namespace gr

#endif /* INCLUDED_OFDM_CORBA_POWER_ALLOCATOR_H */

