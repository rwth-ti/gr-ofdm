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
#include "corba_power_allocator_impl.h"

#include <gnuradio/malloc16.h>
#include <algorithm>
#include <cmath>
#include <stdexcept>
#include <iostream>

#define DEBUG 0

namespace gr {
  namespace ofdm {

    corba_power_allocator::sptr
    corba_power_allocator::make(int vlen, std::string event_channel, std::string nameservice_ip, std::string nameservice_port, bool allocate)
    {
      return gnuradio::get_initial_sptr
        (new corba_power_allocator_impl(vlen, event_channel, nameservice_ip, nameservice_port, allocate));
    }

    /*
     * The private constructor
     */
    corba_power_allocator_impl::corba_power_allocator_impl(int vlen, std::string event_channel, std::string nameservice_ip, std::string nameservice_port, bool allocate)
      : gr::block("corba_power_allocator",
              gr::io_signature::make3(3, 3, sizeof(gr_complex)*vlen,   // blocks
                      sizeof(short),             // IDs
                      sizeof(char) ),            // trig
              gr::io_signature::make(1, 1, sizeof(gr_complex)*vlen)) // blocks
    	  , d_vlen( vlen )
		  , d_event_channel( event_channel )
		  , d_nameservice_ip( nameservice_ip )
		  , d_nameservice_port( nameservice_port )
		  , d_allocate( allocate )
		  , d_need_id( 1 )
		  , d_last_id( -1 )
    {
    	  d_last_powermap =
    	    static_cast< afloat * >( malloc16Align( sizeof( float ) * vlen ) );

    	  d_push_consumer = get_corba_push_consumer_singleton(nameservice_ip,
    	        nameservice_port);

    	  d_push_consumer->set_owner("corba_power_allocator");
    }

    /*
     * Our virtual destructor.
     */
    corba_power_allocator_impl::~corba_power_allocator_impl()
    {
    	  if( d_last_powermap )
    	    free16Align( static_cast< void * >( d_last_powermap ) );
    }

    void
    corba_power_allocator_impl::forecast (int noutput_items, gr_vector_int &ninput_items_required)
    {
        /* <+forecast+> e.g. ninput_items_required[0] = noutput_items */
    	  ninput_items_required[0] = noutput_items; // blocks
    	  ninput_items_required[2] = noutput_items; // trigger
    	  ninput_items_required[1] = d_need_id;
    }

    void
    corba_power_allocator_impl::get_power_map( short id )
    {
      corba_push_consumer::value_ptr config_data =
        d_push_consumer->get_tx_config( id, true );

    //  ofdm_ti::tx_config_data* config_data =
    //      d_push_consumer->get_tx_config( id, true ); // blocking


      if( config_data->power_map.length() != (unsigned)d_vlen )
      {
        throw std::runtime_error("[PowerAlloc] Error: received power map"\
                                 " vector has different length than expected");
      }


      for( int i = 0; i < d_vlen; ++i )
      {
        float tmp = std::sqrt( config_data->power_map[i] );
        if( tmp < 10e-6 )
          tmp = 1.0; // for deallocate, limit

        if( d_allocate )
        {
          d_last_powermap[i] = tmp;
          //d_last_powermap[2*i+1] = tmp;
        }
        else
        {
          d_last_powermap[i] = 1.0/tmp;
          //d_last_powermap[2*i+1] = 1.0/tmp;
        }
      } // for( int i = 0; i < d_vlen; ++i )

    }

    int
    corba_power_allocator_impl::general_work (int noutput_items,
                       gr_vector_int &ninput_items,
                       gr_vector_const_void_star &input_items,
                       gr_vector_void_star &output_items)
    {
    	const gr_complex *blk = static_cast<const gr_complex*>(input_items[0]);
    	  const short *id = static_cast<const short*>(input_items[1]);
    	  const char *trig = static_cast<const char*>(input_items[2]);

    	  gr_complex *out = static_cast<gr_complex*>(output_items[0]);


    	  int n_blk = ninput_items[0];
    	  int n_id = ninput_items[1];
    	  int n_trig = ninput_items[2];
    	  int nout = noutput_items;

    	  int n_min = std::min( nout, std::min( n_blk, n_trig ) );

    	  memcpy( out, blk, n_min * sizeof(gr_complex) * d_vlen );

    	  for( int n = 0; n < n_min; ++n, out += d_vlen, --nout )
    	  {
    	    if( trig[n] == 1 )
    	    {
    	      if( n_id > 0 )
    	      {
    	        if( *id != d_last_id )
    	          get_power_map( *id );
    	        d_last_id = *id;
    	        ++id;
    	        --n_id;
    	      }
    	      else
    	      {
    	        d_need_id = 1;
    	        break;
    	      } // n_id > 0

    	      // handle ID block here, power map = [1]*vlen
    	      // TODO: more than one ID block?
    	      continue;

    	    } // trig[n] == 1

    	    // data block

    	    int const i_max = d_vlen;
    	    for( int i = 0; i < i_max; ++i ) // AUTO VECTORIZED!!
    	    {
    	      out[i] *= d_last_powermap[i];
    	    }

    	  } // for-loop

    	  consume( 1, ninput_items[1] - n_id );

    	  int p = noutput_items - nout;
    	  consume( 0, p );
    	  consume( 2, p );

    	  return p;
    }

    bool
    corba_power_allocator_impl::start()
    {
      d_push_consumer->subscribe_event_channel(d_event_channel);
      return true;
    }

    bool
    corba_power_allocator_impl::stop()
    {
      std::cout << "[corbapowerallocator] shutdown consumer" << std::endl;
      d_push_consumer->shutdown();
      return true;
    }


    int
    corba_power_allocator_impl::noutput_forecast( gr_vector_int &ninput_items,
        int available_space, int max_items_avail, std::vector<bool> &input_done )
    {

      if( ninput_items[1] < d_need_id ){
        if( input_done[1] )
          return -1;

        return 0;
      }

      int nout = std::min( available_space,
                 std::min( ninput_items[0], ninput_items[2] ) );

      if( nout == 0 && ( input_done[0] || input_done[2] ) )
        return -1;

      return nout;

    }

  } /* namespace ofdm */
} /* namespace gr */

