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

#ifndef INCLUDED_OFDM_CORBA_POWER_ALLOCATOR_IMPL_H
#define INCLUDED_OFDM_CORBA_POWER_ALLOCATOR_IMPL_H

#include <ofdm/corba_power_allocator.h>

#include <ofdm/corba_push_consumer.h>

namespace gr {
  namespace ofdm {

    class corba_power_allocator_impl : public corba_power_allocator
    {
     private:
		int             d_vlen;
		std::string     d_event_channel;
		std::string     d_nameservice_ip;
		std::string     d_nameservice_port;
		bool            d_allocate;

		boost::shared_ptr<corba_push_consumer> d_push_consumer;

		int             d_need_id;
		short           d_last_id;
		typedef float afloat __attribute__ ((__aligned__(16)));
		afloat * d_last_powermap;

		void get_power_map( short id );

     public:
      corba_power_allocator_impl(int vlen, std::string event_channel, std::string nameservice_ip, std::string nameservice_port, bool allocate);
      ~corba_power_allocator_impl();

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

#endif /* INCLUDED_OFDM_CORBA_POWER_ALLOCATOR_IMPL_H */

