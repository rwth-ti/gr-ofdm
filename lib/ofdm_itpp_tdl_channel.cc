#ifdef HAVE_CONFIG_H
#include "config.h"
#endif

#include <gr_sync_block.h>
#include <gr_io_signature.h>
#include <ofdm_itpp_tdl_channel.h>

#include <iostream>
#include <algorithm>

#include <itpp/itcomm.h>
#include <itpp/base/random.h>

#define DEBUG 0

template < typename T >
static itpp::Vec< T >
conv_stdvector_to_itppvec( const std::vector< T > & vec )
{
  if( vec.size() == 0 )
  {
    return itpp::Vec< T >();
  }

  itpp::Vec< T > out( vec.size() );
  for( typename std::vector<T>::size_type i = 0; i < vec.size(); ++i )
  {
   out[i] = vec[i];
  }
  return out;
}

template < typename T >
static std::vector< T >
conv_itppvec_to_stdvector( const itpp::Vec< T > & vec )
{
  if( vec.size() == 0 )
  {
    return std::vector< T >();
  }

  std::vector< T > out( vec.size() );
  for( typename std::vector<T>::size_type i = 0; i < (unsigned)vec.size(); ++i )
  {
   out[i] = vec[i];
  }
  return out;
}


ofdm_itpp_tdl_channel::ofdm_itpp_tdl_channel( const dvec & avg_power_db,
  const ivec & delay_prof, bool calc_impulse_response )

  : gr_sync_block(
      "itpp_tdl_channel",
      gr_make_io_signature(
        1, 1,
        sizeof( gr_complex ) ),
      gr_make_io_signature(
        1, 1,
        sizeof( gr_complex ) ) ),

  d_avg_power_db( avg_power_db ),
  d_delay_prof( delay_prof ),
  d_calc_impulse_response( calc_impulse_response ),

  d_channel( new itpp::TDL_Channel() )

{
  itpp::RNG_randomize();

  if( avg_power_db.size() > 0 && delay_prof.size() > 0 &&
      avg_power_db.size() == delay_prof.size() )
  {
    d_channel->set_channel_profile(
      conv_stdvector_to_itppvec( avg_power_db ),
      conv_stdvector_to_itppvec( delay_prof ) );

    if( calc_impulse_response )
    {
      // enable optional impulse response output
      int maxdelay = *std::max_element( delay_prof.begin(), delay_prof.end() );

      set_output_signature(
	gr_make_io_signature2(
	  1, 2,
	  sizeof( gr_complex ),
	  sizeof( gr_complex ) * ( maxdelay + 1 ) ) );
    }
  }
  else
  {
    if( avg_power_db.size() == delay_prof.size() && avg_power_db.size() == 0)
    {
      return;
    }

    std::cerr << "Didn't set neither avg_power_db nor delay_prof since one of"
              << " them has size==0 or they have different sizes" << std::endl;
  }
}

void
ofdm_itpp_tdl_channel ::
  global_rng_reset( unsigned int seed )
{
  itpp::RNG_reset( seed );
}

bool ofdm_itpp_tdl_channel::start()
{
  const int max_delay = itpp::max( d_channel->get_delay_prof() );
  assert( max_delay >= 0 );
  d_buffer.resize( max_delay, 0.0 );
  d_max_delay = max_delay;
  return true;
}

int
ofdm_itpp_tdl_channel::work(
  int                         noutput_items,
  gr_vector_const_void_star & input_items,
  gr_vector_void_star       & output_items )
{
  const gr_complex *in = static_cast< const gr_complex* >( input_items[0] );
  gr_complex *out = static_cast< gr_complex* >( output_items[0] );

  const int bufsize = (int) d_buffer.size();



  // convert input to itpp::cvec (double)
  itpp::cvec input( noutput_items );
  for( int i = 0; i < noutput_items; ++i )
  {
    input[i] = in[i];
  }

  itpp::cvec output;

  if( d_calc_impulse_response )
  {
    const int imp_size = d_max_delay + 1;
    assert( output_items.size() == 2 );
    assert( output_signature()->sizeof_stream_item( 1 ) ==
            sizeof( gr_complex ) * imp_size );
    gr_complex * imp = static_cast< gr_complex * >( output_items[1] );

    itpp::Array<itpp::cvec> channel_coeff, impulse_response;
    output = d_channel->filter( input, channel_coeff );
    d_channel->calc_impulse_response( channel_coeff, impulse_response );

    for( int ix = 0; ix < noutput_items; ++ix )
    {
      for( int iy = 0; iy < imp_size; ++iy )
      {
	*imp++ = impulse_response(ix)(iy);
      }
    }

  } // if( d_calc_impulse_response )
  else
  {
    output = d_channel->filter( input );
    assert( output.size() == noutput_items + bufsize );

  } // if( d_calc_impulse_response )
  // store result in output buffer and internal buffer
  int i = 0;

  const int n = std::min( noutput_items, bufsize );
  for( ; i < n; ++i )
  {
    out[i] = output[i] + d_buffer[i];
  }

  for( ; i < noutput_items; ++i )
  {
    out[i] = output[i];
  }

  if( bufsize > 0 )
  {
    const int leftover = bufsize - n;
    int j = 0;
    for( ; j < leftover; ++j, ++i )
    {
      d_buffer[j] = d_buffer[ n + j ] + output[i];
    }
    for( ; j < bufsize; ++j, ++i )
    {
      d_buffer[j] = output[i];
    }
  } // if( bufsize > 0 )

  return noutput_items;
}


cvec
ofdm_itpp_tdl_channel ::
  calc_frequency_response( int fft_size )
{

  cvec  frequency_response;
  itpp::Array< itpp::cvec > channel_coeff;
  const int no_samples = 1;

  d_channel->generate( no_samples, channel_coeff );

  if( d_channel->get_norm_doppler() > 0.0 )
  {
    d_channel->shift_time_offset( - no_samples );
  }

  itpp::Array< itpp::cvec > freq_resp;
  d_channel->calc_frequency_response( channel_coeff, freq_resp, fft_size );

  assert( freq_resp(0).size() == fft_size );

  frequency_response.resize( freq_resp(0).size(), 0.0 );
  for( int i = 0; i < freq_resp(0).size(); ++i )
  {
    frequency_response[i] = freq_resp(0)[i];
  }
  return frequency_response;
}

/*cvec
ofdm_itpp_tdl_channel ::
  set_vector(int vlen)
{
	cvec vout;
	vout.resize(vlen,0);
	return vout;
}*/


void
ofdm_itpp_tdl_channel ::
  calc_impulse_response( cvec & impulse_response  )
{
  itpp::Array< itpp::cvec > channel_coeff;
  const int no_samples = 1;

  d_channel->generate( no_samples, channel_coeff );

  if( d_channel->get_norm_doppler() > 0.0 )
  {
    d_channel->shift_time_offset( - no_samples );
  }


  itpp::Array< itpp::cvec > imp_resp;
  d_channel->calc_impulse_response( channel_coeff, imp_resp );

  impulse_response.resize( imp_resp(0).size(), 0.0 );
  for( int i = 0; i < imp_resp(0).size(); ++i )
  {
    impulse_response[i] = imp_resp(0)[i];
  }
}




template < typename T1, typename T2 >
struct enum_pair
{
  T1 first;
  T2 second;
};

static enum_pair< CHANNEL_PROFILE, itpp::CHANNEL_PROFILE >
  CHANNEL_PROFILE_TRANSLATE[] =
{
  { ITU_Vehicular_A, itpp::ITU_Vehicular_A },
  { ITU_Vehicular_B, itpp::ITU_Vehicular_B },
  { ITU_Pedestrian_A, itpp::ITU_Pedestrian_A },
  { ITU_Pedestrian_B, itpp::ITU_Pedestrian_B },
  { COST207_RA, itpp::COST207_RA },
  { COST207_RA6, itpp::COST207_RA6 },
  { COST207_TU, itpp::COST207_TU },
  { COST207_TU6alt, itpp::COST207_TU6alt },
  { COST207_TU12, itpp::COST207_TU12 },
  { COST207_TU12alt, itpp::COST207_TU12alt },
  { COST207_BU, itpp::COST207_BU },
  { COST207_BU6alt, itpp::COST207_BU6alt },
  { COST207_BU12, itpp::COST207_BU12 },
  { COST207_BU12alt, itpp::COST207_BU12alt },
  { COST207_HT, itpp::COST207_HT },
  { COST207_HT6alt, itpp::COST207_HT6alt },
  { COST207_HT12, itpp::COST207_HT12 },
  { COST207_HT12alt, itpp::COST207_HT12alt },
  { COST259_TUx, itpp::COST259_TUx },
  { COST259_RAx, itpp::COST259_RAx },
  { COST259_HTx, itpp::COST259_HTx }
};

static enum_pair< FADING_TYPE, itpp::FADING_TYPE >
  FADING_TYPE_TRANSLATE[] =
{
  { Independent, itpp::Independent },
  { Static, itpp::Static },
  { Correlated, itpp::Correlated }
};

static enum_pair< CORRELATED_METHOD, itpp::CORRELATED_METHOD >
  CORRELATED_METHOD_TRANSLATE[] =
{
  { Rice_MEDS, itpp::Rice_MEDS },
  { IFFT, itpp::IFFT },
  { FIR, itpp::FIR }
};

static enum_pair< DOPPLER_SPECTRUM, itpp::DOPPLER_SPECTRUM >
  DOPPLER_SPECTRUM_TRANSLATE[] =
{
  { Jakes, itpp::Jakes },
  { GaussI, itpp::GaussI },
  { GaussII, itpp::GaussII }
};

template < typename T1, typename T2 >
static T2
enum_first_to_second( T1 f, enum_pair< T1, T2 > tr_list[], int list_size )
{
  for( int i = 0; i < list_size; ++i )
  {
    if( tr_list[i].first == f )
    {
      return tr_list[i].second;
    }
  }
  assert(0 && "failed to translate");
}

template < typename T1, typename T2 >
static T1
enum_second_to_first( T2 s, enum_pair< T1, T2 > tr_list[], int list_size )
{
  for( int i = 0; i < list_size; ++i )
  {
    if( tr_list[i].second == s )
    {
      return tr_list[i].first;
    }
  }
  assert(0 && "failed to translate");
}

#define ENUM_FIRST_TO_SECOND( x )     \
  static itpp::x  \
  enum_first_to_second( x _t ) \
  {  \
    return enum_first_to_second( _t, x ## _TRANSLATE,  \
      sizeof( x ## _TRANSLATE ) /  \
      sizeof( enum_pair< x, itpp::x > ) ); \
  }

#define ENUM_SECOND_TO_FIRST( x )     \
  static x  \
  enum_second_to_first( itpp::x _t ) \
  {  \
    return enum_second_to_first( _t, x ## _TRANSLATE,  \
      sizeof( x ## _TRANSLATE ) /  \
      sizeof( enum_pair< x, itpp::x > ) ); \
  }

ENUM_FIRST_TO_SECOND( CHANNEL_PROFILE )
ENUM_FIRST_TO_SECOND( DOPPLER_SPECTRUM )
ENUM_FIRST_TO_SECOND( FADING_TYPE )
ENUM_FIRST_TO_SECOND( CORRELATED_METHOD )
ENUM_SECOND_TO_FIRST( CHANNEL_PROFILE )
ENUM_SECOND_TO_FIRST( DOPPLER_SPECTRUM )
ENUM_SECOND_TO_FIRST( FADING_TYPE )
ENUM_SECOND_TO_FIRST( CORRELATED_METHOD )

void
ofdm_itpp_tdl_channel::set_channel_profile( const dvec & avg_power_db,
  const ivec & delay_prof )
{
  d_channel->set_channel_profile(
    conv_stdvector_to_itppvec( avg_power_db ),
    conv_stdvector_to_itppvec( delay_prof ) );
}
/*
void
ofdm_itpp_tdl_channel::set_channel_profile_uniform( int no_taps )
{
  d_channel->set_channel_profile_uniform( no_taps );
}
*/
void
ofdm_itpp_tdl_channel::set_channel_profile_exponential( int no_taps )
{
  d_channel->set_channel_profile_exponential( no_taps );
}

void
ofdm_itpp_tdl_channel::set_channel_profile( const CHANNEL_PROFILE profile,
  double sampling_time )
{
  itpp::Channel_Specification spec;

  spec.set_channel_profile( enum_first_to_second( profile ) );

  d_channel->set_channel_profile( spec, sampling_time );
}

void
ofdm_itpp_tdl_channel::set_correlated_method( CORRELATED_METHOD method )
{
  itpp::CORRELATED_METHOD m = enum_first_to_second( method );

  d_channel->set_correlated_method( m );
}

void
ofdm_itpp_tdl_channel::set_fading_type( FADING_TYPE fading_type )
{
  itpp::FADING_TYPE f = enum_first_to_second( fading_type );

  d_channel->set_fading_type( f );
}

void
ofdm_itpp_tdl_channel::set_norm_doppler( double norm_doppler )
{
  d_channel->set_norm_doppler( norm_doppler );
}

void
ofdm_itpp_tdl_channel::set_LOS( const dvec& relative_power,
  const dvec& relative_doppler /* = dvec() */ )
{
  d_channel->set_LOS( conv_stdvector_to_itppvec( relative_power ),
    conv_stdvector_to_itppvec( relative_doppler ) );
}

void
ofdm_itpp_tdl_channel::set_LOS_power( const dvec& relative_power )
{
  d_channel->set_LOS_power( conv_stdvector_to_itppvec( relative_power ) );
}

void
ofdm_itpp_tdl_channel::set_LOS_doppler( const dvec& relative_doppler )
{
  d_channel->set_LOS_doppler( conv_stdvector_to_itppvec( relative_doppler ) );
}

void
ofdm_itpp_tdl_channel::set_doppler_spectrum(
  const std::vector< DOPPLER_SPECTRUM > tap_spectrum )
{
  itpp::DOPPLER_SPECTRUM *ds =
    new itpp::DOPPLER_SPECTRUM[ tap_spectrum.size() ];

  for( std::vector< DOPPLER_SPECTRUM >::size_type i = 0;
       i < tap_spectrum.size(); ++i )
  {

    ds[i] = enum_first_to_second( tap_spectrum[i] );
  }

  d_channel->set_doppler_spectrum( ds );

  delete[] ds;
}

void
ofdm_itpp_tdl_channel::set_doppler_spectrum( int tap_number,
  DOPPLER_SPECTRUM tap_spectrum )
{
  d_channel->set_doppler_spectrum( tap_number,
    enum_first_to_second( tap_spectrum ) );
}

void
ofdm_itpp_tdl_channel::set_no_frequencies( int no_freq )
{
  d_channel->set_no_frequencies( no_freq );
}

void
ofdm_itpp_tdl_channel::set_time_offset( int offset )
{
  d_channel->set_time_offset( offset );
}

void
ofdm_itpp_tdl_channel::shift_time_offset( int no_samples )
{
  d_channel->shift_time_offset( no_samples );
}

void
ofdm_itpp_tdl_channel::set_filter_length( int filter_length )
{
  d_channel->set_filter_length( filter_length );
}

int
ofdm_itpp_tdl_channel::taps() const
{
  return d_channel->taps();
}

void
ofdm_itpp_tdl_channel::get_channel_profile( dvec &avg_power_dB,
  ivec &delay_prof ) const
{
  itpp::vec a;
  itpp::ivec d;
  d_channel->get_channel_profile( a, d );

  avg_power_dB = conv_itppvec_to_stdvector( a );
  delay_prof = conv_itppvec_to_stdvector( d );
}

dvec
ofdm_itpp_tdl_channel::get_avg_power_dB() const
{
  itpp::vec out = d_channel->get_avg_power_dB();
  return conv_itppvec_to_stdvector( out );
}

ivec
ofdm_itpp_tdl_channel::get_delay_prof() const
{
  itpp::ivec out = d_channel->get_delay_prof();
  return conv_itppvec_to_stdvector( out );
}

CORRELATED_METHOD
ofdm_itpp_tdl_channel::get_correlated_method() const
{
  itpp::CORRELATED_METHOD m = d_channel->get_correlated_method();
  return enum_second_to_first( m );
}

FADING_TYPE
ofdm_itpp_tdl_channel::get_fading_type() const
{
  itpp::FADING_TYPE f = d_channel->get_fading_type();
  return enum_second_to_first( f );
}

double
ofdm_itpp_tdl_channel::get_norm_doppler() const
{
  return d_channel->get_norm_doppler();
}

dvec
ofdm_itpp_tdl_channel::get_LOS_power() const
{
  itpp::vec out = d_channel->get_LOS_power();
  return conv_itppvec_to_stdvector( out );
}

dvec
ofdm_itpp_tdl_channel::get_LOS_doppler() const
{
  itpp::vec out = d_channel->get_LOS_doppler();
  return conv_itppvec_to_stdvector( out );
}

double
ofdm_itpp_tdl_channel::get_LOS_power( int tap_number ) const
{
  return d_channel->get_LOS_doppler( tap_number );
}

double
ofdm_itpp_tdl_channel::get_LOS_doppler( int tap_number ) const
{
  return d_channel->get_LOS_doppler( tap_number );
}

int
ofdm_itpp_tdl_channel::get_no_frequencies() const
{
  return d_channel->get_no_frequencies();
}

double
ofdm_itpp_tdl_channel::get_time_offset() const
{
  return d_channel->get_time_offset();
}

double
ofdm_itpp_tdl_channel::calc_mean_excess_delay() const
{
  return d_channel->calc_mean_excess_delay();
}

double
ofdm_itpp_tdl_channel::calc_rms_delay_spread() const
{
  return d_channel->calc_rms_delay_spread();
}

double
ofdm_itpp_tdl_channel::get_sampling_time() const
{
  return d_channel->get_sampling_time();
}



ofdm_itpp_tdl_channel_sptr
ofdm_make_itpp_tdl_channel( const dvec & avg_power_db,
  const ivec & delay_prof, bool calc_impulse_response )
{
  return ofdm_itpp_tdl_channel::create( avg_power_db, delay_prof,
    calc_impulse_response );
}


ofdm_itpp_tdl_channel_sptr
ofdm_itpp_tdl_channel::create( const dvec & avg_power_db,
  const ivec & delay_prof, bool calc_impulse_response )
{
  try
  {
    ofdm_itpp_tdl_channel_sptr tmp(
      new ofdm_itpp_tdl_channel( avg_power_db, delay_prof, calc_impulse_response ) );

    return tmp;
  }
  catch ( ... )
  {
    std::cerr << "[ERROR] Caught exception at creation of "
              << "ofdm_itpp_tdl_channel" << std::endl;
    throw;
  } // catch ( ... )
}



