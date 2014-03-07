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

#ifndef INCLUDED_OFDM_ITPP_TDL_CHANNEL_IMPL_H
#define INCLUDED_OFDM_ITPP_TDL_CHANNEL_IMPL_H

#include <ofdm/itpp_tdl_channel.h>

namespace gr {
  namespace ofdm {

    class itpp_tdl_channel_impl : public itpp_tdl_channel
    {
     private:
    	  dvec   d_avg_power_db;
    	  ivec   d_delay_prof;
    	  bool	 d_calc_impulse_response;

    	  cvec   d_buffer;
    	  int 	 d_max_delay;


    	  boost::shared_ptr< itpp::TDL_Channel > d_channel;

     public:
      itpp_tdl_channel_impl(const dvec & avg_power_db, const ivec & delay_prof, bool calc_impulse_response);
      ~itpp_tdl_channel_impl();

      // Where all the action really happens
      int work(int noutput_items,
	       gr_vector_const_void_star &input_items,
	       gr_vector_void_star &output_items);

      void global_rng_reset( unsigned int seed );

        void set_channel_profile( const dvec & avg_power_db,
          const ivec & delay_prof );
        //void set_channel_profile_uniform( int no_taps );
        void set_channel_profile_exponential( int no_taps );
        void set_channel_profile( const CHANNEL_PROFILE profile,
          double sampling_time );

        void set_correlated_method( CORRELATED_METHOD method );
        void set_fading_type( FADING_TYPE fading_type );

        void set_norm_doppler( double norm_doppler );

        void set_LOS( const dvec& relative_power, const dvec& relative_doppler =
            dvec() );
        void set_LOS_power( const dvec& relative_power );
        void set_LOS_doppler( const dvec& relative_doppler );

        void set_doppler_spectrum(
          const std::vector< DOPPLER_SPECTRUM > tap_spectrum );
        void set_doppler_spectrum( int tap_number, DOPPLER_SPECTRUM tap_spectrum );

        void set_no_frequencies( int no_freq ); // Rice-MEDS

        void set_time_offset( int offset );
        void shift_time_offset( int no_samples );

        void set_filter_length( int filter_length ); // FIR fading type

        int taps() const;
        void get_channel_profile( dvec &avg_power_dB, ivec &delay_prof ) const;
        dvec get_avg_power_dB() const;
        ivec get_delay_prof() const;
        CORRELATED_METHOD get_correlated_method() const;
        FADING_TYPE get_fading_type() const;
        double get_norm_doppler() const;
        dvec get_LOS_power() const;
        dvec get_LOS_doppler() const;
        double get_LOS_power( int tap_number ) const;
        double get_LOS_doppler( int tap_number ) const;
        int get_no_frequencies() const;
        double get_time_offset() const;
        double calc_mean_excess_delay() const;
        double calc_rms_delay_spread() const;
        double get_sampling_time() const;

        /*! Calculate frequency response
         *
         * We calculate the response based on the current state. Thus, the returned
         * vector represents the response used for the next sample step. If the
         * fading process is static, it is identical for all samples.
         * Note that we must generate a new realization of the channel, compute
         * the FFT, and then step back in time. This works for the currently known
         * fading generators but might invalidate state for future generators.
         *
         * The channel will be initialized automatically to allow generating a
         * realization. Any subsequent change to this object might reinitialize
         * the channel and thus invalidate the result.
         *
         * @param[out] frequency_response Vector that will hold frequency response
         * @param[in] fft_size FFT size
         */
        cvec calc_frequency_response(int fft_size );
        //cvec set_vector(int vlen);

        /*! Calculate impulse response
         *
         * \see calc_frequency_response
         */
        void calc_impulse_response( cvec &impulse_response );


        virtual bool start();
    };

  } // namespace ofdm
} // namespace gr

#endif /* INCLUDED_OFDM_ITPP_TDL_CHANNEL_IMPL_H */

