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

#ifndef INCLUDED_OFDM_ITPP_TDL_CHANNEL_H
#define INCLUDED_OFDM_ITPP_TDL_CHANNEL_H

#include <ofdm/api.h>
#include <gnuradio/sync_block.h>

#include <itpp/itcomm.h>
#include <itpp/base/random.h>

namespace itpp
{
  class TDL_Channel;
};

namespace gr {
  namespace ofdm {

  /*!
   * \brief Wrapper for itpp::TDL_Channel class
   *
   * See IT++ documentation.
   *
   * Pimpl idiom used. Explicitly hide all IT++ implementation;
   *
   * IT++'s global random number generator state is reset with a random seed.
   *
   * A few notes:
   * The average power profile is always normalized at initialization.
   * The IFFT correlated method seems to generate independent fading for
   * small blocks, thus might be useless in a stream based model.
   * Setting the doppler spectrum type automatically chooses Rice_MEDS as
   * the correlated method.
   *
   * FIR correlated method chooses a FIR filter with jakes doppler spectrum
   * for each tap. This filter is applied on a sequence of gaussian noise
   * variables. Possibly the fastest method. It doesn't work for small doppler
   * frequencies.
   *
   * Static fading type generates a realization of the channel at initialization
   * and stays static/constant over the whole period of operation.
   */

  typedef std::vector< double > dvec;
  typedef std::vector< int >    ivec;
  typedef std::vector< std::complex< double > > cvec;

  enum CHANNEL_PROFILE {
     ITU_Vehicular_A, ITU_Vehicular_B, ITU_Pedestrian_A, ITU_Pedestrian_B,
     COST207_RA, COST207_RA6,
     COST207_TU, COST207_TU6alt, COST207_TU12, COST207_TU12alt,
     COST207_BU, COST207_BU6alt, COST207_BU12, COST207_BU12alt,
     COST207_HT, COST207_HT6alt, COST207_HT12, COST207_HT12alt,
     COST259_TUx, COST259_RAx, COST259_HTx
};

  enum DOPPLER_SPECTRUM {
    Jakes = 0, J = 0, Classic = 0, C = 0,
    GaussI = 1, Gauss1 = 1, GI = 1, G1 = 1,
    GaussII = 2, Gauss2 = 2, GII = 2, G2 = 2
  };

  enum FADING_TYPE { Independent, Static, Correlated };

  enum CORRELATED_METHOD { Rice_MEDS, IFFT, FIR };


    class OFDM_API itpp_tdl_channel : virtual public gr::sync_block
    {
     public:
      typedef boost::shared_ptr<itpp_tdl_channel> sptr;

      virtual void set_channel_profile( const dvec & avg_power_db,
               const ivec & delay_prof ) = 0;
      virtual void set_channel_profile_exponential( int no_taps ) = 0;
      virtual void set_channel_profile( const CHANNEL_PROFILE profile,
        double sampling_time ) = 0;

      virtual void global_rng_reset( unsigned int seed ) = 0;
      virtual void set_correlated_method( CORRELATED_METHOD method ) = 0;
      virtual void set_fading_type( FADING_TYPE fading_type ) = 0;

      virtual void set_norm_doppler( double norm_doppler ) = 0;

      virtual void set_LOS( const dvec& relative_power, const dvec& relative_doppler =
		  dvec() ) = 0;
      virtual void set_LOS_power( const dvec& relative_power ) = 0;
      virtual void set_LOS_doppler( const dvec& relative_doppler ) = 0;

      virtual void set_doppler_spectrum(
		const std::vector< DOPPLER_SPECTRUM > tap_spectrum ) = 0;
      virtual void set_doppler_spectrum( int tap_number, DOPPLER_SPECTRUM tap_spectrum )= 0;

      virtual void set_no_frequencies( int no_freq ) = 0; // Rice-MEDS

      virtual void set_time_offset( int offset ) = 0;
      virtual void shift_time_offset( int no_samples ) = 0;

      virtual void set_filter_length( int filter_length ) = 0; // FIR fading type

      static sptr make(const dvec & avg_power_db = dvec(), const ivec & delay_prof = ivec(), bool calc_impulse_response = false);
    };

  } // namespace ofdm
} // namespace gr

#endif /* INCLUDED_OFDM_ITPP_TDL_CHANNEL_H */

