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


#ifndef INCLUDED_OFDM_IMGTRANSFER_SINK_H
#define INCLUDED_OFDM_IMGTRANSFER_SINK_H

#include <ofdm/api.h>
#include <gnuradio/block.h>

#include <vector>
#include <ofdm/util_random.h>
#include <ofdm/util_bmp.h>
#include <sys/socket.h>
#include <arpa/inet.h>

#include <boost/thread/thread.hpp>
#include <netdb.h>
#include <stdio.h>

#include <string.h>

#include <boost/date_time/posix_time/posix_time_types.hpp>

//#include <boost/thread/thread.hpp>
#include <boost/bind.hpp>


namespace gr {
  namespace ofdm {

    /*!
     * \brief <+description of block+>
     * \ingroup ofdm
     *
     */
    class OFDM_API imgtransfer_sink : virtual public gr::block
    {


     public:
      typedef boost::shared_ptr<imgtransfer_sink> sptr;
      virtual float get_BER_estimate();



      /*!
       * \brief Return a shared_ptr to a new instance of ofdm::imgtransfer_sink.
       *
       * To avoid accidental use of raw pointers, ofdm::imgtransfer_sink's
       * constructor is in a private implementation
       * class. ofdm::imgtransfer_sink::make is the public interface for
       * creating new instances.
       */
      static sptr make(unsigned int udppacketsize=512, std::string src_ip="127.0.0.1", unsigned short src_port=0, std::string dst_ip="127.0.0.1", unsigned short dst_port=45454, std::string filename="", bool do_compare=true);
    };

  } // namespace ofdm
} // namespace gr

#endif /* INCLUDED_OFDM_IMGTRANSFER_SINK_H */

