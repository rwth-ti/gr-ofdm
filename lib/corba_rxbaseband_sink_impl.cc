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
#include "corba_rxbaseband_sink_impl.h"

namespace gr {
  namespace ofdm {

	#define KEEPLAST
	typedef boost::shared_ptr<corba_push_supplier_wrapper> cps_wrap_t;

    corba_rxbaseband_sink::sptr
    corba_rxbaseband_sink::make(std::string sevent_channel, std::string snameservice_ip, std::string snameservice_port, int vlen, long station_id)
    {
      return gnuradio::get_initial_sptr
        (new corba_rxbaseband_sink_impl(sevent_channel, snameservice_ip, snameservice_port, vlen, station_id));
    }

    /*
     * The private constructor
     */
    corba_rxbaseband_sink_impl::corba_rxbaseband_sink_impl(std::string sevent_channel, std::string snameservice_ip, std::string snameservice_port, int vlen, long station_id)
      : gr::sync_block("corba_rxbaseband_sink",
              gr::io_signature::make(1, 1,sizeof(float)*vlen),
              gr::io_signature::make(0, 0, 0))
    	, d_sevent_channel(sevent_channel)
        , d_snameservice_ip(snameservice_ip)
        , d_snameservice_port(snameservice_port)
        , d_vlen(vlen)
        , d_station_id(station_id)
    {
    	  cps_wrap_t t(new corba_push_supplier_wrapper(snameservice_ip,
    	      snameservice_port));
    	  d_supplier = t;

    }

    /*
     * Our virtual destructor.
     */
    corba_rxbaseband_sink_impl::~corba_rxbaseband_sink_impl()
    {
    }

    int
    corba_rxbaseband_sink_impl::work(int noutput_items,
			  gr_vector_const_void_star &input_items,
			  gr_vector_void_star &output_items)
    {
    	//const short *id = static_cast<const short*>(input_items[0]);
    	  const float *bband = static_cast<const float*>(input_items[0]);
    	  //const float *frlos = static_cast<const float*>(input_items[2]);

    	  ofdm_ti::baseband_rx rxbaseband;
    	  ofdm_ti::float_sequence corba_bband(d_vlen);
    	  corba_bband.length(d_vlen);

    	#ifdef KEEPLAST

    	  bband += (noutput_items-1)*d_vlen;
    	  //id += (noutput_items-1);
    	  //frlos += (noutput_items-1);

    	#else

    	  for(int j = 0; j < noutput_items; ++j, /*++id,*/ bband+=d_vlen)
    	  //for(int j = 0; j < noutput_items; ++j, ++id, ++frlos, bband+=d_vlen)

    	#endif

    	  {

    	    for(int i = 0; i < d_vlen; ++i){
    	      corba_bband[i] = static_cast<CORBA::Float>(bband[i]);
    	    }
    	    //rxbaseband.rx_id = static_cast<CORBA::ULong>(*id);
    	    rxbaseband.bband = corba_bband;
    	    //rxbaseband.frlos = static_cast<CORBA::Float>(*frlos);
    	    rxbaseband.rx_station = static_cast<CORBA::Long>(d_station_id);

    	    try {
    	      d_supplier->push( rxbaseband );
    	    }
    	    catch( ... )
    	    {
    	      std::cerr << "Too much radiation.  failed" << std::endl;
    	    }

    	  }

    	  return noutput_items;
    }

    bool
    corba_rxbaseband_sink_impl::start()
    {
      d_supplier->set_event_channel(d_sevent_channel);
      return true;
    }

    bool
    corba_rxbaseband_sink_impl::stop()
    {
      std::cout << "[corbarxbasebandsink] supplier shutdown" << std::endl;
      d_supplier->shutdown();

      return true;
    }

  } /* namespace ofdm */
} /* namespace gr */

