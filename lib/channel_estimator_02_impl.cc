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
#include "channel_estimator_02_impl.h"

#include <gnuradio/expj.h>
#include <gnuradio/math.h>

#include <iostream>
#include <cmath>
#include <algorithm>

#include <string.h>

#define DEBUG 0

#if DEBUG > 0
#define ASSERT_(x) assert((x))
#else
#define ASSERT_(x)
#endif

namespace gr {
  namespace ofdm {

  	static const float s_power_threshold = 10e-3;

  	// Least Squares Estimate
  	static /*inline*/ void
  	calculate_equalization(
  	  const gr_complex* blk,
  	  const boost::shared_array<gr_complex> known_block,
  	  const std::vector<bool> &subc_used,
  	  boost::shared_array<gr_complex> inv_ctf,
  	  boost::shared_array<gr_complex> ctf,
  	  int vlen )
  	{
  	  ASSERT_( inv_ctf );
  	  ASSERT_( ctf );

  	  for(int i = 0; i < vlen; ++i) {

  	    if( subc_used[i] )
  	    {
  	      inv_ctf[i] = known_block[i] / blk[i];
  	      ctf[i] = blk[i] / known_block[i];
  	    }
  	    else
  	    {
  	      // leave unaffected
  	      inv_ctf[i] = 0.0;
  	      ctf[i] = 0.0;
  	    } // subc_used[i]

  	  } // for-loop

  	}

    channel_estimator_02::sptr
    channel_estimator_02::make(int vlen, const std::vector<int> &pilot_tones, const std::vector<int> &nondata_block)
    {
      return gnuradio::get_initial_sptr
        (new channel_estimator_02_impl(vlen, pilot_tones, nondata_block));
    }


    /*
     * The private constructor
     */
    channel_estimator_02_impl::channel_estimator_02_impl(int vlen, const std::vector<int> &pilot_tones, const std::vector<int> &nondata_block)
      : gr::sync_block("channel_estimator_02",
              gr::io_signature::make2(2, 2, sizeof(gr_complex)*vlen,
                      sizeof(char)),
              gr::io_signature::make3(2, 3, sizeof(gr_complex)*vlen,
                      sizeof(float)*vlen,
                      sizeof(gr_complex)*vlen))
    , d_inv_ctf_estimate( new gr_complex[vlen] )
    , d_norm_ctf_estimate( new float[vlen] )
    , d_tmp_ctf_estimate( new gr_complex[vlen] )
    , d_tmp_inv_ctf_estimate( new gr_complex[vlen] )
    , d_tmp_norm_ctf_estimate( new float[vlen] )
    , d_blk(0)
    , d_dblk(0)
    , d_vlen(vlen)
    , d_pcount(pilot_tones.size())
    , d_acc_gamma(0.0)
    , d_acc_b(0.0)
    {
    	init_LMS_phasetracking( pilot_tones, nondata_block );
    	init_channel_estimation();
    }

    /*
     * Our virtual destructor.
     */
    channel_estimator_02_impl::~channel_estimator_02_impl()
    {
    }

    void
        channel_estimator_02_impl::init_LMS_phasetracking(
            const std::vector<int> &pilot_tones,
            const std::vector<int> &nondata_block )
        {
          // LMS phasetracking init

          // LUT: identify non data blocks
          int max = *std::max_element(nondata_block.begin(), nondata_block.end());
          d_nondata_block.resize(max+1,false);
          for(unsigned int i = 0; i < nondata_block.size(); ++i) {
            d_nondata_block[nondata_block[i]] = true;

            if(DEBUG)
              std::cout << "LUT non data block: " << nondata_block[i] << std::endl;
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
          for(int i = 0; i < d_pcount; ++i){
            d_gamma_coeff[i] = static_cast<float>(pilot_tones[i])*a+b;

            if(DEBUG)
              std::cout << "gamma["<<i<<"]=" << d_gamma_coeff[i] << std::endl;
          }

        }

        void
        channel_estimator_02_impl::init_channel_estimation()
        {
          // LS channel equalizer, init

          const gr_complex one(1.0,0.0);

          for(int i = 0; i < d_vlen; ++i)
          {
            d_inv_ctf_estimate[i] = one;
            d_norm_ctf_estimate[i] = 1.0;
          }
        }





        void
        channel_estimator_02_impl::set_known_block(
          int no, const std::vector<gr_complex> &block, bool pilot)
        {
          ASSERT_(no >= 0);
          ASSERT_(block.size() == static_cast<unsigned>(d_vlen));

          while(d_ofdm_frame.size() <= (unsigned)no)
          {
            ofdm_block_sptr new_entry( new ofdm_block() );
            d_ofdm_frame.push_back( new_entry );
          }

          ofdm_block_sptr cur = d_ofdm_frame[no];

          cur->known_block = true;
          cur->pilot = pilot;
          cur->subc_used.resize( d_vlen, false );

          boost::shared_array<gr_complex> vec( new gr_complex[d_vlen] );

          for( int i = 0; i < d_vlen; ++i )
          {
            vec[i] = block[i];

            if( abs( block[i] ) > 10e-6 )
            {
              cur->subc_used[i] = true;
            }
          } // for-loop

          cur->block = vec;

          // current index in frame
          d_blk = d_ofdm_frame.size();
        }


        static /*inline*/ void
        norm_vector(boost::shared_array<float> vec_out,
            const boost::shared_array<gr_complex> vec_in,
            const int& vlen)
        {
          float acc = 0.0;

          ASSERT_( vec_out );
          ASSERT_( vec_in );


          for( int i = 0; i < vlen; ++i )
          {
            const float __x = vec_in[i].real();
            const float __y = vec_in[i].imag();

            const float t = __x*__x + __y*__y;
            vec_out[i] = t;
            acc += t;
          }

          const float f = static_cast< float >( vlen ) / acc;
          for( int i = 0; i < vlen; ++i )
          {
            vec_out[i] *= f;
          }

        }

    int
    channel_estimator_02_impl::work(int noutput_items,
			  gr_vector_const_void_star &input_items,
			  gr_vector_void_star &output_items)
    {
    	const gr_complex *in = static_cast<const gr_complex*>(input_items[0]);
    	  const char *trig = static_cast<const char*>(input_items[1]);
    	  gr_complex *out = static_cast<gr_complex*>(output_items[0]);
    	  float *ctf = static_cast<float*>(output_items[1]);
    	  gr_complex *real_ctf = 0;

    	  if( output_items.size() > 2 )
    	    real_ctf = static_cast< gr_complex* >( output_items[2] );


    	  if(DEBUG)
    	    std::cout << "[chaneq " << unique_id() << "] entered, state"
    	              << " nout=" << noutput_items << std::endl;

    	  for( int item = 0;
    	       item < noutput_items;
    	       ++item, ++d_blk, out+=d_vlen, ctf+=d_vlen, in+=d_vlen )
    	  {

    	    if( trig[item] == 1 )
    	    { // reset
    	      d_acc_phase.assign(d_acc_phase.size(), 0.0);
    	      d_acc_gamma = d_acc_b = 0.0;
    	      d_dblk = d_blk = 0;

    	      if(DEBUG)
    	        std::cout << "TRIGGER! reset counters and phase accumulator"
    	                  << std::endl;
    	    } // if trig[item] == 1



    	    // Channel Estimation
    	    block_t inv_ctf_estimate = channel_estimation( in, out, ctf );



    	    // Equalization
    	    for( int i = 0; i < d_vlen; ++i )
    	    {
    	      out[i] = in[i] * inv_ctf_estimate[i];
    	    }

    	    if( real_ctf != 0 )
    	    {
    	      for( int i = 0; i < d_vlen; ++i )
    	      {
    	        real_ctf[i] = d_tmp_ctf_estimate[i];
    	      }
    	      real_ctf += d_vlen;
    	    }


    	    // LMS phase tracking algorithm
    	    LMS_phasetracking( out );


    	  }

    	  if(DEBUG)
    	    std::cout << "[chaneq " << unique_id() << "] leaving, produce "
    	              << noutput_items << " items" << std::endl;


    	  return noutput_items;
    }

    /*inline*/ void
    channel_estimator_02_impl::LMS_phasetracking( gr_complex* out )
    {

      // LMS phase tracking algorithm

      // skip nondata blocks
      if( d_blk < (signed)d_nondata_block.size() && d_nondata_block[d_blk] ){
        return;
      }


    //  // precompensation
    //  if( d_dblk != 0 ){
    //
    //    for(int i = 0; i < d_vlen; ++i){
    //      out[i] *= gr_expj(-d_acc_phase[i]);
    //    }
    //
    //    if(DEBUG)
    //      std::cout << "perform phase precompensation on block" << std::endl;
    //  }

      float gamma = 0.0;
      float b = 0.0;

      ASSERT_( d_pcount == d_pilot.size() );

      // LMS coefficient adaptation
      for(int i = 0; i < d_pcount; ++i){

        ASSERT_( i < d_pilot.size() );
        const int ind = d_pilot[i];

        ASSERT_( ind < d_vlen && ind >= 0 );
        gr_complex pilot = out[ind];

        // precompensation on pilot subcarrier
        if( d_dblk != 0 ){
          ASSERT_(i >= 0 && i < d_acc_phase.size());
          pilot *= gr_expj( -d_acc_phase[i] );
        }

        ASSERT_( i < d_pilot_tone.size() );
        const gr_complex x = pilot * d_pilot_tone[i];
        const float beta = std::atan2( x.imag(), x.real() ); //gr_fast_atan2f();

        ASSERT_( i < d_gamma_coeff.size() );
        gamma += d_gamma_coeff[i]*beta;
        b += beta; //d_b_coeff[i]
        ASSERT_( i < d_acc_phase.size() );
        d_acc_phase[i] += beta;

      } // for-loop


      b /= static_cast<float>(d_pcount);

      if(DEBUG)
        std::cout << "LMS parameters: gamma=" << gamma
                  << " b=" << b << std::endl;

      d_acc_b += b;
      d_acc_gamma += gamma;

      // phase compensation, includes accumulated estimates

      const float init_phase = d_acc_gamma * (-d_vlen/2+1) + d_acc_b;

      gr_complex phasor = gr_expj( -init_phase );
      const gr_complex phasor_step = gr_expj( -d_acc_gamma );

      for(int i = 0; i < d_vlen; ++i ){

        // out[i] *= gr_expj( - ( gamma * ( i - d_vlen/2 + 1 ) + b ) )

        out[i] *= phasor;
        phasor *= phasor_step;

      } // for-loop

      ++d_dblk;

    //  std::cout << "[chanest02] accgamma=" << d_acc_gamma << " accb=" << d_acc_b
    //            << std::endl;

    }


    /*inline*/ channel_estimator_02_impl::block_t
    channel_estimator_02_impl::channel_estimation(
        const gr_complex* in,
        gr_complex* out,
        float* ctf )
    {

      // Channel Estimation

      if(d_blk < (signed)d_ofdm_frame.size() && d_ofdm_frame[d_blk]->known_block)
      {
        // block is known, calculate inverse ctf and ctf

        ASSERT_( d_ofdm_frame[d_blk] );

        calculate_equalization(in, d_ofdm_frame[d_blk]->block,
                               d_ofdm_frame[d_blk]->subc_used,
                               d_tmp_inv_ctf_estimate,
                               d_tmp_ctf_estimate, d_vlen);


        // normalize ctf and store magnitude values
        // we can't attribute any information to absolute values
        // prefer relative values at any time as long as the system
        // is not calibrated.
        norm_vector(d_tmp_norm_ctf_estimate, d_tmp_ctf_estimate, d_vlen);


        if(DEBUG)
          std::cout << " found known block" << std::endl;


        if( d_ofdm_frame[d_blk]->pilot )
        { // store for later reuse

          memcpy( d_inv_ctf_estimate.get(), d_tmp_inv_ctf_estimate.get(),
            sizeof(block_t::element_type) * d_vlen );

          memcpy( d_norm_ctf_estimate.get(), d_tmp_norm_ctf_estimate.get(),
            sizeof(norm_ctf_t::element_type) * d_vlen );

          if(DEBUG)
            std::cout << " found pilot block, store internal state" << std::endl;
        }

        memcpy( ctf, d_tmp_norm_ctf_estimate.get(),
          sizeof(norm_ctf_t::element_type) * d_vlen );

        return d_tmp_inv_ctf_estimate;

      } // if( known block )

      // The symbol is unknown or we got more symbols in an ofdm block than
      // expected. Output last known CTF vectors

      memcpy( ctf, d_norm_ctf_estimate.get(),
        sizeof(norm_ctf_t::element_type) * d_vlen );

      if(DEBUG)
        std::cout << " found normal block, reuse internal state" << std::endl;

      return d_inv_ctf_estimate;

    }



  } /* namespace ofdm */
} /* namespace gr */

