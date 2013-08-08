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

#ifndef INCLUDED_OFDM_CORBA_MULTIPLEX_SRC_SS_IMPL_H
#define INCLUDED_OFDM_CORBA_MULTIPLEX_SRC_SS_IMPL_H

#include <ofdm/corba_multiplex_src_ss.h>

#include <ofdm/corba_push_consumer.h>
#include <queue>

namespace gr {
  namespace ofdm {

    class corba_multiplex_src_ss_impl : public corba_multiplex_src_ss
    {
     private:
        std::string   d_sevent_channel;
        std::string   d_snameservice_ip;
        std::string   d_snameservice_port;
        boost::shared_ptr<corba_push_consumer> d_push_consumer;

        typedef std::queue<short> queue_type;
        queue_type d_qdata;

        int d_pos;

        int d_bitspermode[9];

        bool d_coding;

     public:
      corba_multiplex_src_ss_impl(std::string sevent_channel, std::string snameservice_ip, std::string snameservice_port, bool coding);
      ~corba_multiplex_src_ss_impl();

      // Where all the action really happens
      void forecast (int noutput_items, gr_vector_int &ninput_items_required);

      int general_work(int noutput_items,
		       gr_vector_int &ninput_items,
		       gr_vector_const_void_star &input_items,
		       gr_vector_void_star &output_items);

      virtual bool start();
      virtual bool stop();

      virtual int noutput_forecast( gr_vector_int &ninput_items,
          int available_space, int max_items_avail,
          std::vector<bool> &input_done );
    };

  } // namespace ofdm
} // namespace gr

#endif /* INCLUDED_OFDM_CORBA_MULTIPLEX_SRC_SS_IMPL_H */

