#ifdef HAVE_CONFIG_H
#include "config.h"
#endif

#include <gr_block.h>
#include <gr_io_signature.h>
#include <ofdm_skip.h>

#include <cstring>

#include <algorithm>
#include <iostream>

ofdm_skip_sptr ofdm_make_skip(std::size_t itemsize, unsigned int blocklen)
{
  return ofdm_skip_sptr(new ofdm_skip(itemsize, blocklen));
}

ofdm_skip::ofdm_skip(std::size_t itemsize, unsigned int blocklen)
  : gr_block("skip",
           gr_make_io_signature2 (2, 2, itemsize, sizeof(char)),
           gr_make_io_signature2 (1, 2, itemsize, sizeof(char))),
  d_itemsize(itemsize), d_blocklen(blocklen), d_item(blocklen), d_skip(0),
  d_items(blocklen,false), d_first_item(blocklen,false)
{
  d_first_item[0] = true;

  //set_output_multiple(d_blocklen);
  set_relative_rate(1.0);
  set_fixed_rate(true);
}

int ofdm_skip::general_work (int noutput_items,
  gr_vector_int &ninput_items,
  gr_vector_const_void_star &input_items,
  gr_vector_void_star &output_items)
{
  const char *in = static_cast<const char*>(input_items[0]);
  const char *trigger = static_cast<const char*>(input_items[1]);
  char *out = static_cast<char*>(output_items[0]);

  char *filt_trigger = 0;

  if(output_items.size() > 1) {
    filt_trigger = static_cast<char*>(output_items[1]);
    memset(filt_trigger, 0, noutput_items);
  }

  int i = 0;
  int produced = 0;

  int i_max = std::min( ninput_items[0], ninput_items[1] );

  while( produced < noutput_items && i < i_max )
  {
    if( trigger[i] == 1 )
    { // reset
      d_item = 0;
    }

    if( d_item < d_items.size() )
    {
      if( d_items[d_item] ) // skip flag set
      {
	++d_item;
	++i;
	continue;
      }

      if(filt_trigger != 0)
      {
        if( d_first_item[d_item])
        {
  	  *filt_trigger = 1;
        }
        ++filt_trigger;
      }

      ++d_item;
    }


    // skip flag not set
    memcpy( out, in + i * d_itemsize, d_itemsize );
    out += d_itemsize;
    ++produced;

    ++i;
  } // for-loop

  consume_each( i );
  return produced;
}

void ofdm_skip::skip(unsigned int no)
{
  assert(no < d_blocklen);

  d_items[no] = true;
  ++d_skip;

  assert(d_skip < d_blocklen);

//  set_output_multiple(d_blocklen-d_skip);
  set_relative_rate(static_cast<float>(d_blocklen-d_skip)/d_blocklen);


  bool first = true;
  for(unsigned int i = 0; i < d_first_item.size(); ++i) {
    d_first_item[i] = false;
    if(!d_items[i]){
      d_first_item[i] = first;
      first = false;
    }
  }
}

void ofdm_skip::forecast (int noutput_items, gr_vector_int &ninput_items_required)
{
  int nreqd = fixed_rate_noutput_to_ninput(noutput_items);
  for(unsigned int i = 0; i < ninput_items_required.size(); ++i){
    ninput_items_required[i] = nreqd;
  }
}

int ofdm_skip::fixed_rate_noutput_to_ninput(int noutput_items)
{
  return noutput_items * d_blocklen/(d_blocklen-d_skip);
}

int ofdm_skip::fixed_rate_ninput_to_noutput(int ninput_items)
{
  return std::max(0U,ninput_items * (d_blocklen-d_skip)/d_blocklen);
}


int
ofdm_skip::noutput_forecast( gr_vector_int &ninput_items,
    int available_space, int max_items_avail, std::vector<bool> &input_done )
{

  if( ninput_items[0] < (d_blocklen-d_skip) && input_done[0] )
    return -1;

  if( ninput_items[1] < (d_blocklen-d_skip) && input_done[1] )
    return -1;


  if( max_items_avail == 0 )
    return 0;

  return available_space;

}
