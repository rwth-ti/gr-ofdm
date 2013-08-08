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
#include "corba_power_src_sv_impl.h"

#include <iostream>
#include <stdexcept>

#define DEBUG 0

namespace gr {
  namespace ofdm {

    corba_power_src_sv::sptr
    corba_power_src_sv::make(int isubcarriers, std::string sevent_channel,  std::string snamedervice_ip, std::string snameservice_port, bool hack1)
    {
      return gnuradio::get_initial_sptr
        (new corba_power_src_sv_impl(isubcarriers, sevent_channel, snamedervice_ip, snameservice_port, hack1));
    }

    /*
     * The private constructor
     */
    corba_power_src_sv_impl::corba_power_src_sv_impl(int isubcarriers, std::string sevent_channel,  std::string snamedervice_ip, std::string snameservice_port, bool hack1)
      : gr::block("corba_power_src_sv",
              gr::io_signature::make(1, 1, sizeof(short)),
              gr::io_signature::make(1, 1, sizeof(float)*isubcarriers))
		  , d_isubcarriers(isubcarriers)
		  , d_sevent_channel(sevent_channel)
		  , d_snameservice_ip(snamedervice_ip)
		  , d_snameservice_port(snameservice_port)
		  , d_hack1(hack1)
    {
    	d_push_consumer = get_corba_push_consumer_singleton(d_snameservice_ip,
    	    d_snameservice_port);
    	d_push_consumer->set_owner("corba_power_src_sv");
    }

    /*
     * Our virtual destructor.
     */
    corba_power_src_sv_impl::~corba_power_src_sv_impl()
    {
    }

    void
    corba_power_src_sv_impl::forecast (int noutput_items, gr_vector_int &ninput_items_required)
    {
        /* <+forecast+> e.g. ninput_items_required[0] = noutput_items */
    	  if(d_qdata.empty())
    	    ninput_items_required[0] = 1;
    	  else
    	    ninput_items_required[0] = 0;
    }

    int
    corba_power_src_sv_impl::general_work (int noutput_items,
                       gr_vector_int &ninput_items,
                       gr_vector_const_void_star &input_items,
                       gr_vector_void_star &output_items)
    {
    	const short *in = static_cast<const short*>(input_items[0]);
    	  float *out = static_cast<float*>(output_items[0]);



    	  if( d_qdata.empty() ){

    	    for( int i = 0; i < ninput_items[0]; ++i ){

    	      if(DEBUG)
    	        std::cout << "Power_src asks for ID: " << in[i] << std::endl;


    	      corba_push_consumer::value_ptr config_data =
    	         d_push_consumer->get_tx_config(in[i],true);

    	//  	  ofdm_ti::tx_config_data*  config_data =
    	//  	      d_push_consumer->get_tx_config( in[i], true );

    	  	  //stop, if ID was not found or max. output items were produced
    	  	  if( config_data == 0 ){

    	  		break;

    	  	  } else {

    	  	      if( config_data->power_map.length() != (unsigned)d_isubcarriers ){
    	  	        throw std::runtime_error("[PowerMapSrc] Error: received power"\
    	  	                                 " map vector with false length");
    	  	      }

    	  	      int mul_id = config_data->id_blocks;
    	  	      int mul_data = config_data->data_blocks;

    	  	      if( d_hack1 ){ // FIXME dirty hack
    	  	        mul_id = 1;
    	  	        mul_data = 1;
    	  	      }


    	  		  //1st produce ID map(s)
    	  		  for(unsigned short i = 0; i < (mul_id * d_isubcarriers); ++i)
    	  		  {
    	  		    d_qdata.push(1);
    	  		  }

    	  		  //2nd add real maps
    	  		  for(int k = 0; k < mul_data; ++k)
    	  		  {
    	            for(int j = 0; j < d_isubcarriers; ++j)
    	            {
    	              d_qdata.push(config_data->power_map[j]);
    	            }
    	  		  }


    	  		  //3rd remove input item and set ireturn_items
    	  		  consume_each(1);

    	  		  if(DEBUG)
    	  		    std::cout << "Consume input element" << std::endl;

    	  	  } // if config_data == 0

    	    } // for-loop

    	    if(DEBUG)
    	      std::cout << "Power_src consumed"
    	                << " elements and new queue size is "
    	                << d_qdata.size()/d_isubcarriers << std::endl;

    	  } // if d_qdata.empty()


    	  if( d_qdata.empty() ){
    	    if(DEBUG)
    	      std::cout << "Power_src produces " << 0 << " elements"<< std::endl;

    	    return 0;
    	  }

    	  int produced = std::min( noutput_items,
    	         static_cast<int>( d_qdata.size() ) / d_isubcarriers );

    	  for( int p = 0; p < produced*d_isubcarriers; ++p ){
    	    out[p] = d_qdata.front();
    	    d_qdata.pop();
    	  }

    	  if(DEBUG)
    	    std::cout << "Power_src produces " << produced << " elements"<< std::endl;

    	  return produced;
    }

    bool
    corba_power_src_sv_impl::start()
    {
      d_push_consumer->subscribe_event_channel(d_sevent_channel);
      return true;
    }

    bool
    corba_power_src_sv_impl::stop()
    {
      std::cout << "[corbapowersrc] shutdown consumer" << std::endl;
      d_push_consumer->shutdown();
      return true;
    }

  } /* namespace ofdm */
} /* namespace gr */

