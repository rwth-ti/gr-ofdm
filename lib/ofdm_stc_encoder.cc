#ifdef HAVE_CONFIG_H
#include "config.h"
#endif

#include <gr_sync_block.h>
#include <gr_io_signature.h>
#include "ofdm_stc_encoder.h"

#include <iostream>
#include <algorithm>

#define DEBUG 0


ofdm_stc_encoder ::
ofdm_stc_encoder( int vlen, int num_symbols, std::vector< int > const & pilot_subcarriers )
  : gr_sync_block(
      "stc_encoder",
      gr_make_io_signature(
        1, 1,
        sizeof( gr_complex ) * vlen ),          // ofdm_blocks
      gr_make_io_signature2(
        2, 2,
        sizeof( gr_complex ) * vlen,            // encoded ofdm_blocks
        sizeof( gr_complex ) * vlen ) )			// encoded ofdm_blocks2

  , d_vlen( vlen )
  , d_num_symbols( num_symbols )
  , d_pcount( pilot_subcarriers.size() )
  , d_pilot_tone(pilot_subcarriers)

{
  assert( ( vlen % 2 ) == 0 ); // alignment 16 byte
  //init_stc_encoder( pilot_subcarriers );
}

//void
//ofdm_stc_encoder ::
//init_stc_encoder(std::vector< int > const &pilot_tones)
//    {
//    d_pilot_tone.resize(d_pcount);
//    for(int i = 0; i < d_pcount; ++i){
//        d_pilot_tone[i] = pilot_tones[i];
//        std::cout << "LMS: pilot is " << d_pilot_tone[i] << std::endl;
//      }
//    }// init_stc_encoder

int
ofdm_stc_encoder ::work (
        int                         noutput_items,
        gr_vector_const_void_star & input_items,
        gr_vector_void_star       & output_items )
{
  gr_complex const * ofdm_blocks = static_cast< gr_complex const * >( input_items[0] );
  gr_complex * out = static_cast< gr_complex * >( output_items[0] );
  gr_complex * out2 = static_cast< gr_complex * >( output_items[1] );

  int k = 0;
  int kk = 0;
  gr_complex norm_c = sqrt(2);
  gr_complex null = 0.0;

  for( int j = 0; j < noutput_items*d_vlen; ++j )
  {
      //std::cout << "LMS: k is " << k << std::endl;
      //std::cout << "LMS: pilot is " << d_pilot_tone[k] << std::endl;
//      std::cout << "LMS: pilot is " << d_pilot_tone[0] << std::endl;
//      std::cout << "LMS: pilot is " << d_pilot_tone[1] << std::endl;
//      std::cout << "LMS: pilot is " << d_pilot_tone[7] << std::endl;
      if (j == d_pilot_tone[k] + kk*d_vlen || j == d_pilot_tone[k]+1+ kk*d_vlen)
        {
          //std::cout << "LMS: pilot is " << d_pilot_tone[k] << std::endl;
          if( j % 2 == 0 )
        {
          out[j] =  norm_c*ofdm_blocks[j];
          out2[j] = 0.0;
          //std::cout << "LMS: out2 is " << out[j] << std::endl;
          //std::cout << "LMS: out2 is " << out2[j] << std::endl;
        } else {
            out[j] = - norm_c*std::conj( ofdm_blocks[j] );
            out2[j] = null;
            //k++;
           if (k == d_pilot_tone.size()-1)
                              {k=0;
                              kk++;}
                          else
                              k++;
        }

        }
      else
      {
          if( j % 2 == 0 )
              {
                out[j] = ofdm_blocks[j];
                out2[j] = ofdm_blocks[j+1];
              } else {
                  out[j] = - std::conj( ofdm_blocks[j] );
                  out2[j] = std::conj( ofdm_blocks[j-1] );
              }
      }
  }

  return noutput_items;

} // general_work

ofdm_stc_encoder_sptr
ofdm_make_stc_encoder( int vlen, int num_symbols, std::vector< int > const & pilot_subcarriers  )
{
  return ofdm_stc_encoder::create( vlen, num_symbols, pilot_subcarriers  );
}

ofdm_stc_encoder_sptr
ofdm_stc_encoder ::
create( int vlen, int num_symbols, std::vector< int > const & pilot_subcarriers  )
{
  try
  {
    ofdm_stc_encoder_sptr tmp(
      new ofdm_stc_encoder( vlen, num_symbols, pilot_subcarriers ) );

    return tmp;
  }
  catch ( ... )
  {
    std::cerr << "[ERROR] Caught exception at creation of "
              << "ofdm_stc_encoder" << std::endl;
    throw;
  } // catch ( ... )
}

