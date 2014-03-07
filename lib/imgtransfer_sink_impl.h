/* -*- c++ -*- */
/* 
 * Copyright 2014 Institute for Theoretical Information Technology,
 *                RWTH Aachen University
 *                www.ti.rwth-aachen.de
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

#ifndef INCLUDED_OFDM_IMGTRANSFER_SINK_IMPL_H
#define INCLUDED_OFDM_IMGTRANSFER_SINK_IMPL_H

#include <ofdm/imgtransfer_sink.h>


#define REPETITIONS 20

namespace gr {
  namespace ofdm {


    class imgtransfer_sink_impl : public imgtransfer_sink
    {
     private:
    	  boost::thread d_udp_thread;
    	  unsigned int d_bitcount;
    	  unsigned int d_bitpos;
    	  unsigned int d_header;
    	  unsigned int d_udppacketsize;
    	  unsigned int d_width, d_height;
    	  unsigned char d_processedbyte;
    	  int d_pos;
    	  unsigned int d_pixelpos;

    	  unsigned int d_packet_to_send;

	      std::vector<unsigned char> d_pixels;
          Bitmap d_compareimage;

    	  std::vector<unsigned char> d_headerbuffer;

    	  bool d_compare;
    	  bool d_printedequality;



    	  CRandom random_generator;

    	  //UDP things...
    	  bool           d_udp_running;
    	  int            d_payload_size;    // maximum transmission unit (packet length)
    	  int            d_socket;          // handle to socket
    	  int            d_socket_rcv;      // handle to socket retuned in the accept call
    	  struct in_addr d_ip_src;          // store the source ip info
    	  struct in_addr d_ip_dst;          // store the destination ip info
    	  unsigned short d_port_src;        // the port number to open for connections to this service
    	  unsigned short d_port_dst;        // port number of the remove system
    	  struct sockaddr_in    d_sockaddr_src;    // store the source sockaddr data (formatted IP address and port number)
    	  struct sockaddr_in    d_sockaddr_dst;    // store the destination sockaddr data (formatted IP address and port number)
    	  bool udp_open();
    	  void udp_close();
    	  void udp_send_pixels(/*unsigned int start, unsigned int count*/);

    	  unsigned int   d_lasttime;

    	  void decode_header();
    	  void write_buffer_to_file();

     public:
      imgtransfer_sink_impl(unsigned int udppacketsize, std::string src_ip, unsigned short src_port, std::string dst_ip, unsigned short dst_port, std::string filename, bool do_compare);
      ~imgtransfer_sink_impl();

      bool start();
	  bool stop();
	  float get_BER_estimate();

      // Where all the action really happens
      void forecast (int noutput_items, gr_vector_int &ninput_items_required);

      int general_work(int noutput_items,
		       gr_vector_int &ninput_items,
		       gr_vector_const_void_star &input_items,
		       gr_vector_void_star &output_items);
    };

  } // namespace ofdm
} // namespace gr

#endif /* INCLUDED_OFDM_IMGTRANSFER_SINK_IMPL_H */

