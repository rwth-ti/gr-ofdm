#ifdef HAVE_CONFIG_H
#include "config.h"
#endif

#include <gr_block.h>
#include <gr_io_signature.h>
#include "ofdm_reference_data_source_ib.h"

#include <algorithm>
#include <iostream>

#define DEBUG 0

ofdm_reference_data_source_ib_sptr ofdm_make_reference_data_source_ib(const std::vector<int> &ref_data)
{
  return ofdm_reference_data_source_ib_sptr(new ofdm_reference_data_source_ib(ref_data));
}


void ofdm_reference_data_source_ib::forecast(int noutput_items, gr_vector_int &ninput_items_required)
{
  ninput_items_required[0] = 1;
}


ofdm_reference_data_source_ib::ofdm_reference_data_source_ib(const std::vector<int> &ref_data)
  : gr_block("reference_data_source_ib",
           gr_make_io_signature (1, 1, sizeof(unsigned int)),
           gr_make_io_signature (1, 1, sizeof(char))),
    d_produced(0)
{
  // unpack byte array
  d_ref_data.resize(ref_data.size()*8*10);
  for(std::vector<char>::size_type i = 0; i < ref_data.size()*8; ++i){
    std::vector<char>::size_type pos = i / 8, bpos = i % 8;
    std::vector<char>::value_type b = ((ref_data[pos] & 0xFF) >> bpos) & 0x01;
    d_ref_data[i] = b;
  }
  for(int i = 1; i < 10; ++i )
  {
    for( int j = 0; j < ref_data.size()*8; ++j )
    {
      d_ref_data[i*ref_data.size()*8 + j] = d_ref_data[j];
    }
  }

  // FIXME: generate longer random data



  d_bpos = d_ref_data.begin();



}

int ofdm_reference_data_source_ib::general_work(
    int noutput_items,
    gr_vector_int &ninput_items,
    gr_vector_const_void_star &input_items,
    gr_vector_void_star &output_items)
{
  const unsigned int *in = static_cast<const unsigned int*>(input_items[0]);
  char *out = static_cast<char*>(output_items[0]);

  if(DEBUG)
    std::cout << "[dref.src " << unique_id() << "] entered, state "
              << "nin=" << ninput_items[0] << " nout=" << noutput_items
              << " d_produced=" << d_produced
              << " in[0]=" << in[0]
              << std::endl;

  if(in[0] == 0){

      std::cerr << "warning: bitcount = 0" << std::endl;
      consume_each(1);
      return 0;

  } else if(in[0] > d_produced){

    assert( in[0] <= d_ref_data.size() );

    std::vector<char>::size_type p = std::min(
        static_cast<std::vector<char>::size_type>(in[0]-d_produced),
        static_cast<std::vector<char>::size_type>(noutput_items));

    if(DEBUG)
      std::cout << "produce " << p << " items" << std::endl;

    std::copy(d_bpos, d_bpos+p, out);
    d_bpos += p;
    d_produced += p;

    if(d_produced >= in[0]){
      d_bpos = d_ref_data.begin();
      d_produced = 0;
      consume_each(1);

      if(DEBUG)
        std::cout << "consume input value" << std::endl;
    }

    return p;

  }

  assert(false && "should never get here");
  return -1;
}
