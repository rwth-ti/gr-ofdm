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
#include "time_sync_impl.h"

#include <iostream>
#include <algorithm>
#include <cmath>

#define DEBUG 0



namespace gr {
    namespace ofdm {

        enum states
        {
            ACQUISITION = 0,
            TRACKING = 1
        };

        time_sync::sptr
        time_sync::make(int vlen, int cplen)
        {
            return gnuradio::get_initial_sptr
                (new time_sync_impl(vlen, cplen));
        }

        /*
         * The private constructor
         */
        time_sync_impl::time_sync_impl(int vlen, int cplen)
            : gr::block("time_sync",
                    gr::io_signature::make2(  3, 3, // 4, 4,
                        sizeof( gr_complex ),
                        sizeof( float )),
                    gr::io_signature::make3(2, 3,
                        sizeof( gr_complex ) * vlen,
                        sizeof( char ),
                        sizeof( unsigned long )))
              , d_vlen( vlen )
              , d_cplen( cplen )
              , d_blocklen( vlen + cplen )
              , d_state( ACQUISITION )
              , d_avg_blocks( 10 )
              , d_sc_threshold( 0.2 )
              , d_gi_threshold( 0.2 * d_avg_blocks )
              , d_s0_max_ind_err( cplen ) // 10
              , d_s1_gi_failures( 0 )
              , d_s1_max_failures( 20 )
              , d_avg_gi_metric( new float[d_blocklen] )
              , d_index_decision( -1 )
              , d_shift( d_blocklen )
              , d_window_shift( 0.0 )
              , d_i_gain_shift( 0.01 )
              , d_sample( 0 )
          {
              //set_history( ( d_avg_blocks + 1 ) * d_blocklen );
              //d_sample = - history() + 1 + d_vlen; // zeros
              set_history( d_shift );
              d_hist = ( d_avg_blocks + 1 ) * d_blocklen;
          }

        /*
         * Our virtual destructor.
         */
        time_sync_impl::~time_sync_impl()
        {
            delete[] d_avg_gi_metric;
        }

        bool
        time_sync_impl ::
        start()
        {
            return true;
        }

        void
        time_sync_impl::forecast (int noutput_items, gr_vector_int &ninput_items_required)
        {
            /* <+forecast+> e.g. ninput_items_required[0] = noutput_items */
            // FIXME: is there a better forecast?
            int req = d_hist; // history();

            if( d_state == TRACKING )
                req += d_blocklen - 1;

            for( unsigned int i = 0; i < ninput_items_required.size(); ++i )
            {
                ninput_items_required[i] = req;
            }
        }

        static inline
        void
        bootstrap_peakdetector( float const * m, int vlen, int & ind, float & val )
        {
            val = 0.0;
            ind = 0;
            for( int i = 0; i < vlen; ++i )
            {
                if( m[i] > val )
                {
                    val = m[i];
                    ind = i;
                }
            } // for

        } // bootstrap_peakdetector

        static inline
        void
        compute_average_gi_metric( float const * gi_metric, float * vec, int blocklen,
                int nblocks )
        {
            // TODO: vectorization?

            std::fill( vec, vec + blocklen, 0.0 );

            int j = 0;
            for( int i = 0; i < ( blocklen * nblocks ); ++i )
            {
                vec[j] += gi_metric[i];

                ++j;
                if( j == blocklen )
                    j = 0;
            } // for-loop

        } // compute average gi metric

        inline
        int
        time_sync_impl ::
        compute_min_ninput( gr_vector_int const & ninput_items ) const
        {
            int const nin = std::min( ninput_items[0], std::min( ninput_items[1],
                        ninput_items[2] ) ) - d_hist + 1;
            return nin;
        }

        inline
        int
        time_sync_impl ::
        compute_min_ninput( gr_vector_int const & ninput_items,
                int const & multiple ) const
        {
            int nin = compute_min_ninput( ninput_items );

            if( ( nin % multiple ) != 0 )
                nin -= nin % multiple;

            return nin;
        }

        inline
        bool
        time_sync_impl ::
        frame_detected( int const & ind, float const & sc_val,
                float const * const gi_metric )
        {
            int const mid_point = d_blocklen / 2;

            if( ind == mid_point && sc_val > d_sc_threshold )
            {
                compute_average_gi_metric( gi_metric, d_avg_gi_metric, d_blocklen,
                        d_avg_blocks );

                int gi_ind;
                float gi_val;
                bootstrap_peakdetector( d_avg_gi_metric, d_vlen, gi_ind, gi_val );

                if( DEBUG )
                    std::cout << "SYNC: found peak, sc_val=" << sc_val
                        << " gi_ind=" << gi_ind << " gi_val=" << gi_val
                        << " at ind: " << d_avg_gi_metric[mid_point] << std::endl;

                if( gi_val > d_gi_threshold
                        && std::abs( gi_ind - ind ) < d_s0_max_ind_err )
                {
                    // TODO: use weights here, proportional to peak values

                    d_index_decision = ( ind + gi_ind ) / 2;

                    return true;
                    //      enter_state1();
                    //      break;

                } // if gi_val > gi threshold && abs(ind-gi_ind)<max_ind_err

            } // if ind == mid_point && sc_val > threshold

            return false;

        } // frame_detected


        inline
        void
        time_sync_impl ::
        s1_compute_metric_values(
                float const * const sc_metric, float const * const gi_metric,
                float & sc_val, float & gi_val ) const
        {
            sc_val = 0.0;
            gi_val = 0.0;

            sc_val = sc_metric[ d_index_decision ];

            for( int j = 0; j < d_avg_blocks; ++j )
            {
                gi_val += gi_metric[ d_index_decision + j * d_blocklen ];
            }
        } // s1_compute_metric_values


        inline
        bool
        time_sync_impl ::
        s1_must_recover( float const & gi_val )
        {
            if( gi_val < d_gi_threshold )
            {
                // TODO: use gi_val as indicator how fast we should recover

                ++d_s1_gi_failures;

                if( DEBUG )
                    std::cout << "SYNC: tracking, failure " << d_s1_gi_failures
                        << " gi_val=" << gi_val << std::endl;

                if( d_s1_gi_failures > d_s1_max_failures )
                {
                    return true;
                    //      enter_state0();
                    //      break;
                }
            }
            else
            {
                d_s1_gi_failures = 0;

            } // if( gi_val < d_gi_threshold )

            return false;
        }

        inline
        void
        time_sync_impl ::
        s1_track_cyclic_prefix( float const * const sc_metric,
                float const * const gi_metric, float const & gi_val )
        {
            float sc_val, gi_val_1, gi_val_2;

            // see if we should change our decision
            // look at GI ML estimator values one to the left and one sample to the
            // right

            // FIXME: if the higher value has only a small improvement, i.e.
            // |new-old| < x it may not be worth to shift. The error could be due to
            // finite precision arithmetic

            // -1
            s1_compute_metric_values( sc_metric, gi_metric - 1, sc_val, gi_val_1 );

            // +1
            s1_compute_metric_values( sc_metric, gi_metric + 1, sc_val, gi_val_2 );

            if( gi_val_1 > gi_val && gi_val_1 > gi_val_2 )
            {
                //    if( ( gi_val_1 - gi_val ) > ( 0.05 * d_avg_blocks ) )
                {
                    d_window_shift -= d_i_gain_shift;
                    //      std::cout << "gi_val_1=" << gi_val_1 << " gi_val=" << gi_val
                    //                << " gi_val_2=" << gi_val_2 << std::endl;
                }
            }
            else if( gi_val_2 > gi_val && gi_val_2 > gi_val_1 )
            {
                //    if( ( gi_val_2 - gi_val ) > ( 0.05 * d_avg_blocks ) )
                {
                    d_window_shift += d_i_gain_shift;
                    //      std::cout << "gi_val_2=" << gi_val_2 << " gi_val=" << gi_val
                    //                << " gi_val_1=" << gi_val_1 << std::endl;
                }

            }
            else
            {
                //    d_window_shift *= 0.8;
                if( d_window_shift > 0.0 )
                    d_window_shift -= d_i_gain_shift;
                else
                    d_window_shift += d_i_gain_shift;
            }

            if( std::abs( d_window_shift ) >= 1.0 )
            {
                if( d_window_shift > 0.0 )
                    std::cout << "Q";
                else
                    std::cout << "W";
                int tmp = d_window_shift;
                d_index_decision += tmp;
                d_window_shift = 0.0;


                if( DEBUG )
                    std::cout << "!! SYNC: shift " << tmp << std::endl
                        << "gi_val_1=" << gi_val_1 << " gi_val=" << gi_val
                        << " gi_val_2=" << gi_val_2 << std::endl;

            }
        }


        inline
        void
        time_sync_impl ::
        debug_samplectr_out( unsigned long * & trig_out, int const & i ) const
        {
            if( DEBUG )
            {
                std::cout << "## p at "
                    << ( (signed)d_sample + i + d_index_decision ) % d_blocklen
                    << std::endl;
            }

            if( trig_out ) // DEBUGGING
                *trig_out++ = d_sample +
                    static_cast< unsigned long >( i + d_index_decision );
        }

        int
        time_sync_impl::general_work (int noutput_items,
                gr_vector_int &ninput_items,
                gr_vector_const_void_star &input_items,
                gr_vector_void_star &output_items)
        {
            gr_complex const * samples =
                static_cast< gr_complex const * >( input_items[0] );

            float const * sc_metric = static_cast< float const * >( input_items[1] );
            float const * gi_metric = static_cast< float const * >( input_items[2] );
            //  float const * ctrl_shift = static_cast< float const * >( input_items[3] );

            // shift the pointers so that our accesses are never out of range
            // trying to avoid range checking
            samples   += d_shift;
            sc_metric += d_shift;
            gi_metric += d_shift;


            // If we made a decision, stored in d_index_decision, we enter tracking
            // state in which we advance the stream pointers blockwise (d_blocklen).
            // The decision point will be near the center of the search window. But
            // this is the last sample of the ofdm block. Hence, we extract vlen samples
            // to the left of this index.

            // Note: we use set_history() and history() in the forecast() function
            // to assert that we always have enough items and do not need to perform
            // range checking. However, this introduces delay.


            //  int & n_ctrl_shift = ninput_items[3];


            int const mid_point = d_vlen/2;


            gr_complex * out = static_cast< gr_complex * >( output_items[0] );
            char * framestart = static_cast< char * >( output_items[1] );

            // DEBUGGING whitebox test
            unsigned long * trig_out = 0;
            if( output_items.size() > 2 )
                trig_out = static_cast< unsigned long * >( output_items[2] );



            int produced = 0;

            if(DEBUG)
                std::cout << "SYNC: Enter work, noutput_items=" << noutput_items
                    << std::endl;


            if( d_state == ACQUISITION )
            {
                //    // Consume all input streams that are irrelevant in this stage.
                //    if( n_ctrl_shift > 0 )
                //      consume( 3, n_ctrl_shift );



                int const nin = compute_min_ninput( ninput_items );
                float const * const sc_metric2 = sc_metric + d_vlen + 1;

                int ind;
                float sc_val;
                bootstrap_peakdetector( sc_metric, d_vlen, ind, sc_val );

                if( DEBUG )
                    std::cout << "ACQ state, bootstrap pd: ind=" << ind << " val=" << sc_val
                        << " nin=" << nin << std::endl;

                int i = 0;
                for( ; i < nin; ++i )
                {
                    if( frame_detected( ind, sc_val, gi_metric + i ) )
                    {
                        d_sample += i;
                        enter_state1();
                        d_sample -= i;
                        break;
                    }

                    // track peak value: shift search window by 1 sample
                    // old value at left limits falls out of range
                    // new val is peak? else old peak was at left limit?
                    // else adjust peak index (compensate window shift)
                    if( sc_metric2[i] > sc_val )
                    {
                        ind = d_vlen;
                        sc_val = sc_metric2[i];
                    }
                    else if( ind == 0 )
                    {
                        // FIXME: does the re-bootstrap significantly influence the performance?
                        bootstrap_peakdetector( sc_metric + i + 1, d_vlen, ind, sc_val );
                    }
                    else
                    {
                        --ind;
                    }

                } // for-loop

                consume( 0, i );
                consume( 1, i );
                consume( 2, i );
                d_sample += i;

                if( DEBUG )
                    std::cout << "SYNC: consume i=" << i << std::endl;

                // consume i items, hence the next sample we will look (if we enter the
                // tracking state is the sample at index i.

            }
            else if( d_state == TRACKING )
            {

                // advance pointers blockwise (d_blocklen samples stride)

                //int const nin = compute_min_ninput( ninput_items, d_blocklen );
                int const nin = compute_min_ninput( ninput_items ) - d_blocklen + 1;

                if( DEBUG )
                    std::cout << "SYNC, Tracking state: nin=" << nin << std::endl;

                int i = 0;
                while( i < nin ) // (i+d_blocklen-1) < nin
                    //    for( ; i < nin; i += d_blocklen )
                {
                    // TODO: mute sc & gi autocorrelators, perform correlation here
                    //       will this be really faster?

                    // at d_index_decision, to check if we must recover and to detect
                    // frame starts
                    float sc_val, gi_val;
                    s1_compute_metric_values( sc_metric + i, gi_metric + i, sc_val, gi_val );


                    s1_track_cyclic_prefix( sc_metric + i, gi_metric + i, gi_val );


                    if( s1_must_recover( gi_val ) )
                    {
                        d_sample += i;
                        enter_state0();
                        d_sample -= i;
                        break;
                    }


                    char is_framestart = 0;

                    // If S&C metric's value > threshold -> preamble detected = frame start
                    if( sc_val > d_sc_threshold )
                    {
                        is_framestart = 1;
                    }

                    debug_samplectr_out( trig_out, i ); // DEBUGGING


                    // Extract OFDM block w/o cyclic prefix

                    gr_complex const * block_start =
                        samples + i + d_index_decision - d_vlen + 1     -1;

                    std::copy( block_start, block_start + d_vlen, out + produced * d_vlen );
                    framestart[ produced ] = is_framestart;

                    ++produced;

                    // Check if we filled the complete output buffer
                    if( produced == noutput_items )
                    {
                        if( DEBUG )
                            std::cout << "SYNC: output blocked" << std::endl;
                        i += d_blocklen;
                        break;
                    }

                    i += d_blocklen;


                    // shift the window in order to have index_decion = mid_point

                    if( d_index_decision > mid_point && ( nin - i ) > 1 )
                    {
                        ++i;
                        --d_index_decision;
                        if( DEBUG )
                            std::cout << "SYNC: window shift +1, index_dec -1" << std::endl;
                    }

                    if( d_index_decision < mid_point )
                    {
                        --i;
                        ++d_index_decision;
                        if( DEBUG )
                            std::cout << "SYNC: window shift -1, index_dec +1" << std::endl;
                    }

                } // for-loop

                consume( 0, i );
                consume( 1, i );
                consume( 2, i );
                d_sample += i;      // DEBUGGING

                if( DEBUG )
                    std::cout << "SYNC: consume i=" << i << std::endl;



            } // if d-state

            if(DEBUG)
                std::cout << "SYNC: Leave work, produced=" << produced
                    << " d_sample=" << d_sample << std::endl;

            return produced;
        }

        void
        time_sync_impl ::
        enter_state1()
        {
            d_state = TRACKING;
            if( DEBUG )
                std::cout << "####### SYNC: Enter tracking state at " << d_sample
                    << std::endl;
            else
                std::cout << "#";

            d_s1_gi_failures = 0;
            d_window_shift = 0.0;
        }

        void
        time_sync_impl ::
        enter_state0()
        {
            d_state = ACQUISITION;
            if( DEBUG )
                std::cout << "####### SYNC: Enter acquisition state at " << d_sample
                    << std::endl;
            else
                std::cout << "A";
        }

    } /* namespace ofdm */
} /* namespace gr */

