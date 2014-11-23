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

#ifndef INCLUDED_OFDM_FEEDBACK_SINK_VF_IMPL_H
#define INCLUDED_OFDM_FEEDBACK_SINK_VF_IMPL_H

#include <ofdm/feedback_sink_vf.h>
#include <zmq.hpp>


namespace gr {
  namespace ofdm {

    class feedback_sink_vf_impl : public feedback_sink_vf
    {
     private:

      size_t d_subc;
      zmq::context_t  *d_context;
      zmq::socket_t   *d_socket;


     public:
      feedback_sink_vf_impl(size_t subc, char *address);
      ~feedback_sink_vf_impl();

      void send_snr(short *id, float *snr);

      // Where all the action really happens
      int work(int noutput_items,
	       gr_vector_const_void_star &input_items,
	       gr_vector_void_star &output_items);
    };

  } // namespace ofdm
} // namespace gr

#endif /* INCLUDED_OFDM_FEEDBACK_SINK_VF_IMPL_H */

