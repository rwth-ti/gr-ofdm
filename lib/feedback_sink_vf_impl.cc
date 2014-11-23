/* -*- c++ -*- */
/* 
 * Copyright 2014 <+YOU OR YOUR COMPANY+>.
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
#include "feedback_sink_vf_impl.h"

namespace gr {
  namespace ofdm {

    feedback_sink_vf::sptr
    feedback_sink_vf::make(size_t subc, char *address)
    {
      return gnuradio::get_initial_sptr
        (new feedback_sink_vf_impl(subc, address));
    }

    /*
     * The private constructor
     */
    feedback_sink_vf_impl::feedback_sink_vf_impl(size_t subc, char *address)
      : gr::sync_block("feedback_sink_vf",
              gr::io_signature::make2(2, 2, sizeof(short), sizeof(float)*subc),
              gr::io_signature::make(0, 0, 0))
      ,d_subc(subc)
    {
        d_context = new zmq::context_t(1);
        d_socket = new zmq::socket_t(*d_context, ZMQ_PUB);
        d_socket->bind(address);
        std::cout << "feedback_sink on " << address << std::endl;
    }

    /*
     * Our virtual destructor.
     */
    feedback_sink_vf_impl::~feedback_sink_vf_impl()
    {
        delete(d_socket);
        delete(d_context);
    }

    void
    feedback_sink_vf_impl::send_snr(short *id, float *snr)
    {
        zmq::message_t msg(sizeof(short)
                           + 200*sizeof(float));
        memcpy(msg.data(), id, sizeof(short));
        memcpy((short*)msg.data()+sizeof(short),
                                 snr,
                                 200*sizeof(float));

        d_socket->send(msg, ZMQ_NOBLOCK);


    }

    int
    feedback_sink_vf_impl::work(int noutput_items,
			  gr_vector_const_void_star &input_items,
			  gr_vector_void_star &output_items)
    {
        short *in_id = (short *) input_items[0];
        float *in_snr = (float *) input_items[1];


        for(int i=0; i< noutput_items; i++)
        {
            send_snr(in_id+i, in_snr+(i*d_subc));
        }
        // Tell runtime system how many output items we produced.
        return noutput_items;
    }

  } /* namespace ofdm */
} /* namespace gr */

