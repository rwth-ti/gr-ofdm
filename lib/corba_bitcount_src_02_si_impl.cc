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
#include "corba_bitcount_src_02_si_impl.h"

#include <iostream>

namespace gr {
  namespace ofdm {

    corba_bitcount_src_02_si::sptr
    corba_bitcount_src_02_si::make(int istation_id, std::string sevent_channel, std::string snameservice_ip, std::string snameservice_port, bool coding)
    {
      return gnuradio::get_initial_sptr
        (new corba_bitcount_src_02_si_impl(istation_id, sevent_channel, snameservice_ip, snameservice_port, coding));
    }

    /*
     * The private constructor
     */
    corba_bitcount_src_02_si_impl::corba_bitcount_src_02_si_impl(int istation_id, std::string sevent_channel, std::string snameservice_ip, std::string snameservice_port, bool coding)
      : gr::sync_block("corba_bitcount_src_02_si",
              gr::io_signature::make(1, 1, sizeof(short)),
              gr::io_signature::make2(2, 2, sizeof(short),
                      sizeof(unsigned int)))
    	, d_istation_id(istation_id)
    	, d_sevent_channel(sevent_channel)
    	, d_snameservice_ip(snameservice_ip)
    	, d_snameservice_port(snameservice_port)
    	, d_last_id( -2 )
		, d_coding( coding )
		//d_bitspermode( {1,2,3,4,5,6,7,10,12} )
		, d_bitspermode( {1,2,3,4,6,8,9,10,12})
    {
    	  d_push_consumer = get_corba_push_consumer_singleton(d_snameservice_ip, d_snameservice_port);
    	  d_push_consumer->set_owner("corba_bitcount_src_si");
    }

    void
    corba_bitcount_src_02_si_impl ::
      store_bitcount( void * cd )
    {
      ofdm_ti::tx_config_data * config_data =
        static_cast< ofdm_ti::tx_config_data * >( cd );

      unsigned int tmp = 0;

      if(d_coding)
      {
    	  //go through assignment map & sum up bits per channel from Mod map with channel coding
    	  for( int j = 0; j < config_data->assignment_map.length(); ++j )
    	  {
    		if( config_data->assignment_map[j] == d_istation_id )
    			tmp += d_bitspermode[config_data->mod_map[j]-1];
    	  }
    	  // multiply with number of data blocks and divide by two because we calculate for 2 symbols
    	  tmp *= config_data->data_blocks/2;
      }
      else
      {
		  //go through assignment map & sum up bits per channel from Mod map
		  for( int j = 0; j < config_data->assignment_map.length(); ++j )
		  {
			if( config_data->assignment_map[j] == d_istation_id )
			  tmp += config_data->mod_map[j];
		  }
		  // multiply with number of data blocks
		  tmp *= config_data->data_blocks;
      }

      d_bitcount = tmp;
    }

    /*
     * Our virtual destructor.
     */
    corba_bitcount_src_02_si_impl::~corba_bitcount_src_02_si_impl()
    {
    }

    int
    corba_bitcount_src_02_si_impl::work(int noutput_items,
			  gr_vector_const_void_star &input_items,
			  gr_vector_void_star &output_items)
    {
    	  const short *in = static_cast<const short*>(input_items[0]);
    	  short *out_id = static_cast<short*>(output_items[0]);
    	  unsigned int *out_cnt = static_cast<unsigned int*>(output_items[1]);

    	  //produce values from input
    	  for( int i = 0; i < noutput_items; ++i )
    	  {
    	#ifdef DEBUG_OUT
    		  std::cout << "Bitcount_src asks for ID: " << in[i] << std::endl;
    	#endif
    	     if( d_last_id != in[i] )
    	     {
    	       corba_push_consumer::value_ptr config_data =
    	         d_push_consumer->get_tx_config( in[i], true ); // blocking

    	       if( ! config_data )
    	         return i;

    	       store_bitcount( static_cast< void * >( config_data.get() ) );
    	       d_last_id = in[i];
    	     }

    	     out_cnt[i] = d_bitcount;
    	     out_id[i] = in[i];

    	//      //stop, if ID was not found or max. output items were produced
    	//      if(config_data == NULL)
    	//      {
    	//#ifdef DEBUG_OUT
    	//    	  std::cout << "Bitcount_src produces " << i << " elements"<< std::endl;
    	//#endif
    	//        return i;
    	//      }
    	//      else
    	//      {
    	//          out[i] = 0;
    	//    	  //go through assignment map & sum up bits per channel from Mod map
    	//    	  for(unsigned int j = 0; j < config_data->assignment_map.length(); ++j)
    	//    	  {
    	//    		  if(config_data->assignment_map[j] == d_istation_id)
    	//    			  out[i] +=  config_data->mod_map[j];
    	//    	  }
    	//    	  // multiply with number of data blocks
    	//    	  out[i] *= config_data->data_blocks;
    	//      }

    	  }
    	#ifdef DEBUG_OUT
    	  std::cout << "Bitcount_src produces " << noutput_items << " elements"<< std::endl;
    	#endif
    	  return noutput_items;
    }

    bool
    corba_bitcount_src_02_si_impl::start()
    {
      d_push_consumer->subscribe_event_channel(d_sevent_channel);
      return true;
    }

    bool
    corba_bitcount_src_02_si_impl::stop()
    {
      std::cout << "[corbabitcountsrc] shutdown consumer" << std::endl;
      d_push_consumer->shutdown();
      return true;
    }

  } /* namespace ofdm */
} /* namespace gr */

