#ifdef HAVE_CONFIG_H
#include "config.h"
#endif

#include <gr_block.h>
#include <gr_io_signature.h>
#include <ofdm_generic_demapper_vcb.h>

#include <ofdmi_mod.h>

#include <string.h>


#include <iostream>
#include <stdexcept>
#include <algorithm>

#define DEBUG 0


ofdm_generic_demapper_vcb_sptr ofdm_make_generic_demapper_vcb (int vlen)
{
  return ofdm_generic_demapper_vcb_sptr(new ofdm_generic_demapper_vcb(vlen));
}

ofdm_generic_demapper_vcb::ofdm_generic_demapper_vcb (int vlen)

  : gr_block("ofdm_generic_demapper_vcb",
      gr_make_io_signature3 (
          3, 3,
          sizeof(gr_complex)*vlen, // ofdm blocks
          sizeof(char)*vlen,       // bitmap
          sizeof(char)),           // update trigger
      gr_make_io_signature (
          1, 1,
          sizeof(char))),          // bitdata

    d_vlen( vlen ),
    d_items_req( 1 ),
    d_need_bitmap( 1 ),
    d_bitmap( new char[vlen] ),
    d_demod( new ofdmi_modem() )
{
  memset(d_bitmap.get(), 0, d_vlen);
  
  if( DEBUG > 0 )
    std::cout << "[demapper] create, id = " << unique_id() << std::endl;
}

ofdm_generic_demapper_vcb::~ofdm_generic_demapper_vcb()
{
}

static inline int
calc_bit_amount(const char* cv, int vlen)
{
  int bits_per_block = 0;
  for(int i = 0; i < vlen; ++i) {
    bits_per_block += cv[i];

    if(cv[i] > 8)
      throw std::out_of_range("DEMAPPER: More than 8 bits per symbol not supported");
    if(cv[i] < 0)
      throw std::out_of_range("DEMAPPER: Cannot allocate less than zero bits");
  }

  return bits_per_block;
}

void ofdm_generic_demapper_vcb::forecast (int noutput_items, gr_vector_int &ninput_items_required)
{
  // how may input items do we need _at least_
  // 1 bitmap, but 1 or more data vectors and trigger points if the last
  // bitmap will be used several times
  ninput_items_required[0] = d_items_req;
  ninput_items_required[1] = d_need_bitmap;
  ninput_items_required[2] = d_items_req;
}

int
ofdm_generic_demapper_vcb::general_work (
    int noutput_items,
    gr_vector_int &ninput_items,
    gr_vector_const_void_star &input_items,
    gr_vector_void_star &output_items)
{
  // input streams
  const gr_complex * sym_in = static_cast<const gr_complex*>(input_items[0]);
  const char * cv_in = static_cast<const char*>(input_items[1]);
  const char * trig = static_cast<const char*>(input_items[2]);

  // output streams
  char * out = static_cast<char*>(output_items[0]);

  memset( out, 0, noutput_items );
  
  // reset
  set_output_multiple( 1 );

  const int n_sym = ninput_items[0];
  int n_cv = ninput_items[1];
  const int n_trig = ninput_items[2];
  int nout = noutput_items;

  if(DEBUG)
    std::cout << "[demapper " << unique_id() << "] state, n_sym=" << n_sym
              << " n_cv=" << n_cv
              << " n_trig=" << n_trig << " nout=" << nout
              << std::endl;

  // use internal state variable
  const char * cv = d_bitmap.get();
  bool do_copy = false;


  const int n_min = std::min( n_sym, n_trig );
  int bps = calc_bit_amount( cv, d_vlen );
  int i;
  for( i = 0; i < n_min; ++i ){

    if( trig[i] != 0 )
    {
      if( n_cv == 0 )
      {
        d_need_bitmap = 1;
        break;
      }

      bps = calc_bit_amount( cv_in, d_vlen );
      if( nout < bps ) 
      {
        set_output_multiple( bps );
        break;
      }
        
      cv = cv_in;
      do_copy = true;
      d_need_bitmap = 0;
      --n_cv;
      cv_in += d_vlen;

    } // trig[i] != 0

    if( nout < bps )
    {
      set_output_multiple( bps );
      break;
    }

    // demodulation

    for( int x = 0; x < d_vlen; ++x ) {
      if( cv[x] == 0 )
        continue;

      d_demod->demodulate( sym_in[x], out, cv[x] ); //advances out
    }

    sym_in += d_vlen;
    nout -= bps;

  } // for-loop

  if( do_copy ){
    memcpy( d_bitmap.get(), cv, sizeof(char)*d_vlen );
  }

  assert( i <= ninput_items[0] && i <= ninput_items[2] && i >= 0 );
  assert( n_cv <= ninput_items[1] && n_cv >= 0 );
  consume( 1, ninput_items[1] - n_cv );
  consume( 0, i );
  consume( 2, i );
  
  if( DEBUG ) {
    std::cout << "[demapper] produced " << noutput_items-nout << " items"
              << " and consumed " << i << " symbols and triggers and "
              << ninput_items[1]-n_cv << " bitmap items" << std::endl;
  }

  assert( nout <= noutput_items && nout >= 0 );
  return noutput_items - nout;
}

int
ofdm_generic_demapper_vcb::noutput_forecast( gr_vector_int &ninput_items,
    int available_space, int max_items_avail, std::vector<bool> &input_done )
{

  // we don't know much about the rate.
  //  - if we have no input ofdm block, we won't produce anything
  //  - ofdm blocks and trigger items are consumed at the same rate
  //  - if we need a new bitmap and don't have one, we can't proceed
  //  - one item may need more output space we have but also zero

  if( ninput_items[1] < d_need_bitmap ){
    if( input_done[1] ){
      return -1;
    }

    return 0;
  }

  if( ninput_items[0] == 0 ){
    if( input_done[0] ){
      return -1;
    }
    return 0;
  }

  if( ninput_items[2] == 0 ){
    if( input_done[2] ){
      return -1;
    }
    return 0;
  }

  return available_space;

}

std::vector<gr_complex>
ofdm_generic_demapper_vcb::get_constellation( int bits )
{
  std::vector<gr_complex> x;
  try {
    
    x = d_demod->get_constellation( bits );
    
  } catch ( modulation_not_supported ex ) {
    
    std::cerr << "Error: requested modulation is not supported" << std::endl;
    
  } catch ( ... ) {
    
    throw;
    
  }
  
  return x;
}