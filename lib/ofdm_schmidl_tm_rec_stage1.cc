#ifdef HAVE_CONFIG_H
#include "config.h"
#endif

#include <gr_sync_block.h>
#include <gr_io_signature.h>
#include <ofdm_schmidl_tm_rec_stage1.h>

#include <cmath>

ofdm_schmidl_tm_rec_stage1_sptr
ofdm_make_schmidl_tm_rec_stage1( int fft_length )
{
  return ofdm_schmidl_tm_rec_stage1_sptr( new ofdm_schmidl_tm_rec_stage1(
      fft_length ) );
}

ofdm_schmidl_tm_rec_stage1::ofdm_schmidl_tm_rec_stage1( int fft_length )

  : gr_sync_block( "schmidl_tm_rec_stage1",
           gr_make_io_signature (1, 1, sizeof(gr_complex) ),
           gr_make_io_signature2(2, 2, sizeof(gr_complex), sizeof(float) ) ),

  d_fft_length( fft_length ),
  d_delay( fft_length/2 )

{

  set_history( d_delay + 1 );

}

int
ofdm_schmidl_tm_rec_stage1::work(
    int noutput_items,
    gr_vector_const_void_star &input_items,
    gr_vector_void_star &output_items )
{
  // NOTE: GCC likes temporary constants and simple expressions

  const gr_complex * in_del = static_cast<const gr_complex*>(input_items[0]);
  const gr_complex * in = in_del + d_delay;

  gr_complex * p = static_cast<gr_complex*>(output_items[0]);
  float * r = static_cast<float*>(output_items[1]);



  for( int i = 0; i < noutput_items; ++i ){

    float const x = in[i].real();
    float const y = in[i].imag();

    float const x2 = x*x;
    float const y2 = y*y;


    gr_complex const id = in_del[i];
    gr_complex const cid = std::conj( id );

    gr_complex const in_t = in[i];

    p[i] = cid * in_t;

    r[i] = x2 + y2;

  } // for-loop

  return noutput_items;
}
