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
#include "corba_rxinfo_sink_impl.h"


namespace gr {
  namespace ofdm {

	#define KEEPLAST
	typedef boost::shared_ptr<corba_push_supplier_wrapper> cps_wrap_t;

    corba_rxinfo_sink::sptr
    corba_rxinfo_sink::make(std::string sevent_channel, std::string snameservice_ip, std::string snameservice_port, int vlen, int vlen_sc, long station_id)
    {
      return gnuradio::get_initial_sptr
        (new corba_rxinfo_sink_impl(sevent_channel, snameservice_ip, snameservice_port, vlen, vlen_sc, station_id));
    }

    /*
     * The private constructor
     */
    corba_rxinfo_sink_impl::corba_rxinfo_sink_impl(std::string sevent_channel, std::string snameservice_ip, std::string snameservice_port, int vlen, int vlen_sc, long station_id)
      : gr::sync_block("corba_rxinfo_sink",
              gr::io_signature::make5(7, 7, sizeof(short),
                      sizeof(float)*vlen,
                      sizeof(float)*vlen,
                      sizeof(float)*vlen_sc,
                      sizeof(float)),
              gr::io_signature::make(0, 0, 0))
    	, d_sevent_channel(sevent_channel)
        , d_snameservice_ip(snameservice_ip)
        , d_snameservice_port(snameservice_port)
        , d_vlen(vlen)
        , d_vlen_sc(vlen_sc)
        , d_station_id(station_id)
    {
    	  cps_wrap_t t(new corba_push_supplier_wrapper(snameservice_ip,
    	      snameservice_port));
    	  d_supplier = t;
    }

    /*
     * Our virtual destructor.
     */
    corba_rxinfo_sink_impl::~corba_rxinfo_sink_impl()
    {
    }

    int
    corba_rxinfo_sink_impl::work(int noutput_items,
			  gr_vector_const_void_star &input_items,
			  gr_vector_void_star &output_items)
    {
    	const short *id = static_cast<const short*>(input_items[0]);
    	  const float *ctf = static_cast<const float*>(input_items[1]);
    	  const float *ctf_2 = static_cast<const float*>(input_items[2]);
    	  const float *sinr_sc = static_cast<const float*>(input_items[3]);
    	  const float *ber = static_cast<const float*>(input_items[4]);
    	  const float *snr = static_cast<const float*>(input_items[5]);
    	  const float *snr_2 = static_cast<const float*>(input_items[6]);


    	  ofdm_ti::rx_performance_measure rxinfo;
    	  ofdm_ti::float_sequence corba_ctf(d_vlen);
    	  ofdm_ti::float_sequence corba_ctf_2(d_vlen);
    	  corba_ctf.length(d_vlen);
    	  corba_ctf_2.length(d_vlen);
    	  ofdm_ti::float_sequence corba_est_sinr_sc(d_vlen_sc);
    	  corba_est_sinr_sc.length(d_vlen_sc);

    	//#ifdef KEEPLAST

    	  ctf += (noutput_items-1)*d_vlen;
    	  ctf_2 += (noutput_items-1)*d_vlen;
    	  id += (noutput_items-1);
    	  ber += (noutput_items-1);
    	  snr += (noutput_items-1);
    	  snr_2 += (noutput_items-1);
    	  sinr_sc += (noutput_items-1)*d_vlen_sc;

    	//#else

    	  //for(int j = 0; j < noutput_items; ++j, ++id, ++ber, ++snr, ctf+=d_vlen)

    	//#endif

    	  {

    	    for(int i = 0; i < d_vlen; ++i){
    	      corba_ctf[i] = static_cast<CORBA::Float>(ctf[i]);
    	    }
    	    for(int i = 0; i < d_vlen; ++i){
    	      corba_ctf_2[i] = static_cast<CORBA::Float>(ctf_2[i]);
    	    }
    	    for(int i = 0; i < d_vlen_sc; ++i){
    	      corba_est_sinr_sc[i] = static_cast<CORBA::Float>(sinr_sc[i]);
    	    }
    	    rxinfo.rx_id = static_cast<CORBA::ULong>(*id);
    	    rxinfo.ctf = corba_ctf;
    	    rxinfo.ctf_2 = corba_ctf_2;
    	    rxinfo.est_sinr_sc = corba_est_sinr_sc;
    	    rxinfo.ber = static_cast<CORBA::Float>(*ber);
    	    rxinfo.snr = static_cast<CORBA::Float>(*snr);
    	    rxinfo.snr_2 = static_cast<CORBA::Float>(*snr_2);
    	    rxinfo.rx_station = static_cast<CORBA::Long>(d_station_id);

    	//    std::cout << "BER " << *ber << std::endl;

    	    try {
    	      d_supplier->push( rxinfo );
    	    }
    	    catch( ... )
    	    {
    	      std::cerr << "Too much radiation. Push failed" << std::endl;
    	    }

    	  }

    	  return noutput_items;
    }

    bool
    corba_rxinfo_sink_impl::start()
    {
      d_supplier->set_event_channel(d_sevent_channel);
      return true;
    }

    bool
    corba_rxinfo_sink_impl::stop()
    {
      std::cout << "[corbarxinfosink] supplier shutdown" << std::endl;
      d_supplier->shutdown();

      return true;
    }

  } /* namespace ofdm */
} /* namespace gr */

