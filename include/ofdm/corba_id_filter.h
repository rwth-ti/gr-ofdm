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


#ifndef INCLUDED_OFDM_CORBA_ID_FILTER_H
#define INCLUDED_OFDM_CORBA_ID_FILTER_H

#include <ofdm/api.h>
#include <gnuradio/sync_block.h>



namespace gr {
  namespace ofdm {

  /*!
   * \brief Try to filter corrupted IDs
   *
   * Connect the ID decoder to the input port. It will try to find the IDs in
   * the CORBA pushconsumer buffer. The ID is copied from input to output if it
   * is known to the CORBA subsystem. Else, there will be \param max_trials
   * trials and if it is still unknown, the ID will be replaced by the
   * latest id that is returned by the CORBA pushconsumer.
   */

    class OFDM_API corba_id_filter : virtual public gr::sync_block
    {
     public:
      typedef boost::shared_ptr<corba_id_filter> sptr;

      /*!
       * \brief Return a shared_ptr to a new instance of ofdm::corba_id_filter.
       *
       * To avoid accidental use of raw pointers, ofdm::corba_id_filter's
       * constructor is in a private implementation
       * class. ofdm::corba_id_filter::make is the public interface for
       * creating new instances.
       */
      static sptr make(std::string sevent_channel, std::string snameservice_ip, std::string snameservice_port, int max_trials);
    };

  } // namespace ofdm
} // namespace gr

#endif /* INCLUDED_OFDM_CORBA_ID_FILTER_H */

