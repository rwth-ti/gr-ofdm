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

#ifdef HAVE_CONFIG_H
#include "config.h"
#endif

#include <gnuradio/io_signature.h>
#include "corba_id_src_impl.h"

#include <iostream>
#include <gnuradio/low_latency_policy.h>

#define DEBUG_OUT 1

namespace gr {
  namespace ofdm {

    corba_id_src::sptr
    corba_id_src::make(std::string sevent_channel, std::string snameservice_ip, std::string snameservice_port)
    {
      return gnuradio::get_initial_sptr
        (new corba_id_src_impl(sevent_channel, snameservice_ip, snameservice_port));
    }

    /*
     * The private constructor
     */
    corba_id_src_impl::corba_id_src_impl(std::string sevent_channel, std::string snameservice_ip, std::string snameservice_port)
      : gr::sync_block("corba_id_src",
              gr::io_signature::make(0, 0, 0),
              gr::io_signature::make(1, 1, sizeof(short)))
		, d_sevent_channel(sevent_channel)
		, d_snameservice_ip(snameservice_ip)
		, d_snameservice_port(snameservice_port)
    {
    	  d_push_consumer = get_corba_push_consumer_singleton(d_snameservice_ip, d_snameservice_port);
    	  set_latency_policy( make_low_latency_policy( 40, 200 ) );
    	  set_output_multiple( 20 );
    }

    /*
     * Our virtual destructor.
     */
    corba_id_src_impl::~corba_id_src_impl()
    {
    }

    int
    corba_id_src_impl::work(int noutput_items,
			  gr_vector_const_void_star &input_items,
			  gr_vector_void_star &output_items)
    {
    	  short *out = static_cast<short*>(output_items[0]);
    	  short ret = d_push_consumer->get_latest_id();

    	  if( ret != -1 )
    	  {
    	//    if( ret != d_lastid )
    	//    {
    	//      std::cout << "ID src, new ID: " << ret << " cnt = " << d_cnt << std::endl;
    	//      d_lastid = ret;
    	//      d_cnt = 0;
    	//    }

    	    for( int i = 0; i < output_multiple(); ++i ){
    	      out[i] = ret;
    	    }

    	//    d_cnt += output_multiple();

    	    return output_multiple();
    	  }
    	  else // interrupt requested, we're done
    	  {
    	    return -1;
    	  }
    }

    bool
    corba_id_src_impl::start()
    {
      d_push_consumer->clear();
      d_push_consumer->subscribe_event_channel(d_sevent_channel);
      return true;
    }

    bool
    corba_id_src_impl::stop()
    {
      if( DEBUG_OUT )
        std::cout << "[corbaidsrc] shutdown push consumer" << std::endl;

      d_push_consumer->shutdown();
      return true;
    }


    bool
    corba_id_src_impl::ready()
    {
      return d_push_consumer->ready();
    }


  } /* namespace ofdm */
} /* namespace gr */

