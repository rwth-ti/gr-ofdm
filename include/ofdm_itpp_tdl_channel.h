
/* $Id: ofdm_itpp_tdl_channel.h 923 2009-04-21 14:03:45Z auras $ */

#ifndef INCLUDED_OFDM_ITPP_TDL_CHANNEL_H_
#define INCLUDED_OFDM_ITPP_TDL_CHANNEL_H_

#include <ofdm_api.h>
#include <gr_sync_block.h>

class ofdm_itpp_tdl_channel;
typedef boost::shared_ptr<ofdm_itpp_tdl_channel>
  ofdm_itpp_tdl_channel_sptr;

typedef std::vector< double > dvec;
typedef std::vector< int >    ivec;
typedef std::vector< std::complex< double > > cvec;

OFDM_API ofdm_itpp_tdl_channel_sptr
ofdm_make_itpp_tdl_channel( const dvec & avg_power_db = dvec(),
  const ivec & delay_prof = ivec(), bool calc_impulse_response = false );

namespace itpp
{
  class TDL_Channel;
};

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
class OFDM_API ofdm_itpp_tdl_channel : public gr_sync_block
{
private:

    friend OFDM_API ofdm_itpp_tdl_channel_sptr
        ofdm_itpp_make_tdl_channel( const dvec & avg_power_db,  const ivec & delay_prof, bool calc_impulse_response);
    ofdm_itpp_tdl_channel( const dvec & avg_power_db, const ivec & delay_prof,
    bool calc_impulse_response );

  dvec   d_avg_power_db;
  ivec   d_delay_prof;
  bool	 d_calc_impulse_response;

  cvec   d_buffer;
  int 	 d_max_delay;


  boost::shared_ptr< itpp::TDL_Channel > d_channel;

public:

  static ofdm_itpp_tdl_channel_sptr create( const dvec & avg_power_db,
    const ivec & delay_prof, bool calc_impulse_response );

  virtual ~ofdm_itpp_tdl_channel() {}

  /*! Reset IT++'s global random number generator state
   *
   * Note, this changes the global IT++'s RNG state!
   * Use to reproduce results.
   *
   * @param[in] seed New seed for RNG
   */
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

  int
  work(
    int                         noutput_items,
    gr_vector_const_void_star & input_items,
    gr_vector_void_star       & output_items );

};

#endif /* INCLUDED_OFDM_ITPP_TDL_CHANNEL_H_ */
