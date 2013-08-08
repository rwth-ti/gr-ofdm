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
#include "corba_id_filter_impl.h"

#include <iostream>

namespace gr {
  namespace ofdm {

    corba_id_filter::sptr
    corba_id_filter::make(std::string sevent_channel, std::string snameservice_ip, std::string snameservice_port, int max_trials)
    {
      return gnuradio::get_initial_sptr
        (new corba_id_filter_impl(sevent_channel, snameservice_ip, snameservice_port, max_trials));
    }

    /*
     * The private constructor
     */
    corba_id_filter_impl::corba_id_filter_impl(std::string sevent_channel, std::string snameservice_ip, std::string snameservice_port, int max_trials)
      : gr::sync_block("corba_id_filter",
              gr::io_signature::make(1, 1, sizeof(short)),
              gr::io_signature::make(1, 1, sizeof(short)))
		, d_sevent_channel(sevent_channel)
		, d_snameservice_ip(snameservice_ip)
		, d_snameservice_port(snameservice_port)
		, d_max_trials(max_trials)
    	, d_trials(0)
    {
        d_push_consumer = get_corba_push_consumer_singleton(d_snameservice_ip,
                d_snameservice_port);
        d_push_consumer->set_owner("corba_id_filter");
        set_history(2);
    }

    /*
     * Our virtual destructor.
     */
    corba_id_filter_impl::~corba_id_filter_impl()
    {
    }

    int
    corba_id_filter_impl::work(int noutput_items,
			  gr_vector_const_void_star &input_items,
			  gr_vector_void_star &output_items)
    {
    	const short *in = static_cast<const short*> (input_items[0]);
    	    short *out = static_cast<short*> (output_items[0]);

    	    if (noutput_items < 2) {
    	        return (0);
    	    }

    	    for (int i = 0; i < noutput_items-1; ++i) {
    	        short id = in[i+1];
    	        if (in[i] == in[i+2]) {
    	            id = in[i];
    	        }

    	        corba_push_consumer::value_ptr config_data =
    	                d_push_consumer->get_tx_config(id);

    	        //    ofdm_ti::tx_config_data *config_data = d_push_consumer->get_tx_config(id);
    	        if (!config_data) {
    	            //      if(d_trials < d_max_trials){
    	            //        ++d_trials;
    	            //        return i;
    	            //      }

    	            id = d_push_consumer->get_latest_id();
    	            std::cout << "-";
    	        }
    	        else {
    	            std::cout << "+";// << in[i+1];
    	            //      d_trials = 0;
    	        }

    	        out[i] = id;
    	    }

    	    return noutput_items-1;
    }

    bool
    corba_id_filter_impl::start()
    {
        d_push_consumer->subscribe_event_channel(d_sevent_channel);
        return true;
    }

    bool
    corba_id_filter_impl::stop()
    {
        std::cout << "[corbaidfilter] shutdown consumer" << std::endl;
        d_push_consumer->shutdown();
        return true;
    }

  } /* namespace ofdm */
} /* namespace gr */

