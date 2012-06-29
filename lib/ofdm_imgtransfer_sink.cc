
/* $Id$ */

#ifdef HAVE_CONFIG_H
#include "config.h"
#endif

#include <gr_block.h>
#include <gr_io_signature.h>
#include <ofdm_imgtransfer_sink.h>
#include <iostream>
#include <algorithm>
#include <string.h>
#include <boost/date_time/posix_time/posix_time_types.hpp>

#include <boost/thread/thread.hpp>
#include <boost/bind.hpp>


#define DEBUG 0

ofdm_imgtransfer_sink::ofdm_imgtransfer_sink( unsigned int udppacketsize, std::string src_ip, unsigned short src_port,
    std::string dst_ip, unsigned short dst_port, std::string filename, bool do_compare)
  : gr_block(
      "imgtransfer_sink",
      gr_make_io_signature2(
        2, 2,
        sizeof( unsigned int ),
        sizeof(  char ) ),
      gr_make_io_signature(0,0,0) )

  , d_bitcount(0)
  , d_bitpos(0)
  , d_header(0)
  , d_udppacketsize(udppacketsize)
  , d_processedbyte(0)
  , d_pos(-1)
  , d_pixelpos(0)
  , d_packet_to_send(0)
  , d_compare(false)
  , d_udp_running(false)
  , d_payload_size( udppacketsize )
{
  assert( d_payload_size > 0 );


  if (filename!="")
    {
      std::cout << "Imagetransfer is in Comparemode\n";
      d_compareimage.load(filename);
      d_compare=do_compare;
    }
  else
    std::cout << "Imagetransfer is in Standardmode\n";
  std::cout << "Initialized Imagetransfer Sink!\n";
  d_headerbuffer.resize(32*REPETITIONS,0);

  d_width=256; d_height=256;
  if (d_compare)
    {
      d_width=d_compareimage.get_width(); d_height=d_compareimage.get_height();
    }
  d_pixels.resize(d_width*d_height*3,0);

  random_generator.load_from_file("random.txt");


  int ret = 0;
  // Set up the address stucture for the source address and port numbers
  // Get the source IP address from the host name
  struct hostent *hsrc = gethostbyname(src_ip.c_str());
  if(hsrc) {   // if the source was provided as a host namex
    d_ip_src = *(struct in_addr*)hsrc->h_addr_list[0];
  }
  else { // assume it was specified as an IP address
    if((ret=inet_aton(src_ip.c_str(), &d_ip_src)) == 0) {            // format IP address
      perror("Not a valid source IP address or host name");
      //return -1;
    }
  }

  // Get the destination IP address from the host name
  struct hostent *hdst = gethostbyname(dst_ip.c_str());
  if(hdst) {   // if the source was provided as a host namex
    d_ip_dst = *(struct in_addr*)hdst->h_addr_list[0];
  }
  else { // assume it was specified as an IP address
    if((ret=inet_aton(dst_ip.c_str(), &d_ip_dst)) == 0) {            // format IP address
      perror("Not a valid destination IP address or host name");
      //return -1;
    }
  }

  d_port_src = htons(src_port);           // format port number
  d_port_dst = htons(dst_port);           // format port number

  d_sockaddr_src.sin_family = AF_INET;
  d_sockaddr_src.sin_addr   = d_ip_src;
  d_sockaddr_src.sin_port   = d_port_src;

  d_sockaddr_dst.sin_family = AF_INET;
  d_sockaddr_dst.sin_addr   = d_ip_dst;
  d_sockaddr_dst.sin_port   = d_port_dst;

  d_udp_running=udp_open();


}

bool
ofdm_imgtransfer_sink ::
start()
{
  boost::thread mythread(boost::bind(&ofdm_imgtransfer_sink::udp_send_pixels, this));
  d_udp_thread = mythread.move();
  return true;
}

bool
ofdm_imgtransfer_sink ::
stop()
{
  d_udp_thread.interrupt();
  d_udp_thread.join(); // FIXME this may wait forever if the thread doesn't return
  return true;
}

ofdm_imgtransfer_sink ::
~ofdm_imgtransfer_sink()
{
  if(d_udp_thread.joinable())
  {
    d_udp_thread.interrupt();
    d_udp_thread.join(); // FIXME this may wait forever if the thread doesn't return
  }
}

bool ofdm_imgtransfer_sink::udp_open()
{
  // create socket
  if((d_socket = socket(AF_INET, SOCK_DGRAM, IPPROTO_UDP)) == -1) {
    perror("socket open");
    return false;
  }

  // Turn on reuse address
  int opt_val = true;
  if(setsockopt(d_socket, SOL_SOCKET, SO_REUSEADDR, (optval_t)&opt_val, sizeof(int)) == -1) {
    perror("SO_REUSEADDR");
    return false;
  }

  // Don't wait when shutting down
  linger lngr;
  lngr.l_onoff  = 1;
  lngr.l_linger = 0;
  if(setsockopt(d_socket, SOL_SOCKET, SO_LINGER, (optval_t)&lngr, sizeof(linger)) == -1) {
    perror("SO_LINGER");
    return false;
  }

  // bind socket to an address and port number to listen on
  if(bind (d_socket, (sockaddr*)&d_sockaddr_src, sizeof(struct sockaddr)) == -1) {
    perror("socket bind");
    return false;
  }

  // Not sure if we should throw here or allow retries
  if(connect(d_socket, (sockaddr*)&d_sockaddr_dst, sizeof(struct sockaddr)) == -1) {
    perror("socket connect");
    return false;
  }

  return d_socket != 0;
}

void ofdm_imgtransfer_sink::udp_send_pixels()
{
  unsigned int count=d_udppacketsize-4;
  unsigned char* temp_buffer=(unsigned char*)malloc(count+4);
  int ctr = 0;
  try
  {
    while( ! boost::this_thread::interruption_requested() )
    {

      unsigned int start=d_packet_to_send*count;

      ssize_t r=0, bytes_sent=0, bytes_to_send=0;
      ssize_t total_size = count+4;

//      std::cout << "start send" << std::endl << std::flush;

      start%=d_width*d_height*3;


      *((unsigned int*)temp_buffer)=start;
      if ((d_width*d_height*3-start)>count)
        {
          memcpy(&temp_buffer[4],&d_pixels.data()[start],count);
        }
      else
        {
          memcpy(&temp_buffer[4],&d_pixels.data()[start],d_width*d_height*3-start);
          memcpy(&temp_buffer[4+d_width*d_height*3-start],&d_pixels.data()[0],count-d_width*d_height*3+start);
        }


      while(bytes_sent <  total_size) {
//        std::cout << "bytes to send " << bytes_to_send
//                  << " payloadsize=" << d_payload_size
//                  << " total_size=" << total_size
//                  << " bytes_sent=" << bytes_sent
//                  << std::endl;
        bytes_to_send = std::min((ssize_t)d_payload_size, (total_size-bytes_sent));
        if(bytes_to_send == 0)
          break;

        r = send(d_socket,temp_buffer, bytes_to_send, 0);
        if(r == -1) {         // error on send command
//          perror("udp_sink"); // there should be no error case where this function
          //return -1;          // should not exit immediately
        }
        bytes_sent += r;
      }

//      std::cout << "stop send" << std::endl << std::flush;

      d_packet_to_send++;

      boost::this_thread::sleep( boost::posix_time::milliseconds(200) );
      ++ctr;
      if( ctr >= 5 )
      {
        ctr = 0;
  //      std::cout << "BER: " << get_BER_estimate() << " ";
      }

    } // while ! interruption requested
  }
  catch( boost::thread_interrupted const & ex )
  {
    std::cout << "img xfer thread interrupted" << std::endl;
  }

  std::cout << "img xfer thread returned" << std::endl;

}

void ofdm_imgtransfer_sink::udp_close()
{
  if (d_socket){
    shutdown(d_socket, SHUT_RDWR);
    d_socket = 0;
  }
}

void ofdm_imgtransfer_sink::decode_header()
{
  std::vector<char> bits;
  d_header=0;
  bits.resize(32,0);
  for (int i=0; i<32*REPETITIONS; ++i)
  {
    bits[i%32]+=d_headerbuffer[i];
  }
  for (int i=0; i<32; ++i)
  {
    d_header<<=1;
    d_header+=bits[i]>(REPETITIONS/2);
  }
}

void
ofdm_imgtransfer_sink::forecast( int noutput_items,
  gr_vector_int &ninput_items_required )
{
  ninput_items_required[0] = 1;
  if (d_pos < 32*REPETITIONS)
    ninput_items_required[1] = 32*REPETITIONS;
  else
    ninput_items_required[1] = noutput_items*8;
}

int
ofdm_imgtransfer_sink::general_work(
  int                         noutput_items,
  gr_vector_int             & ninput_items,
  gr_vector_const_void_star & input_items,
  gr_vector_void_star       & output_items )
{
  const unsigned int *in = static_cast< const unsigned int* >( input_items[0] );
  const unsigned char *in_1 = static_cast< const unsigned char* >( input_items[1] );
//  unsigned char *out = static_cast< unsigned char* >( output_items[0] );

  /* last time bitcount has been reached or first call of function */
  if (d_pos<0)
  {
    if (ninput_items[0]==0) return 0;
    /* read new bitcount */
    d_bitcount = in[0];
    d_pos=0;          //counts the bit to read
    random_generator.reset();
  }

  /* either I read the elements remaining until next header or all the bits */
  int ninput = (int)(std::min)((unsigned int)ninput_items[1],(unsigned int)(d_bitcount-d_pos));
  for (int i=0; i<ninput; ++i)
  {
    if ((i+d_pos)<32*REPETITIONS)
    {
      d_headerbuffer[d_pos+i]=in_1[i]^random_generator.rand_bit();
    }
    else
    {
      if ((i+d_pos)==32*REPETITIONS)
      {
        decode_header();
        d_pixelpos = d_header%(d_width*d_height*3);
      }
      if (d_pixelpos>=d_width*d_height*3) d_pixelpos -= d_width*d_height*3;
      d_processedbyte<<=1;
      d_processedbyte+=in_1[i]^random_generator.rand_bit();
      ++d_bitpos;
      if (d_bitpos==8)
      {
        d_pixels[d_pixelpos]=d_processedbyte;
        d_bitpos=0;
        d_processedbyte=0;
        ++d_pixelpos;
      }
    }
  }
  d_pos+=ninput;
  /* in the for loop above I read ninput bits */
  consume(1,ninput);

  if (d_compare)
    {
      if ((time(NULL)%2)==0)
        {
          if (!d_printedequality)
            {
              unsigned int equals=0;
              unsigned char* pixels;
              d_compareimage.get_bytepointer(0,&pixels);
              for (unsigned int i=0; i<d_compareimage.get_width()*d_compareimage.get_height(); ++i)
                if (pixels[i]==d_pixels[i]) ++equals;
              std::cout << "Equality: " << (double)equals/(double)(d_compareimage.get_width()*d_compareimage.get_height()) << "\n";
              d_printedequality=true;
              std::cout << "BER: " << get_BER_estimate()<< std::endl;
            }
        }
      else
        d_printedequality=false;
    }

  /* I received d_bitcount bits and therefore I will begin to read the new bitcount nxt time */
  if ((unsigned)d_pos==d_bitcount)
  {
    d_processedbyte=0;
    d_bitpos=0;
    consume(0,1);
    d_pos=-1;

//    unsigned int d_time=(boost::posix_time::microsec_clock::local_time()-boost::posix_time::ptime(boost::gregorian::date(1970,1,1))).total_milliseconds();
//    if ((d_time-d_lasttime)>50)
//      {
//        boost::thread mythread(boost::bind(&ofdm_imgtransfer_sink::udp_send_pixels, this));
//        udp_send_pixels(d_packet_to_send*d_udppacketsize,d_udppacketsize);
//        ++d_packet_to_send;
//        d_lasttime=d_time;
//      }
  }

  return noutput_items;
}

static
int
bitcount (unsigned int n)
{
   int count = 0 ;
   while (n)  {
      count++ ;
      n &= (n - 1) ;
   }
   return count ;
}


float
ofdm_imgtransfer_sink ::
get_BER_estimate()
{
  unsigned char * pixels;
  unsigned int bit_errors = 0;
  d_compareimage.get_bytepointer(0,&pixels);
  for (unsigned int i=0; i<d_pixels.size(); ++i)
  {
    unsigned int cmp = pixels[i] ^ d_pixels[i];
    int const d = bitcount( cmp );
    bit_errors += d;
  }

  unsigned int const nbits = d_pixels.size()*8;

  float BER = static_cast< float >( bit_errors ) / nbits;

  return BER;
}


ofdm_imgtransfer_sink_sptr
ofdm_make_imgtransfer_sink(unsigned int udppacketsize,
    std::string src_ip,
    unsigned short src_port,
    std::string dst_ip,
    unsigned short dst_port,
    std::string filename,
    bool do_compare)
{
  return ofdm_imgtransfer_sink::create(udppacketsize,src_ip,src_port,dst_ip,dst_port,filename, do_compare);
}


ofdm_imgtransfer_sink_sptr
ofdm_imgtransfer_sink::create(unsigned int udppacketsize,
    std::string src_ip,
    unsigned short src_port,
    std::string dst_ip,
    unsigned short dst_port,
    std::string filename,
    bool do_compare)
{
  try
  {
    ofdm_imgtransfer_sink_sptr tmp(
      new ofdm_imgtransfer_sink( udppacketsize,src_ip,src_port,dst_ip,dst_port,filename, do_compare ) );

    return tmp;
  }
  catch ( ... )
  {
    std::cerr << "[ERROR] Caught exception at creation of "
              << "ofdm_imgtransfer_sink" << std::endl;
    throw;
  } // catch ( ... )
}



