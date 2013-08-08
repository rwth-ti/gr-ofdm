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


#ifndef INCLUDED_OFDM_CORBA_ASSIGNMENT_SRC_SV_H
#define INCLUDED_OFDM_CORBA_ASSIGNMENT_SRC_SV_H

#include <ofdm/api.h>
#include <gnuradio/block.h>

#include <queue>

namespace gr {
  namespace ofdm {

  /*!
   * \brief Subcarrier assignment source
   *
   * Output assignment as function of ID input and station id. Either 1 if
   * subcarrier belongs to this station or 0 if not. It will output one
   * zero vector for the ID ofdm block and one vector for the data blocks
   * per frame.
   *
   * Note: there are only two vector outputted per frame.
   */

    class OFDM_API corba_assignment_src_sv : virtual public gr::block
    {
     public:
      typedef boost::shared_ptr<corba_assignment_src_sv> sptr;

      /*!
       * \brief Return a shared_ptr to a new instance of ofdm::corba_assignment_src_sv.
       *
       * To avoid accidental use of raw pointers, ofdm::corba_assignment_src_sv's
       * constructor is in a private implementation
       * class. ofdm::corba_assignment_src_sv::make is the public interface for
       * creating new instances.
       */
      static sptr make(int istation_id, int isubcarriers, std::string sevent_channel, std::string snameservice_ip, std::string snameservice_port);
    };

  } // namespace ofdm
} // namespace gr

#endif /* INCLUDED_OFDM_CORBA_ASSIGNMENT_SRC_SV_H */

