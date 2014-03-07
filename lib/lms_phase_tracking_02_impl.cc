/* -*- c++ -*- */
/* 
 * Copyright 2014 Institute for Theoretical Information Technology,
 *                RWTH Aachen University
 *                www.ti.rwth-aachen.de
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
#include "lms_phase_tracking_02_impl.h"

#include <ofdm/ofdmi_fast_math.h>

#include <gnuradio/expj.h>

#include <iostream>
#include <algorithm>

#define DEBUG 0

#if DEBUG > 1
#define ASSERT_(x) assert((x))
#else
#define ASSERT_(x)
#endif


namespace gr {
  namespace ofdm {

    lms_phase_tracking_02::sptr
    lms_phase_tracking_02::make(int vlen, const std::vector<int> &pilot_subc, std::vector< int > const &nondata_blocks)
    {
      return gnuradio::get_initial_sptr
        (new lms_phase_tracking_02_impl(vlen, pilot_subc, nondata_blocks));
    }

    /*
     * The private constructor
     */
    lms_phase_tracking_02_impl::lms_phase_tracking_02_impl(int vlen, const std::vector<int> &pilot_subc, std::vector< int > const &nondata_blocks)
      : gr::sync_block("lms_phase_tracking_02",
              gr::io_signature::make2(
            	        2, 2,
            	        sizeof( gr_complex ) * vlen,
            	        sizeof( char ) ),
              gr::io_signature::make( 1, 1, sizeof( gr_complex ) * vlen))
    , d_vlen( vlen )

    , d_acc_gamma( 0.0 )
    , d_acc_b( 0.0 )

    , d_pcount( pilot_subc.size() )
    , d_blk( 0 )
    {
    	  assert( ( vlen % 2 ) == 0 );
    	  init_LMS_phasetracking( pilot_subc, nondata_blocks );
    }

    void
    lms_phase_tracking_02_impl ::
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


      // LUT: identify pilot subcarrier
      d_pilot_tone.resize(d_pcount,1.0); // FIXME allow different pilot tone value
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
    lms_phase_tracking_02_impl ::
    LMS_phasetracking(
      gr_complex const * in,
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

      d_acc_b += b;
      d_acc_gamma += gamma;

      // phase compensation, includes accumulated estimates

      float const phase_slope = -d_acc_gamma;

      float const init_phase = phase_slope * (-d_vlen/2) - d_acc_b;

      perform_frequency_shift( in, out, d_vlen, init_phase, phase_slope );

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

    /*
     * Our virtual destructor.
     */
    lms_phase_tracking_02_impl::~lms_phase_tracking_02_impl()
    {
    }

    int
    lms_phase_tracking_02_impl::work(int noutput_items,
			  gr_vector_const_void_star &input_items,
			  gr_vector_void_star &output_items)
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
    	      d_acc_gamma = d_acc_b = 0.0;
    	      d_blk = 0;

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
    }

  } /* namespace ofdm */
} /* namespace gr */

