/* -*- c++ -*- */
/* 
 * Copyright 2013 <+YOU OR YOUR COMPANY+>.
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

#ifdef HAVE_CONFIG_H
#include "config.h"
#endif

#include <gnuradio/io_signature.h>
#include "lms_phase_tracking_03_impl.h"

#include "ofdm/ofdmi_fast_math.h"

#include <gnuradio/expj.h>

#include <iostream>
#include <algorithm>
#include "malloc16.h"

#define DEBUG 0

#if DEBUG > 1
#define ASSERT_(x) assert((x))
#else
#define ASSERT_(x)
#endif

namespace gr {
  namespace ofdm {

    lms_phase_tracking_03::sptr
    lms_phase_tracking_03::make(int vlen, const std::vector<int> &pilot_subc, std::vector< int > const &nondata_blocks, std::vector< gr_complex > const &pilot_subcarriers, int dc_null)
    {
      return gnuradio::get_initial_sptr
        (new lms_phase_tracking_03_impl(vlen, pilot_subc, nondata_blocks, pilot_subcarriers, dc_null));
    }

    /*
     * The private constructor
     */
    lms_phase_tracking_03_impl::lms_phase_tracking_03_impl(int vlen, const std::vector<int> &pilot_subc, std::vector< int > const &nondata_blocks, std::vector< gr_complex > const &pilot_subcarriers, int dc_null)
      : gr::block("lms_phase_tracking_03",
              gr::io_signature::make3(
            	       3, 3,
            	        sizeof( gr_complex ) * vlen,
            	        //sizeof( gr_complex ) * vlen,
            	        sizeof( gr_complex ) * vlen/2,
            	       // sizeof( gr_complex ) * vlen/2,
            	        sizeof( char ) ),
              gr::io_signature::make(1, 1, sizeof( gr_complex ) * vlen))
		, d_vlen( vlen )
		, d_dc_null( dc_null )
		, d_acc_gamma( 0.0 )
		, d_acc_b( 0.0 )
		, d_pcount( pilot_subc.size() )
		, d_blk( 0 )
		, d_in_da(0)
		, d_pilot_tone(pilot_subcarriers)
		, d_need_input_h1( 1 )
		, d_buffer_h1( static_cast< gr_complex * >( malloc16Align( sizeof( gr_complex ) * vlen/2 ) ) )
    //, d_need_input_h2( 1 )
    //, d_buffer_h2( static_cast< gr_complex * >( malloc16Align( sizeof( gr_complex ) * vlen/2 ) ) )
    //, d_buffer_in2( static_cast< gr_complex * >( malloc16Align( sizeof( gr_complex ) * vlen ) ) )
    {
    	  assert( ( vlen % 2 ) == 0 );
    	  init_LMS_phasetracking( pilot_subc, nondata_blocks, d_dc_null );
    }

    /*
     * Our virtual destructor.
     */
    lms_phase_tracking_03_impl::~lms_phase_tracking_03_impl()
    {
    	  if( d_buffer_h1 )
    	    free16Align( d_buffer_h1 );
    	  //if( d_buffer_h2 )
    	   // free16Align( d_buffer_h2 );
    }

    void
    lms_phase_tracking_03_impl::forecast (int noutput_items, gr_vector_int &ninput_items_required)
    {
      /* <+forecast+> e.g. ninput_items_required[0] = noutput_items */
	  ninput_items_required[0] = ninput_items_required[2] =  noutput_items;
	  ninput_items_required[1] = d_need_input_h1;
    }

    void
    lms_phase_tracking_03_impl ::
    init_LMS_phasetracking(
        std::vector< int > const & pilot_tones,    //[-91 -65 -39 -13  13  39  65  91]
        std::vector< int > const & nondata_block,
        int dc_nulled) //[0 1]
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


      // LUT: identify pilot subcarrier
      d_pilot_tone.resize(d_pcount,2.0); // FIXME allow different pilot tone value
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
    lms_phase_tracking_03_impl ::
    LMS_phasetracking(
      gr_complex const * in_1,
      gr_complex const * inv_ctf_1,
      gr_complex * out )
    {

      // LMS phase tracking algorithm

      float gamma = 0.0;
      float b = 0.0;

      ASSERT_( d_pcount == d_pilot.size() );

      // LMS coefficient adaptation
      for( int i = 0; i < d_pcount; ++i )
      {
        ASSERT_( i < d_pilot.size() );
        const int ind = d_pilot[i];
        const int ind_ctf = static_cast<int>((static_cast<float>(d_pilot[i]))/2);
        //const int ind_ctf = static_cast<int>((static_cast<float>(d_pilot[i]) - 1.0)/2) + 1;

        ASSERT_( ind < d_vlen && ind >= 0 );
        //gr_complex pilot = in_1[ind] + in_2[ind];
        gr_complex pilot = in_1[ind]*inv_ctf_1[ind_ctf];// + in_2[ind]*inv_ctf_2[ind_ctf];
        //std::cout << "LMS: pilot is " << pilot << " at " << ind << std::endl;

        if( DEBUG )
        {
          std::cout << "LMS: pilot is " << pilot << " at " << ind << std::endl
                    << "at " << ind-1 << ": " << in_1[ind-1] << std::endl
                    << "at " << ind+1 << ": " << in_1[ind+1] << std::endl;
        }

        // precompensation on pilot subcarrier
        ASSERT_(i >= 0 && i < d_acc_phase.size());
        pilot *= gr_expj( -d_acc_phase[i] );



        ASSERT_( i < d_pilot_tone.size() );
        gr_complex const x = pilot * d_pilot_tone[i];
        float const beta = std::atan2( x.imag(), x.real() );

        ASSERT_( i < d_gamma_coeff.size() );
        gamma += d_gamma_coeff[i]*beta;
        b += beta;

        ASSERT_( i < d_acc_phase.size() );
        d_acc_phase[i] += beta;

      } // for-loop over pilot subcarrier


      b /= static_cast<float>(d_pcount);

      if(DEBUG)
        std::cout << "LMS parameters: gamma=" << gamma
                  << " b=" << b << std::endl;
      //b = 0;
      //gamma = 0;
      d_acc_b += b;
      d_acc_gamma += gamma;

    if(0)
        std::cout << "LMS parameters: d_acc_gamma=" << d_acc_gamma
                  << " d_acc_b =" << d_acc_b << std::endl;

      // phase compensation, includes accumulated estimates

      float const phase_slope = -d_acc_gamma;

      float const init_phase = phase_slope * (-d_vlen/2) - d_acc_b;
      perform_frequency_shift( in_1, out, d_vlen, init_phase, phase_slope );

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
    lms_phase_tracking_03_impl::general_work (int noutput_items,
                       gr_vector_int &ninput_items,
                       gr_vector_const_void_star &input_items,
                       gr_vector_void_star &output_items)
    {
    	gr_complex const * in_1 = static_cast< gr_complex const * >( input_items[0] );
    	  //gr_complex const * in_2 = static_cast< gr_complex const * >( input_items[1] );
    	  gr_complex const * inv_ctf_1 = static_cast< gr_complex const * >( input_items[1] );
    	  //gr_complex const * inv_ctf_2 = static_cast< gr_complex const * >( input_items[3] );
    	  char const * frame_start_1 = static_cast< char const * >( input_items[2] );
    	  //char const * frame_start_2 = static_cast< char const * >( input_items[5] );
    	  gr_complex * out = static_cast< gr_complex * >( output_items[0] );

    	  //int const nin = std::min( ninput_items[0],//ninput_items[1],
    	    //                std::min( ninput_items[1], std::min(ninput_items[4],std::min(ninput_items[5],noutput_items ) ))) ;//
    	  int const nin = std::min( ninput_items[0],std::min(ninput_items[2],noutput_items ) ) ;//
    	  int n_ctf_1 = ninput_items[1];
    	  //int n_ctf_2 = ninput_items[3];

    	  int i = 0;

    	  for( ; i < nin;
    	       ++i, in_1 += d_vlen, out += d_vlen, ++d_blk )
    	  {
    	    if(( frame_start_1[i] != 0))// && (frame_start_2[i] != 0 ))
    	    {
    	        if( n_ctf_1 == 0 )
    	              {
    	                d_need_input_h1 = 1;
    	                if( DEBUG )
    	                    std::cout << "d_need_input_h1" << std::endl;
    	                break;
    	              }

    	        std::copy( inv_ctf_1, inv_ctf_1+ d_vlen/2, d_buffer_h1 );
    	        --n_ctf_1;
    	        inv_ctf_1 += d_vlen/2;
    	        d_need_input_h1 = 0;


    	      d_acc_phase.assign( d_acc_phase.size(), 0.0 );
    	      //d_phase_last.assign( d_phase_last.size(), 0.0 );
    	      d_acc_gamma = d_acc_b = 0.0;
    	      d_blk = 0;
    	      d_in_da = 0;

    	    } // if frame_start[i] != 0



    	    // No tracking on non-data OFDM blocks
    	    if( d_blk < (signed)d_nondata_block.size() && d_nondata_block[ d_blk ] )
    	    {
    	      if( DEBUG )
    	        std::cout << "LMS: non data block" << std::endl;

    	      std::copy( in_1, in_1 + d_vlen, out );
    	      //std::copy( in_2, in_2 + d_vlen, out2 );
    	      continue;
    	    }
    	    LMS_phasetracking( in_1, d_buffer_h1, out );
    	    // LMS_phasetracking( in_1, in_2, out );
    	    //LMS_phasetracking( in_1, in_2, inv_ctf_1, inv_ctf_2, out );
    	    //LMS_phasetracking( in_1, in_2, inv_ctf_1, inv_ctf_2, out2 );


    	  } // for-loop over input

    	  if( i > 0 )
    	   {
    	     consume( 0, i );
    	     consume( 2, i );
    	     //consume( 4, i );
    	     //consume( 5, i );
    	   }

    	   int const tmp_1 = ninput_items[1] - n_ctf_1;
    	   if( tmp_1 > 0 )
    	     consume( 1, tmp_1 );
    	   //int const tmp_2 = ninput_items[3] - n_ctf_2;
    	   //if( tmp_2 > 0 )
    	    // consume( 3, tmp_2 );


    	  if( DEBUG )
    	    std::cout << "LMS: leave, nout=" << noutput_items
    	              << " d_blk=" << d_blk << std::endl;

    	  return i;
    }

  } /* namespace ofdm */
} /* namespace gr */

