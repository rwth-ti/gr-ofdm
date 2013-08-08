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

#ifndef INCLUDED_OFDM_CORBA_BITCOUNT_SRC_02_SI_IMPL_H
#define INCLUDED_OFDM_CORBA_BITCOUNT_SRC_02_SI_IMPL_H

#include <ofdm/corba_bitcount_src_02_si.h>
#include <ofdm/corba_push_consumer.h>

namespace gr {
  namespace ofdm {

    class corba_bitcount_src_02_si_impl : public corba_bitcount_src_02_si
    {
     private:
    	int   d_istation_id;
		std::string   d_sevent_channel;
		std::string   d_snameservice_ip;
		std::string   d_snameservice_port;
		boost::shared_ptr<corba_push_consumer> d_push_consumer;

		unsigned int d_bitcount;
		short        d_last_id;

		bool d_coding;
		int d_bitspermode[9];

		void store_bitcount( void * cd );

     public:
      corba_bitcount_src_02_si_impl(int istation_id, std::string sevent_channel, std::string snameservice_ip, std::string snameservice_port, bool coding);
      ~corba_bitcount_src_02_si_impl();

      // Where all the action really happens
      int work(int noutput_items,
	       gr_vector_const_void_star &input_items,
	       gr_vector_void_star &output_items);
      virtual bool start();
      virtual bool stop();
    };

  } // namespace ofdm
} // namespace gr

#endif /* INCLUDED_OFDM_CORBA_BITCOUNT_SRC_02_SI_IMPL_H */

