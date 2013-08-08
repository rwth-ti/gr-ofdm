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

#ifndef INCLUDED_OFDM_CORBA_BITMAP_SRC_IMPL_H
#define INCLUDED_OFDM_CORBA_BITMAP_SRC_IMPL_H

#include <ofdm/corba_bitmap_src.h>

#include <ofdm/corba_push_consumer.h>


namespace gr {
  namespace ofdm {

    class corba_bitmap_src_impl : public corba_bitmap_src
    {
     private:
    	int             d_vlen;
		int             d_station_id;
		std::string     d_event_channel;
		std::string     d_nameservice_ip;
		std::string     d_nameservice_port;

		short           d_last_id;

		boost::shared_ptr<corba_push_consumer> d_push_consumer;

		void set_map_for_idblock( char * const map );
		void store_map( void * config_data );

		typedef char achar __attribute__ ((__aligned__(16)));
    	    achar * d_map;

     public:
      corba_bitmap_src_impl(int vlen, int station_id, std::string event_channel, std::string nameservice_ip, std::string nameservice_port);
      ~corba_bitmap_src_impl();

      // Where all the action really happens
      int work(int noutput_items,
	       gr_vector_const_void_star &input_items,
	       gr_vector_void_star &output_items);

      virtual bool start();
      virtual bool stop();

    };

  } // namespace ofdm
} // namespace gr

#endif /* INCLUDED_OFDM_CORBA_BITMAP_SRC_IMPL_H */

