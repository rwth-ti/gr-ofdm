#ifdef HAVE_CONFIG_H
#include "config.h"
#endif

#include <gr_sync_block.h>
#include <gr_io_signature.h>
#include <ofdm_complex_white_noise.h>

#include <cmath>

#include <boost/random.hpp>
#include <boost/random/normal_distribution.hpp>
#include <boost/random/variate_generator.hpp>

#include <iostream>

#include <stdexcept>

#include <ofdmi_shared_generator.h>

typedef boost::lagged_fibonacci44497 base_generator_type;
typedef boost::shared_ptr<base_generator_type> base_generator_sptr;
  
typedef boost::normal_distribution<float> distribution_type;
typedef boost::variate_generator<base_generator_type&, distribution_type> rng_type;
typedef boost::shared_ptr<rng_type> rng_sptr;

#define DEBUG 0
#if DEBUG
#include <iostream>
#endif


class ofdm_complex_white_noise::rng_detail
{

  distribution_type dist_r, dist_i;
  rng_sptr rng_r,rng_i;
  
  base_generator_sptr generator;
  
public:
  
  rng_detail( gr_complex mean, float sigma ) 
    : dist_r( mean.real(), sigma / std::sqrt(2.0) ),
      dist_i( mean.imag(), sigma / std::sqrt(2.0) )
  {
    base_generator_sptr u( new base_generator_type( ) );
    generator = u;
    generator->seed( *get_shared_generator() );
    
    rng_sptr t( new rng_type( *generator, dist_r ) );
    rng_r = t;
    
    rng_sptr v( new rng_type( *generator, dist_i ) );
    rng_i = v;
    
    volatile float f;
    for( int i = 0; i < 1000000; ++i ){
      f = (*rng_r)();
      f = (*rng_i)();
    }
  }
  
  gr_complex
  get_complex_sample(void)
  {
    return gr_complex( (*rng_r)(), (*rng_i)() );
  }
};



ofdm_complex_white_noise_sptr ofdm_make_complex_white_noise(gr_complex mean, 
    float sigma)
{
  return ofdm_complex_white_noise::create( mean, sigma );
}

ofdm_complex_white_noise_sptr
ofdm_complex_white_noise::create( gr_complex mean, float sigma )
{
  try {
    
    ofdm_complex_white_noise_sptr tmp( new ofdm_complex_white_noise( 
        mean, sigma ) );
    
    return tmp;
    
  } catch ( ... ) {
    
    if( DEBUG ) {
      std::cerr << "[ERROR] Caught exception at creation of"
                << "ofdm_complex_white_noise" << std::endl;
    }
    
    throw;
    
  }
}

ofdm_complex_white_noise::ofdm_complex_white_noise(gr_complex mean, float sigma)
  : gr_sync_block(
      "complex_white_noise",
      gr_make_io_signature (0, 0, 0),
      gr_make_io_signature (1, 1, sizeof(gr_complex))),
  
  d_rng_detail( new rng_detail( mean, sigma ) ),
  d_mean( mean ), 
  d_sigma( sigma )
{
}

int ofdm_complex_white_noise::work(
    int noutput_items,
    gr_vector_const_void_star &input_items,
    gr_vector_void_star &output_items)
{
  gr_complex * out = static_cast<gr_complex*>(output_items[0]);
  
  for( int i = 0; i < noutput_items; ++i ){
    out[i] = d_rng_detail->get_complex_sample();
  }
  
  return noutput_items;
}
