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
#include "corba_multiplex_src_ss_impl.h"

#include <algorithm>
#include <iostream>
#include <cstring>
#include <vector>

namespace gr {
  namespace ofdm {

    corba_multiplex_src_ss::sptr
    corba_multiplex_src_ss::make(std::string sevent_channel, std::string snameservice_ip, std::string snameservice_port, bool coding)
    {
      return gnuradio::get_initial_sptr
        (new corba_multiplex_src_ss_impl(sevent_channel, snameservice_ip, snameservice_port, coding));
    }

    /*
     * The private constructor
     */
    corba_multiplex_src_ss_impl::corba_multiplex_src_ss_impl(std::string sevent_channel, std::string snameservice_ip, std::string snameservice_port, bool coding)
      : gr::block("corba_multiplex_src_ss",
              gr::io_signature::make(1, 1, sizeof(short)),
              gr::io_signature::make(1, 1, sizeof(short)))
		, d_sevent_channel(sevent_channel)
		, d_snameservice_ip(snameservice_ip)
		, d_snameservice_port(snameservice_port)
		, d_pos( 0 )
		, d_coding( coding )
		, d_bitspermode( {1,2,2,4,4,6,6,6,8} )
    {
    	  d_push_consumer =
    	    get_corba_push_consumer_singleton(d_snameservice_ip, d_snameservice_port);
    }

    /*
     * Our virtual destructor.
     */
    corba_multiplex_src_ss_impl::~corba_multiplex_src_ss_impl()
    {
    }

    void
    corba_multiplex_src_ss_impl::forecast (int noutput_items, gr_vector_int &ninput_items_required)
    {
        /* <+forecast+> e.g. ninput_items_required[0] = noutput_items */
    	  if(d_qdata.empty())
    	    ninput_items_required[0] = 1;
    	  else
    	    ninput_items_required[0] = 0;
    }

    int
    corba_multiplex_src_ss_impl::general_work (int noutput_items,
                       gr_vector_int &ninput_items,
                       gr_vector_const_void_star &input_items,
                       gr_vector_void_star &output_items)
    {
    	const short * __restrict in = static_cast< const short* >( input_items[0] );
    	  short * __restrict out = static_cast< short* >( output_items[0] );

    	  bool stop = false;
    	  int o = 0;
    	  int consumed = 0;

    	  short last_id = -1;

    	  corba_push_consumer::value_ptr config_data;
    	  int vlen = 0;
    	  int nzeros = 0;
    	  int pos_max = 0;

    	  int bits_per_block = 0;
    	  std::vector<int> unrolled_assignment_map;

    	  for( int i = 0; i < ninput_items[0] && !stop && o < noutput_items; ++i )
    	  {
    	    if( in[i] != last_id )
    	    {
    	      config_data = d_push_consumer->get_tx_config( in[i], i == 0 );

    	      if( ! config_data )
    	        break;

    	      vlen = config_data->mod_map.length();
    	      nzeros = config_data->id_blocks * vlen;
    	      pos_max = config_data->data_blocks * vlen + nzeros;

    	      bits_per_block = 0;
    	      if(d_coding)
    	      {
    			  for( int subc = 0; subc < vlen; ++subc )
    			  {
    				  if(config_data->mod_map[subc] > 0)
    					  bits_per_block += d_bitspermode[config_data->mod_map[subc]-1];
    			  }

    			  unrolled_assignment_map.resize( bits_per_block );

    			  for( int subc = 0, k = 0; subc < vlen; ++subc )
    			  {
    				  if(config_data->mod_map[subc] > 0)
    				  {
    					  int const rep = d_bitspermode[config_data->mod_map[subc]-1];
    					  short const id = config_data->assignment_map[subc];

    					  for( int x = 0; x < rep; ++x, ++k )
    					  {
    						  unrolled_assignment_map[ k ] = id;
    					  }
    				  }
    			  }
    	      }
    	      else
    	      {
    			  for( int subc = 0; subc < vlen; ++subc )
    			  {
    				bits_per_block += config_data->mod_map[subc];
    			  }

    			  unrolled_assignment_map.resize( bits_per_block );

    			  for( int subc = 0, k = 0; subc < vlen; ++subc )
    			  {
    				  int const rep = config_data->mod_map[subc];
    				  short const id = config_data->assignment_map[subc];
    				  for( int x = 0; x < rep; ++x, ++k )
    				  {
    					unrolled_assignment_map[ k ] = id;
    				  }
    			  }
    	      }

    	      set_output_multiple( bits_per_block );
    	    } // if( in[i] != last_id )

    	    const int n = std::min( noutput_items - o, std::max( 0, nzeros-d_pos ) );

    	    if( n > 0 )
    	    {
    	      for( int j = 0; j < n; ++j, ++o )
    	      {
    		out[o] = 0;
    	      }
    	      d_pos += n;
    	    } // n > 0

    	    if( noutput_items == o )
    	      break;


    	    int pos = d_pos;

    	    for(; pos < pos_max; pos += vlen )
    	    {
    	      if( ( o + bits_per_block ) > noutput_items )
    	      {
    	        stop = true;
    	        break;
    	      }

    	      for( int x = 0; x < bits_per_block; ++x )
    	      {
    	        out[o++] = unrolled_assignment_map[x];
    	      }
    	    } // for(; pos < pos_max; pos += vlen )

    	/*
    	    int subc = pos % vlen;

    	    for( ; pos < pos_max; ++pos )
    	    {
    	      const short id = config_data->assignment_map[subc];

    	      if( id != 0 )
    	      {
    	        const int rep = config_data->mod_map[subc];
    	        const int next_o = o + rep;

    	        if( next_o <= noutput_items )
    	        {
    	          for( int j = 0; j < rep; ++j, ++o )
    	          {
    	            out[o] = id;
    	          }
    	        }
    	        else
    	        {
    	          stop = true;
    	          break;

    	        } // ( o + rep ) <= noutput_items
    	      } // id != 0

    	      ++subc;
    	      if( subc == vlen ) subc = 0;
    	      //subc %= vlen;

    	    } // for-loop
    	*/

    	    d_pos = pos;
    	    if( pos == pos_max )
    	    {
    	      d_pos = 0;
    	      ++consumed;
    	    }

    	  } // for-loop

    	  consume( 0, consumed );

    	  return o;
    }

    bool
    corba_multiplex_src_ss_impl::start()
    {
      d_push_consumer->subscribe_event_channel(d_sevent_channel);
      return true;
    }

    bool
    corba_multiplex_src_ss_impl::stop()
    {
      std::cout << "[corbamuxsrc] shutdown consumer" << std::endl;
      d_push_consumer->shutdown();
      return true;
    }

    int
    corba_multiplex_src_ss_impl::noutput_forecast( gr_vector_int &ninput_items,
        int available_space, int max_items_avail, std::vector<bool> &input_done )
    {

      // if our queue is empty, check if we are done because our upstream block
      // is done. if the queue is empty and we have no input items available,
      // signal that we can't produce anything.

      if( d_qdata.empty() ){

        if( input_done[0] ){
          return -1;
        }

        if( ninput_items[0] == 0 ){
          return 0;
        }
      }

      return available_space;
    }

  } /* namespace ofdm */
} /* namespace gr */

