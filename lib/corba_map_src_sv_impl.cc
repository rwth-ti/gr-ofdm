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
#include "corba_map_src_sv_impl.h"

#include <iostream>

namespace gr {
  namespace ofdm {

    corba_map_src_sv::sptr
    corba_map_src_sv::make(int isubcarriers, std::string sevent_channel, std::string snameservice_ip, std::string snameservice_port)
    {
      return gnuradio::get_initial_sptr
        (new corba_map_src_sv_impl(isubcarriers, sevent_channel, snameservice_ip, snameservice_port));
    }

    /*
     * The private constructor
     */
    corba_map_src_sv_impl::corba_map_src_sv_impl(int isubcarriers, std::string sevent_channel, std::string snameservice_ip, std::string snameservice_port)
      : gr::block("corba_map_src_sv",
              gr::io_signature::make(1, 1, sizeof(short)),
              gr::io_signature::make2(1, 2, isubcarriers*sizeof(char), sizeof(int)))
    	, d_isubcarriers(isubcarriers)
    	, d_sevent_channel(sevent_channel)
    	, d_snameservice_ip(snameservice_ip)
    	, d_snameservice_port(snameservice_port)
    {
    	  d_push_consumer = get_corba_push_consumer_singleton(d_snameservice_ip, d_snameservice_port);
    	  d_push_consumer->set_owner("corba_map_src_sv");
    }

    /*
     * Our virtual destructor.
     */
    corba_map_src_sv_impl::~corba_map_src_sv_impl()
    {
    }

    void
    corba_map_src_sv_impl::forecast (int noutput_items, gr_vector_int &ninput_items_required)
    {
        /* <+forecast+> e.g. ninput_items_required[0] = noutput_items */
    	  if(d_qdata.empty())
    	    ninput_items_required[0] = 1;
    	  else
    	    ninput_items_required[0] = 0;
    }

    int
    corba_map_src_sv_impl::general_work (int noutput_items,
                       gr_vector_int &ninput_items,
                       gr_vector_const_void_star &input_items,
                       gr_vector_void_star &output_items)
    {
      const short *in = static_cast<const short*>(input_items[0]);
      char *out = static_cast<char*>(output_items[0]);
      unsigned int consumed = 0;

      int *count = 0;
      if(output_items.size() > 1)
        count = static_cast<int*>(output_items[1]);

      // TODO: output buffer gross genug?

      if(d_qdata.empty()){
        for(int i = 0; i < ninput_items[0]; ++i)
        {
      	  //Produce a total of "BLOCKS_PER_FRAME" maps per input id
    #ifdef DEBUG_OUT
      	  std::cout << "Map_src asks for ID: " << in[i] << std::endl;
    #endif

          corba_push_consumer::value_ptr config_data =
            d_push_consumer->get_tx_config(in[i],true);

    //  	  ofdm_ti::tx_config_data* config_data = d_push_consumer->get_tx_config(in[i],true);

      	  //stop, if ID was not found or max. output items were produced
      	  if(config_data == NULL)
      	  {
      		  break;
      	  }
      	  else
      	  {
      		  //1st produce ID map(s)
      		  for(unsigned short k = 0; k < (config_data->id_blocks * d_isubcarriers); ++k)
      		  {
      			  //out[act_out_pos++] = 1;
      			  d_qdata.push(1);
      		  }

      		  if(count){

                for(int j = 0; j < d_isubcarriers; ++j)
                {
                    //out[act_out_pos++] = config_data->mod_map[j];
                  d_qdata.push(config_data->mod_map[j]);
                }

                d_cqdata.push(config_data->id_blocks);
                d_cqdata.push(config_data->data_blocks);

      		  }else{

        		  //2nd add real maps
        		  for(int k = 0; k < config_data->data_blocks; ++k)
        		  {
        			  for(int j = 0; j < d_isubcarriers; ++j)
        			  {
        				  //out[act_out_pos++] = config_data->mod_map[j];
        			    d_qdata.push(config_data->mod_map[j]);
        			  }
        		  }

      		  }


      		  //3rd remove input item and set ireturn_items
      		  //ireturn_items += config_data->data_blocks + config_data->id_blocks;
      		  consume_each(1);
      		  ++consumed;
      	  }
        }
    #ifdef DEBUG_OUT
      std::cout << "Map_src consumed " << consumed << " elements and new queue size is " << d_qdata.size()/d_isubcarriers << std::endl;
    #endif
      }

      if(d_qdata.empty()){
    #ifdef DEBUG_OUT
        std::cout << "Map_src produces " << 0 << " elements"<< std::endl;
    #endif
        return 0;
      }

      int produced = std::min(noutput_items,static_cast<int>(d_qdata.size())/d_isubcarriers);

      for(int p = 0; p < produced*d_isubcarriers; ++p){
        out[p] = d_qdata.front();
        d_qdata.pop();
      }

      if(count){
        for(int p = 0; p < produced; ++p){
          count[p] = d_cqdata.front();
          d_cqdata.pop();
        }

        assert(d_cqdata.size()*d_isubcarriers == d_qdata.size());
      }

    #ifdef DEBUG_OUT
      std::cout << "Map_src produces " << produced << " elements"<< std::endl;
    #endif

      return produced;
    }

    bool
    corba_map_src_sv_impl::start()
    {
      d_push_consumer->subscribe_event_channel(d_sevent_channel);
      return true;
    }

    bool
    corba_map_src_sv_impl::stop()
    {
      std::cout << "[corbamapsrc] shutdown consumer" << std::endl;
      d_push_consumer->shutdown();
      return true;
    }

  } /* namespace ofdm */
} /* namespace gr */

