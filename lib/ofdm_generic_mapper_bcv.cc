#ifdef HAVE_CONFIG_H
#include "config.h"
#endif

#include <gr_block.h>
#include <gr_io_signature.h>
#include <ofdm_generic_mapper_bcv.h>
#include <string.h>




#include <ofdmi_mod.h>

#include <vector>
#include <stdexcept>
#include <iostream>
#include <iostream>

#define DEBUG 0

ofdm_generic_mapper_bcv_sptr
ofdm_make_generic_mapper_bcv( int vlen )
{
  return ofdm_generic_mapper_bcv_sptr( new ofdm_generic_mapper_bcv( vlen ) );
}

ofdm_generic_mapper_bcv::ofdm_generic_mapper_bcv (int vlen)

  : gr_block("ofdm_generic_mapper_bcv",
      gr_make_io_signature3(3, 3, sizeof(char),                 // bit stream
                                  sizeof(char)*vlen,            // bitmap
                                  sizeof(char) ),               // trigger
      gr_make_io_signature (1, 1, sizeof(gr_complex)*vlen ) ),  // ofdm blocks

  d_vlen( vlen ),
  d_need_bits( 0 ),
  mod( new ofdmi_modem() ),
  d_need_bitmap( 1 ),
  d_bitmap( new char[vlen] )

{

  for( int i = 0; i < vlen; ++i ){
    d_bitmap[i] = 0;
  }

  if(DEBUG)
    std::cout << "[mapper " << unique_id() << "] vlen=" << vlen << std::endl;

}


static inline int
calc_bit_amount( const char* cv, const int& vlen )
{
  int bits_per_symbol = 0;
  for(int i = 0; i < vlen; ++i) {
    bits_per_symbol += cv[i];

    if(cv[i] > 8)
      throw std::out_of_range("MAPPER: More than 8 bits per symbol not supported");
    if(cv[i] < 0)
      throw std::out_of_range("MAPPER: Cannot allocate less than zero bits");
  }

  return bits_per_symbol;
}


void
ofdm_generic_mapper_bcv::forecast( int noutput_items,
    gr_vector_int &ninput_items_required )
{
  ninput_items_required[0] = d_need_bits;
  ninput_items_required[1] = d_need_bitmap;
  ninput_items_required[2] = noutput_items;
}


int
ofdm_generic_mapper_bcv::general_work(
    int noutput_items,
    gr_vector_int &ninput_items,
    gr_vector_const_void_star &input_items,
    gr_vector_void_star &output_items )
{

  const char *data = static_cast<const char*>(input_items[0]);
  const char *cv = static_cast<const char*>(input_items[1]);
  const char *trig = static_cast<const char*>(input_items[2]);

  gr_complex *blk = static_cast<gr_complex*>(output_items[0]);

  int n_bits = ninput_items[0];
  int n_cv = ninput_items[1];
  int n_trig = ninput_items[2];
  int nout = noutput_items;

  int n_min = std::min( nout, n_trig );


  if(DEBUG)
    std::cout << "[mapper " << unique_id() << "] entered, state is "
              << "n_bits=" << n_bits << " n_cv=" << n_cv
              << " n_trig=" << n_trig << " nout=" << nout
              << " d_need_bits=" << d_need_bits
              << " d_need_bitmap=" << d_need_bitmap << std::endl;

  bool copy = false;
  const char *map = d_bitmap.get();


  for( int i = 0; i < n_min; ++i, ++trig ){

    if( *trig == 1 ){

      if( n_cv > 0 ){

        // update bitmap buffer
        map = cv;


        d_need_bits = calc_bit_amount( map, d_vlen );

        // if not enough input, won't consume trigger, therefore
        // don't consume bitmap item
        if( n_bits < d_need_bits ){
          d_need_bitmap = 1;
          break;
        }


        copy = true;
        d_need_bitmap = 0;


        --n_cv; cv += d_vlen;
        consume(1, 1);



        if(DEBUG)
          std::cout << "Consume 1 bitmap item, leave " << n_cv << " items"
                    << " and need " << d_need_bits << " bits while "
                    << n_bits << " bits left" << std::endl;


      } else {

        if(DEBUG)
          std::cout << "Need bitmap flag set" << std::endl;

        d_need_bitmap = 1;
        break;

      } // n_cv > 0

    } // *trig == 1


    // check if we have enough bits

    if( n_bits < d_need_bits ){

      if(DEBUG)
        std::cout << "Do not have enough bits, need " << d_need_bits
                  << " have " << n_bits << std::endl;

      break;

    } // n_bits < d_need_bits


    if(DEBUG)
      std::cout << "Modulate" << std::endl;


    // modulate block
    for( int i = 0; i < d_vlen; ++i, ++blk ){
      if( map[i] == 0 ){

        *blk = gr_complex( 0.0, 0.0 );

      }else{

        mod->modulate( blk, data, map[i] );

      } // map[i] == 0

    } // for-loop

    --nout;
    n_bits -= d_need_bits;

  } // for-loop

  // store to internal state variable
  if( copy ){

    memcpy( d_bitmap.get(), map, d_vlen*sizeof(char) );

    if(DEBUG)
      std::cout << "Copy bitmap to internal state buffer" << std::endl;

  } // copy


  if(DEBUG)
    std::cout << "[mapper] Leaving process, d_need_bits=" << d_need_bits
              << " d_need_bitmap=" << d_need_bitmap << " consume "
              << ninput_items[0]-n_bits << " bits and consume/produce "
              << noutput_items-nout << " triggers/ofdm blocks"
              << std::endl;


  consume(0, ninput_items[0]-n_bits);

  int p = noutput_items - nout;
  consume(2, p); // trigger items

  return p;

}


int
ofdm_generic_mapper_bcv::noutput_forecast( gr_vector_int &ninput_items,
    int available_space, int max_items_avail, std::vector<bool> &input_done )
{

  if( ninput_items[0] < d_need_bits ){
    if( input_done[0] ){
      return -1;
    }

    return 0;
  }

  if( ninput_items[1] < d_need_bitmap ){
    if( input_done[1] ){
      return -1;
    }

    return 0;
  }

  if( ninput_items[2] == 0 && input_done[2] ){
    return -1;
  }

  return std::min( available_space, ninput_items[2] );

}
