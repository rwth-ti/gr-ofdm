
/* $Id: ofdm_LMS_phase_tracking3.cc 1076 2009-07-06 13:32:06Z auras $ */

#ifdef HAVE_CONFIG_H
#include "config.h"
#endif

#include <gr_sync_block.h>
#include <gr_io_signature.h>
#include <ofdm_LMS_phase_tracking3.h>

#include <ofdmi_fast_math.h>

#include <gr_expj.h>

#include <iostream>
#include <algorithm>

#define DEBUG 0

#if DEBUG > 1
#define ASSERT_(x) assert((x))
#else
#define ASSERT_(x)
#endif


ofdm_LMS_phase_tracking3 ::
ofdm_LMS_phase_tracking3( int vlen,
  std::vector< int > const & pilot_subc,
  std::vector< int > const & nondata_blocks,
  std::vector< gr_complex > const & pilot_subcarriers)

  : gr_sync_block(
      "LMS_phase_tracking3",
      gr_make_io_signature2(
        2, 2,
        sizeof( gr_complex ) * vlen,
        sizeof( char ) ),
      gr_make_io_signature(
        1, 1,
        sizeof( gr_complex ) * vlen ) )

  , d_vlen( vlen )

  , d_acc_gamma( 0.0 )
  , d_acc_b( 0.0 )
  , d_pcount( pilot_subc.size() )
  , d_blk( 0 )
  , d_in_da(0)
  , d_pilot_tone(pilot_subcarriers)

{
  assert( ( vlen % 2 ) == 0 );
  init_LMS_phasetracking( pilot_subc, nondata_blocks );
}


void
ofdm_LMS_phase_tracking3 ::
init_LMS_phasetracking(
    std::vector< int > const & pilot_tones,    //[-91 -65 -39 -13  13  39  65  91]
    std::vector< int > const & nondata_block ) //[0 1]
{
  // LMS phasetracking init

  if( nondata_block.size() > 0 )
  {

    // LUT: identify non data blocks
    int max = *std::max_element(nondata_block.begin(), nondata_block.end());
    d_nondata_block.resize(max+1,false);
    for(unsigned int i = 0; i < nondata_block.size(); ++i) {
      d_nondata_block[nondata_block[i]] = true;

      if(DEBUG)
        std::cout << "LUT non data block: " << nondata_block[i] << std::endl;
    }

  }
  else
  {
    d_nondata_block.clear();
  }

  // phase compensation accumulator pilot subcarrier
  d_acc_phase.resize(d_pcount,0.0);
  d_phase_last.resize(d_vlen,0.0);
  //d_ina.resize(d_vlen,0.0);

  // LUT: identify pilot subcarrier
  //d_pilot_tone.resize(d_pcount,1.0+ 1.0*j); // FIXME allow different pilot tone value
  d_is_pilot.resize(d_vlen,false);
  d_pilot.resize(d_pcount);

  float x = 0.0;
  float y = 0.0;
  for(int i = 0; i < d_pcount; ++i){
    x += static_cast<float>(pilot_tones[i]*pilot_tones[i]);
    y += static_cast<float>(pilot_tones[i]);

    d_pilot[i] = pilot_tones[i]+d_vlen/2;
    d_is_pilot[d_pilot[i]] = true;
    ASSERT_( d_pilot[i] < d_vlen && d_pilot[i] >= 0 );
  }


  // init LMS algorithm parameter
  float fN = static_cast<float>(d_pcount);
  float c = x*fN-y*y;
  float a = fN/c;
  float b = -y/c;

  d_gamma_coeff.resize(d_pcount);
  for(int i = 0; i < d_pcount; ++i)
  {
    d_gamma_coeff[i] = static_cast<float>(pilot_tones[i])*a+b;

    if(DEBUG)
      std::cout << "gamma["<<i<<"]=" << d_gamma_coeff[i] << std::endl;
  }

} // init_LMS_phase_tracking



inline void
ofdm_LMS_phase_tracking3 ::
LMS_phasetracking(
  gr_complex const * in,
  gr_complex * out )
{

  // LMS phase tracking algorithm

	//for( int i = 0; i < d_vlen; ++i )
		//  {
		//	d_ina[i] = in[i] * gr_expj( -d_phase_last[i] );
		 // }
	//std::vector< gr_complex const> &d_ina = &in*gr_expj( -&d_phase_last );

	//gr_complex ds = in[1] * gr_expj( -d_phase_last[1] );

  float gamma = 0.0;
  float b = 0.0;

  //int in_da = 0;

  ASSERT_( d_pcount == d_pilot.size() );

  // LMS coefficient adaptation
  for( int i = 0; i < d_pcount; ++i )
  {
    ASSERT_( i < d_pilot.size() );
    const int ind = d_pilot[i];

    ASSERT_( ind < d_vlen && ind >= 0 );
    gr_complex pilot = in[ind];

    if( DEBUG )
    {
      std::cout << "LMS: pilot is " << pilot << " at " << ind << std::endl
                << "at " << ind-1 << ": " << in[ind-1] << std::endl
                << "at " << ind+1 << ": " << in[ind+1] << std::endl;
    }

    // precompensation on pilot subcarrier
    ASSERT_(i >= 0 && i < d_acc_phase.size());
    //pilot *= gr_expj( -d_acc_phase[i] );
    pilot *= gr_expj( -d_acc_phase[i] );




    ASSERT_( i < d_pilot_tone.size() );


    gr_complex const x = pilot / d_pilot_tone[i];
    float const beta = std::atan2( x.imag(), x.real() );

    if( DEBUG )
       {
         std::cout << "BETA:  " << beta << " at " << ind << std::endl;
       }

    d_acc_phase[i] += beta;




    ASSERT_( i < d_gamma_coeff.size() );
    gamma += d_gamma_coeff[i]*d_acc_phase[i];
    b += d_acc_phase[i];

    ASSERT_( i < d_acc_phase.size() );
    //d_acc_phase[i] += beta;

  } // for-loop over pilot subcarrier

  b /= static_cast<float>(d_pcount);


  if(DEBUG)
    std::cout << "LMS parameters: gamma=" << gamma
              << " b=" << b <<  "d_in_da: " << d_in_da << std::endl;

  //d_in_da++;
  //d_acc_b = ((d_acc_b)*(1+1.0/d_in_da)*(d_in_da-1) +b)/d_in_da;
  //d_acc_gamma = (d_acc_gamma*(1+1.0/d_in_da)*(d_in_da-1) +gamma)/d_in_da;

  d_acc_b = b;
  d_acc_gamma = gamma;

  // phase compensation, includes accumulated estimates

  float const phase_slope = -d_acc_gamma;
  //float const phase_slope = -gamma;


  float const init_phase = phase_slope * (-d_vlen/2) - d_acc_b;
  //float const init_phase = phase_slope * (-d_vlen/2) - b;
  //float const init_phase = phase_slope  - (b);

  //std::vector< gr_complex >  ina2 = d_ina;

  perform_frequency_shift( in, out, d_vlen, init_phase, phase_slope );

  //for( int j = 0; j < d_vlen; ++j )
  //{out[j] = in[j]*gr_expj((j-d_vlen/2)*phase_slope -d_acc_b);}//+ d_vlen/2*gamma);}

  //for( int j = d_vlen/2+1; j < d_vlen; ++j )
   // {out[j] = in[j]*gr_expj(-(j-d_vlen/2)*phase_slope -b - d_vlen/2*gamma);}


//  gr_complex phasor = gr_expj( -init_phase );
//  const gr_complex phasor_step = gr_expj( -d_acc_gamma );
//
//  for(int i = 0; i < d_vlen; ++i )
//  {
//    out[i] = in[i] * phasor;
//    phasor *= phasor_step;
//  } // for-loop

  if( DEBUG )
    std::cout << "LMS: acc_b=" << d_acc_b << " acc_gamma=" << d_acc_gamma
              << std::endl;

} // LMS_phase_tracking




int
ofdm_LMS_phase_tracking3 ::
work(
  int                         noutput_items,
  gr_vector_const_void_star & input_items,
  gr_vector_void_star       & output_items )
{
  gr_complex const * in = static_cast< gr_complex const * >( input_items[0] );
  char const * frame_start = static_cast< char const * >( input_items[1] );
  gr_complex * out = static_cast< gr_complex * >( output_items[0] );

  for( int i = 0; i < noutput_items;
       ++i, in += d_vlen, out += d_vlen, ++d_blk )
  {
    if( frame_start[i] != 0 )
    {
      d_acc_phase.assign( d_acc_phase.size(), 0.0 );
      d_phase_last.assign( d_phase_last.size(), 0.0 );
      d_acc_gamma = d_acc_b = 0.0;
      d_blk = 0;
      d_in_da = 0;

    } // if frame_start[i] != 0

    // No tracking on non-data OFDM blocks
    if( d_blk < (signed)d_nondata_block.size() && d_nondata_block[ d_blk ] )
    {
      if( DEBUG )
        std::cout << "LMS: non data block" << std::endl;

      std::copy( in, in + d_vlen, out );
      continue;
    }

    LMS_phasetracking( in, out );


  } // for-loop over input

  if( DEBUG )
    std::cout << "LMS: leave, nout=" << noutput_items
              << " d_blk=" << d_blk << std::endl;

  return noutput_items;

} // work


ofdm_LMS_phase_tracking3_sptr
ofdm_make_LMS_phase_tracking3( int vlen,
  std::vector< int > const & pilot_subc,
  std::vector< int > const & nondata_blocks,
  std::vector< gr_complex > const & pilot_subcarriers)
{
  return ofdm_LMS_phase_tracking3::create( vlen, pilot_subc, nondata_blocks,pilot_subcarriers );
}


ofdm_LMS_phase_tracking3_sptr
ofdm_LMS_phase_tracking3 ::
create( int vlen,
  std::vector< int > const & pilot_subc,
  std::vector< int > const & nondata_blocks,
  std::vector< gr_complex > const & pilot_subcarriers)
{
  try
  {
    ofdm_LMS_phase_tracking3_sptr tmp(
      new ofdm_LMS_phase_tracking3( vlen, pilot_subc, nondata_blocks, pilot_subcarriers ) );

    return tmp;
  }
  catch ( ... )
  {
    std::cerr << "[ERROR] Caught exception at creation of "
              << "ofdm_LMS_phase_tracking3" << std::endl;
    throw;
  } // catch ( ... )
}



