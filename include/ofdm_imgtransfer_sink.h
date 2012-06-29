
/* $Id$ */

#ifndef INCLUDED_OFDM_IMGTRANSFER_SINK_H_
#define INCLUDED_OFDM_IMGTRANSFER_SINK_H_

#include <ofdm_api.h>
#include "gr_block_fwd.h"// forward declarations
#include <vector>
#include "util_random.h"
#include "util_bmp.h"
#include <gr_block.h>

#include <netdb.h>
#include <stdio.h>
typedef void* optval_t;


#include <sys/socket.h>
#include <arpa/inet.h>

#include <boost/thread/thread.hpp>


class ofdm_imgtransfer_sink;
typedef boost::shared_ptr<ofdm_imgtransfer_sink>
  ofdm_imgtransfer_sink_sptr;

OFDM_API ofdm_imgtransfer_sink_sptr
ofdm_make_imgtransfer_sink(unsigned int udppacketsize=512,
    std::string src_ip="127.0.0.1",
    unsigned short src_port=0,
    std::string dst_ip="127.0.0.1",
    unsigned short dst_port=45454,
    std::string filename="",
    bool do_compare=true);

#define REPETITIONS 20

class OFDM_API ofdm_imgtransfer_sink : public gr_block
{
private:
  ofdm_imgtransfer_sink(unsigned int udppacketsize,
      std::string src_ip,
      unsigned short src_port,
      std::string dst_ip,
      unsigned short dst_port,
      std::string filename,
      bool do_compare);

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

  std::vector<unsigned char> d_headerbuffer;
  std::vector<unsigned char> d_pixels;

  bool d_compare;
  bool d_printedequality;

  Bitmap d_compareimage;

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

  void
  forecast( int noutput_items,
    gr_vector_int &ninput_items_required );

  void decode_header();
  void write_buffer_to_file();

public:

  bool start();
  bool stop();

  static ofdm_imgtransfer_sink_sptr
  create(unsigned int udppacketsize,
      std::string src_ip,
      unsigned short src_port,
      std::string dst_ip,
      unsigned short dst_port,
      std::string filename,
      bool do_compare);

  float get_BER_estimate();

  virtual ~ofdm_imgtransfer_sink();

  int
  general_work(
    int                         noutput_items,
    gr_vector_int             & ninput_items,
    gr_vector_const_void_star & input_items,
    gr_vector_void_star       & output_items );

};

#endif /* INCLUDED_OFDM_IMGTRANSFER_SINK_H_ */
